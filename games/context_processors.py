def cart_counter(request):
    cart = request.session.get("cart", {})
    return {
        'cart_counter': len(cart)
    }