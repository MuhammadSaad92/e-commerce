from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem
from cart.models import Cart
from django.contrib.auth.decorators import login_required

@login_required
def order_create(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items:
        return redirect('cart_view')  # Redirect if cart is empty

    # Create the order (but don't save it yet)
    order = Order(user=request.user)

    # Save the order to get a primary key
    order.save()

    # Add items to the order
    order_items = []
    for item in cart_items:
        order_items.append(
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        )
    
    # Bulk create order items
    OrderItem.objects.bulk_create(order_items)

    # Calculate and update the total price
    order.total_price = sum(item.quantity * item.price for item in order_items)
    order.save()

    # Clear the cart after order creation
    cart_items.delete()

    return redirect('order_detail', order_id=order.id)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == "POST":
        # If user clicks "Confirm Order", redirect to payment
        return redirect('order_payment', order_id=order.id)
    
    return render(request, 'order_detail.html', {'order': order})


@login_required
def confirm_order(request, order_id):
    """Updates order status and redirects to the payment page."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.status = "processing"
    order.save(update_fields=['status'])
    return redirect('order_payment', order_id=order.id)  # Corrected URL name

@login_required
def order_payment(request, order_id):
    """Displays the payment page."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'payment.html', {'order': order})

@login_required
def process_payment(request, order_id):
    """Handles payment processing and redirects to success page."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Simulating successful payment (Replace with actual payment integration)
    order.status = "shipped"
    order.save(update_fields=['status'])

    return redirect('order_success', order_id=order.id)

@login_required
def order_success(request, order_id):
    """Displays order success page after payment."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_success.html', {'order': order})
