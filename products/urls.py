from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.products, name='products'),
    path('productdetail/<int:product_id>/', views.productDetail, name='productDetail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
]
