from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    github_username = models.CharField(max_length=255, blank=True)
    reputation = models.IntegerField(default=0)

    def __str__(self):
        return f"Profile({self.user.username})"

# Create your models here.
