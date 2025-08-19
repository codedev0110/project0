from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Extended User model with additional fields for the platform"""
    github_username = models.CharField(max_length=100, blank=True, null=True)
    github_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    bio = models.TextField(blank=True)
    skill_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    preferred_languages = models.JSONField(default=list, blank=True)
    reputation_score = models.IntegerField(default=0)
    avatar_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
