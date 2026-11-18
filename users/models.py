from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, default='')
    avatar_color = models.CharField(max_length=7, default='#6366f1')  # hex color for avatar circle

    def __str__(self):
        return f"{self.user.username}'s profile"