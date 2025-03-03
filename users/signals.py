from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Automatically creates a Profile when a new User is created."""
    if created:
        Profile.objects.create(user=instance, email=instance.email)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Saves the Profile when the User is updated."""
    instance.profile.email = instance.email  
    instance.profile.save()
