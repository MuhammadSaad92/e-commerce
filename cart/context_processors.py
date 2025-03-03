from .models import Cart

def cart_count(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        return {"cart_count": sum(item.quantity for item in cart_items)}
    return {"cart_count": 0}  # If user is not logged in, count is 0
