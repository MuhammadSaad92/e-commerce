from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.db import IntegrityError

def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        # Ensure all fields are filled
        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
            return redirect("register")

        # Check if passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        # Check if username or email is already taken
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("register")

        try:
            # Create User (Profile will be created automatically via signals)
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()

            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login")  # Redirect to login page

        except IntegrityError:
            messages.error(request, "An error occurred. Please try again with a different email.")
            return redirect("register")

    return render(request, "register.html")


def login_user(request):
    if request.user.is_authenticated:
        return redirect("home")  

    if request.method == "POST":
        username = request.POST.get("username", "").strip()  
        password = request.POST.get("password", "").strip()  

        if not username or not password:
            messages.error(request, "Both username and password are required.")
            return redirect("login")

        # Authenticate using username and password
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "login.html")


@login_required(login_url="login")  
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


@login_required(login_url="login")  
def profile(request):
    user = request.user  

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Update fields if provided
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.set_password(password)  # Change password securely

        user.save()
        messages.success(request, "Profile updated successfully!")

        return redirect("profile")  

    return render(request, "profile.html", {"user": user})
