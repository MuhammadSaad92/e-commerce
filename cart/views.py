from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Cart

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

    if not created:
        cart_item.quantity += 1  
        cart_item.save()

    messages.success(request, f"{product.name} added to cart.")
    return redirect("cart")  

from django.contrib import messages
from django.shortcuts import render
from .models import Cart

@login_required
@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    # Calculate total price and cart count
    total_price = sum(item.total_price() for item in cart_items)
    cart_count = sum(item.quantity for item in cart_items)

    # Add a message if the cart is empty
    if not cart_items:
        messages.info(request, "Your cart is empty. Continue shopping!")

    return render(
        request, 
        "cart.html", 
        {"cart_items": cart_items, "total_price": total_price, "cart_count": cart_count}
    )

@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("cart")

@login_required
def update_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add":
            cart_item.quantity += 1
        elif action == "minus" and cart_item.quantity > 1:
            cart_item.quantity -= 1

        cart_item.save()
    
    return redirect("cart")  # Reload the cart page
