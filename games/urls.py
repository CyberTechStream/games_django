from django.urls import path
from .views import *
urlpatterns = [
    path('', game_list, name="game_list"),
    path('game/<int:game_id>', game_detail, name="game_detail"),
    path('favorites/add/<int:game_id>', add_to_favorites, name="add_to_favorites"),
    path('ajax/favorites/add/<int:game_id>', add_to_favorites_ajax, name="add_to_favorites_ajax"),
    path('favorites/remove/<int:game_id>', remove_from_favorites, name="remove_from_favorites"),
    path('favorites/', favorites, name="favorites"),

    path('cart/', cart_view, name="cart"),
    path('cart/add/<int:game_id>/', add_to_cart, name="add_to_cart"),
    path('cart/remove/<int:game_id>/', remove_from_cart, name="remove_from_cart"),

    path('stripe/checkout/', stripe_checkout, name="stripe_checkout"),
    path('payment/success/', payment_success, name="payment_success"),

    path('register/', register_view, name="register"),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name="logout"),
    path('profile/', profile_view, name="profile"),
    path('profile/edit/', edit_profile, name="edit_profile"),

    path("users/search/", user_search_view, name="user_search"),

    path('friend/send/<int:user_id>', send_friend_request, name="send_friend_request"),
    path('friend/accept/<int:request_id>', accept_friend_request, name="accept_friend_request"),
    path('friend/reject/<int:request_id>', reject_friend_request, name="reject_friend_request"),
    
    path('friend/cancel/<int:request_id>', cancel_friend_request, name="cancel_friend_request"),
    path('friend/remove/<int:user_id>', remove_friend, name="remove_friend"),

    path('chat/<int:user_id>', chat_view, name="chat"),
    path('chat/<int:user_id>/fetch/', fetch_messages, name='fetch_messages'),


    path('api/games/', api_game_list, name="api_game_list"),
    path('api/games/<int:game_id>', api_game_detail, name="api_game_detail"),
    path('api/profile/', api_profile, name="api_profile"),
    path('api/messages/<int:user_id>', api_messages, name="api_messages"),
]
