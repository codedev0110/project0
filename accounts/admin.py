from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'skill_level', 'reputation_score', 'github_username', 'date_joined')
    list_filter = ('skill_level', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'github_username')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Platform Info', {
            'fields': ('github_username', 'github_id', 'bio', 'skill_level', 
                      'preferred_languages', 'reputation_score', 'avatar_url')
        }),
    )
