from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)  # Already stored in User
    # Removed `username` and `password` fields

    def __str__(self):
        return self.user.username  # Use User's username instead
