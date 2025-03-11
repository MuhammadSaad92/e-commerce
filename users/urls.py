from django.urls import path
from . import views
from .views import register, login_user, logout_user, profile, purchase_history

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/', profile, name='profile'),
    path('purchase_history/', views.purchase_history, name='purchase_history'),
]
