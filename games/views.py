
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import *
from .forms import ReviewForm, ProfileEditForm
from django.http import JsonResponse

def game_list(request):
    query = request.GET.get('q', '')
    genre = request.GET.get('genre', '')

    games = Game.objects.all()
    if query:
        games = games.filter(title__icontains=query)
    if genre:
        games = games.filter(genre=genre)

    genres = Game.objects.values_list('genre', flat=True).distinct()
    # [(SHOOTER), (RPG), (RPG), (RP)] => [SHOOTER, RPG, RP]

    paginator = Paginator(games, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'genres': genres,
        'query': query,
        'selected_genre': genre,
    }
    if request.headers.get('x-requested-with') == "XMLHttpRequest":
        return render(request, 'games/game_list_content.html', context)
    
    return render(request, 'games/game_list.html', context)

def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    reviews = Review.objects.filter(game=game)

    form = ReviewForm(request.POST or None)
    if form.is_valid():
        review = form.save(commit=False)
        review.game = game
        review.save()

    return render(request, 'games/game_detail.html', 
                    {'game': game, 
                     'reviews': reviews,
                     'form': form
                     })


def add_to_favorites(request, game_id):
    favorites = request.session.get('favorites', [])
    if game_id not in favorites:
        favorites.append(game_id)
    
    request.session['favorites'] = favorites
    
    return redirect('game_list')

def add_to_favorites_ajax(request, game_id):
    favorites = request.session.get('favorites', [])
    if game_id not in favorites:
        favorites.append(game_id)
    
    request.session['favorites'] = favorites
    
    return JsonResponse({
        'status': 'ok',
        'favorites_count': len(favorites)
    })

def remove_from_favorites(request, game_id):
    favorites = request.session.get('favorites', [])
    if game_id in favorites:
        favorites.remove(game_id)
    request.session['favorites'] = favorites
    return redirect('favorites')

def favorites(request):
    favorites = request.session.get('favorites', [])
    games = Game.objects.filter(id__in=favorites)
    return render(request, 'games/favorites.html', {'games': games})
    

def add_to_cart(request, game_id):
    cart = request.session.get("cart", {})
    game_id = str(game_id)
    if game_id not in cart:
        cart[game_id] = 1

    request.session['cart'] = cart
    return redirect('cart')

def cart_view(request):
    cart = request.session.get("cart", {})
    game_ids = cart.keys()

    games = Game.objects.filter(id__in=game_ids)

    total = 0
    for game in games:
        total += game.sell_price
    return render(request, 'games/cart.html', {
        'games': games,
        'total': total
    })


def remove_from_cart(request, game_id):
    cart = request.session.get("cart", {})
    game_id = str(game_id)
    if game_id in cart:
        del cart[game_id]

    request.session['cart'] = cart
    return redirect('cart')

import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY

def stripe_checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("cart")
    
    games = Game.objects.filter(id__in=cart.keys())

    items = []
    for game in games:
        items.append({
            'price_data': {
                'currency': 'uah',
                'product_data': {
                    'name': game.title
                },
                'unit_amount': int(game.sell_price * 100)
            },
            'quantity': 1,
        })
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=items,
        mode="payment",
        success_url=request.build_absolute_uri('/payment/success/'),
        cancel_url=request.build_absolute_uri('/cart/'),
    )
    return redirect(session.url, code=303)

def payment_success(request):
    cart = request.session.get("cart", {})
    if cart:
        game_ids = cart.keys()
        games = Game.objects.filter(id__in=game_ids)
        
        for game in games:
            PurchasedGame.objects.get_or_create(
                user=request.user,
                game=game
            )
    
    request.session["cart"] = {}
    return render(request, "games/payment_success.html")


from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.utils import timezone

def register_view(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('profile')
    return render(request, "accounts/register.html", {'form': form})


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user)

        profile = user.profile
        profile.status = 'online'
        profile.last_seen = timezone.now()
        profile.save()

        return redirect('profile')
    return render(request, "accounts/login.html", {'form': form})


def logout_view(request):
    if request.user.is_authenticated:

        profile = request.user.profile
        profile.status = 'offline'
        profile.last_seen = timezone.now()
        profile.save()

    logout(request)
    return redirect('game_list')

from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={'nickname': request.user.username}
    )

    games = PurchasedGame.objects.filter(user=request.user)
    friends = Friend.objects.filter(user=request.user).select_related(
       'friend__profile'
    )
    
    incoming_requests = FriendRequest.objects.filter(
        receiver=request.user,
        status="pending"
    ).select_related('sender')

    outcoming_requests = FriendRequest.objects.filter(
        sender=request.user,
        status="pending"
    ).select_related('receiver')
    
    return render(request, "accounts/profile.html", {
        'profile': profile,
        'games': games,
        'friends': friends,
        'incoming_requests': incoming_requests,
        'outcoming_requests': outcoming_requests,
    })



