from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import stripe
from django.conf import settings
from .models import Order, OrderItem
from cart.models import Cart
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

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
    return redirect('order_payment', order_id=order.id) 


@login_required
def order_payment(request, order_id):
    """Displays the payment page."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'payment.html', {'order': order, 'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY})


@csrf_exempt
@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        try:
            # Parse the JSON request body
            data = json.loads(request.body)
            payment_method_id = data.get('payment_method_id')

            # Construct the return URL for the order success page
            return_url = request.build_absolute_uri(redirect('order_success', order_id=order.id).url)

            # Create a PaymentIntent with redirect-based payment methods enabled
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_price * 100), 
                currency="usd",
                payment_method=payment_method_id,
                confirm=True,  # Keep this for immediate confirmation
                return_url=return_url,  
                automatic_payment_methods={"enabled": True},  
            )

            # Handle different payment intent statuses
            if intent.status == "succeeded":
                order.status = "paid"
                order.save()
                return JsonResponse({"success": True, "redirect_url": return_url})
            elif intent.status == "requires_action":
                return JsonResponse({
                    "success": False,
                    "requires_action": True,
                    "next_action": intent.next_action,
                    "payment_intent_client_secret": intent.client_secret,  # Required for client-side handling
                    "redirect_url": return_url
                })
            else:
                return JsonResponse({"success": False, "status": intent.status})

        except stripe.error.CardError as e:
            return JsonResponse({"success": False, "error": str(e)})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})



@login_required
def order_success(request, order_id):
    """Displays order success page after payment."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == "paid":
        # Payment was successful
        messages.success(request, "Payment successful! Thank you for your purchase.")
        return redirect('home')  # Redirect to the home page
    else:
        # Payment was not successful
        messages.error(request, "Payment failed. Please try again.")
        return redirect('order_payment', order_id=order.id)