from django.urls import path
from .views import add_to_cart, view_cart, remove_from_cart, update_cart

urlpatterns = [
    path("", view_cart, name="cart"),  
    path("add/<int:product_id>/", add_to_cart, name="add_to_cart"),  
    path("remove/<int:cart_id>/", remove_from_cart, name="remove_from_cart"),
    path("cart/update/<int:cart_id>/", update_cart, name="update_cart"),

]