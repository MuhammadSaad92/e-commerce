import json
import re
import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Order, OrderItem, Product
from cart.models import Cart

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def order_create(request):
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items:
        return redirect('cart_view')  # Redirect if cart is empty

    # Create a new order for the user
    order = Order(user=request.user)
    order.save()  # Save to generate a primary key

    # Add items from cart to the order
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

    # Calculate and update the total price for the order
    order.total_price = sum(item.quantity * item.price for item in order_items)
    order.save()

    # Clear the cart
    cart_items.delete()

    return redirect('order_detail', order_id=order.id)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == "POST":
        # If user confirms the order, redirect to payment
        return redirect('order_payment', order_id=order.id)
    
    return render(request, 'order_detail.html', {'order': order})


@login_required
def confirm_order(request, order_id):
    """Update order status to processing and redirect to payment page."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.status = "processing"
    order.save(update_fields=['status'])
    return redirect('order_payment', order_id=order.id)


@login_required
def order_payment(request, order_id):
    """Display the payment page."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'payment.html', {
        'order': order,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY
    })


@csrf_exempt
@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            payment_method_id = data.get('payment_method_id')
            user_data = data.get('user_data')

            # Validate that user_data was provided
            if not user_data:
                return JsonResponse({"success": False, "error": "Missing user details."}, status=400)

            # Validate name: letters and spaces allowed
            if not re.match(r'^[A-Za-z\s]+$', user_data.get("name", "")):
                return JsonResponse({"success": False, "error": "Name must contain only letters and spaces."}, status=400)

            # Validate phone: only digits allowed (modify regex if you need country codes, etc.)
            if not re.match(r'^\d+$', user_data.get("phone", "")):
                return JsonResponse({"success": False, "error": "Phone must be numeric."}, status=400)

            # Save billing details to the order
            order.full_name = user_data.get('name')
            order.email = user_data.get('email')
            order.phone = user_data.get('phone')
            order.address = user_data.get('address')
            order.city = user_data.get('city')
            order.state = user_data.get('state')
            order.zip_code = user_data.get('zip')
            order.save()

            # Process payment with Stripe (convert total to cents)
            intent = stripe.PaymentIntent.create(
            amount=int(order.total_price * 100),
            currency="usd",
            payment_method=payment_method_id,
            confirm=True,
            return_url=request.build_absolute_uri('/')  # Redirect back to home after payment
        )

            if intent.status == "succeeded":
                order.status = "paid"
                order.save()
                return JsonResponse({"success": True, "redirect_url": "/"})  # Redirect to home
            else:
                return JsonResponse({
                    "success": False, 
                    "error": "Payment failed!", 
                    "status": intent.status
                }, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON request."}, status=400)
        except stripe.error.CardError as e:
            return JsonResponse({"success": False, "error": str(e.user_message)}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)


@login_required
def buy_now(request, product_id):
    # Retrieve the product by id
    product = get_object_or_404(Product, id=product_id)

    # Create a new order for the "Buy Now" action
    order = Order(user=request.user)
    order.save()

    # Add the product to the order with default quantity of 1
    order_item = OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        price=product.price
    )

    # Update the order total price
    order.total_price = order_item.price * order_item.quantity
    order.save()

    return redirect('order_detail', order_id=order.id)


@login_required
def order_success(request, order_id):
    """Display order success page after payment."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == "paid":
        messages.success(request, "Payment successful! Thank you for your purchase.")
        return redirect('home')  # Redirect to the home page
    else:
        messages.error(request, "Payment failed. Please try again.")
        return redirect('order_payment', order_id=order.id)
