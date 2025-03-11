from django.urls import path
from .views import order_create, order_detail, buy_now, confirm_order, order_payment, process_payment, order_success

urlpatterns = [
    path('create/', order_create, name='order_create'),
    path('<int:order_id>/', order_detail, name='order_detail'),
    path('<int:order_id>/confirm/', confirm_order, name='confirm_order'),
    path('buy-now/<int:product_id>/', buy_now, name='buy_now'),
    path('<int:order_id>/payment/', order_payment, name='order_payment'),
    path('<int:order_id>/process-payment/', process_payment, name='process_payment'),
    path('<int:order_id>/success/', order_success, name='order_success'),
]