@login_required
def send_friend_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    if receiver == request.user:
        return redirect('profile')

    if Friend.objects.filter(user=request.user, friend=receiver).exists():
        return redirect('profile')

    if FriendRequest.objects.filter(
        sender=request.user,
        receiver=receiver,
        status='pending'
    ).exists():
        return redirect('profile')

    reverse_request = FriendRequest.objects.filter(
        sender=receiver,
        receiver=request.user,
        status='pending'
    ).first()

    if reverse_request:
        # reverse_request.status = 'accepted'
        # reverse_request.save()
        reverse_request.delete()


        Friend.objects.create(user=request.user, friend=receiver)
        Friend.objects.create(user=receiver, friend=request.user)

        return redirect('profile')

    FriendRequest.objects.create(
        sender=request.user,
        receiver=receiver
    )
    return redirect('profile')


@login_required
def accept_friend_request(request, request_id):
    fr = get_object_or_404(
        FriendRequest,
        id=request_id,
        receiver=request.user
    )

    fr.delete()

    Friend.objects.create(user=fr.sender, friend=fr.receiver)
    Friend.objects.create(user=fr.receiver, friend=fr.sender)

    return redirect('profile')


@login_required
def reject_friend_request(request, request_id):
    fr = get_object_or_404(
        FriendRequest,
        id=request_id,
        receiver=request.user
    )

    fr.delete()

    return redirect('profile')

@login_required
def cancel_friend_request(request, request_id):
    fr = get_object_or_404(
        FriendRequest,
        id=request_id,
        sender=request.user
    )

    fr.delete()

    return redirect('profile')


@login_required
def remove_friend(request, user_id):
    fr = get_object_or_404(
        User,
        id=user_id
    )

    Friend.objects.filter(user=request.user, friend=fr).delete()
    Friend.objects.filter(user=fr, friend=request.user).delete()

    return redirect('profile')


@login_required
def user_search_view(request):
    query = request.GET.get('q', '')
    users = User.objects.none()

    if query:
        users = User.objects.filter(
            username__icontains=query
        ).exclude(id=request.user.id).select_related("profile")
    friends_ids = Friend.objects.filter(user=request.user.id).values_list('friend_id', flat=True)
    
    return render(request, "accounts/user_search.html", {
        'users': users,
        'query': query,
        'friends_ids': list(friends_ids),
    })

@login_required
def chat_view(request, user_id):
   friend = get_object_or_404(User, id=user_id)

   if not Friend.objects.filter(user=request.user, friend=friend).exists():
       return redirect('profile')


   messages = Message.objects.filter(
       sender__in=[request.user, friend],
       receiver__in=[request.user, friend]
   ).order_by('timestamp')


   if request.method == 'POST':
       text = request.POST.get('text')
       if text:
           Message.objects.create(
               sender=request.user,
               receiver=friend,
               text=text
           )
       return redirect('chat', user_id=friend.id)


   return render(request, 'accounts/chat.html', {
       'friend': friend,
       'messages': messages
   })

    

from django.http import JsonResponse
from django.utils.dateparse import parse_datetime

@login_required
def fetch_messages(request, user_id):
    friend = get_object_or_404(User, id=user_id)

    if not Friend.objects.filter(user=request.user, friend=friend).exists():
        return JsonResponse({'messages': []})
    
    last_time = request.GET.get("last_time")

    messages = Message.objects.filter(
        sender__in=[request.user, friend],
        receiver__in=[request.user, friend],
    )

    if last_time:
        dt = parse_datetime(last_time)
        if dt is not None:
            messages = messages.filter(timestamp__gt=dt)
    
    messages.order_by("timestamp")

    data = []
    for msg in messages:
        data.append({
            'sender': msg.sender.username,
            'text': msg.text,
            'timestamp': msg.timestamp.isoformat()
        })
    return JsonResponse({'messages': data})


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile)
        
    return render(request, 'accounts/edit_profile.html', {
        'form': form
    })


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import *

@api_view(["GET"])
def api_game_list(request):
    games = Game.objects.all()
    serializer = GameSerializer(games, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def api_game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    serializer = GameSerializer(game)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_profile(request):
    profile = request.user.profile
    serializer = ProfileSerializer(profile)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_messages(request, user_id):
    friend = get_object_or_404(User, id=user_id)

    messages = Message.objects.filter(
       sender__in=[request.user, friend],
       receiver__in=[request.user, friend]
   ).order_by('timestamp')

    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)
