from django.shortcuts import render, redirect, get_object_or_404
from .models import Product

def products(request):
    products = Product.objects.all()  # Fetch all products
    return render(request, 'products.html', {'products': products})

def productDetail(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Fetch product by ID
    return render(request, 'productdetail.html', {'product': product})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Get cart from session (if not exists, create an empty cart)
    cart = request.session.get('cart', {})

    # If product already in cart, increase quantity
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        # Add new product to cart
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': 1,
            'image': product.image.url if product.image else ''
        }

    # Save cart back to session
    request.session['cart'] = cart
    request.session.modified = True  # Ensure session is saved

    return redirect('productDetail', product_id=product.id)

def view_cart(request):
    cart = request.session.get('cart', {})  # Get cart from session
    return render(request, 'cart.html', {'cart': cart})


def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Logic for instant purchase (e.g., redirect to checkout page)
    return redirect('productDetail', product_id=product.id)