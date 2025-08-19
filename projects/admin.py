from django.contrib import admin
from .models import Project, ProjectFile, ProjectLike

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'primary_language', 'difficulty_level', 'stars_count', 'views_count', 'created_at')
    list_filter = ('primary_language', 'difficulty_level', 'created_at')
    search_fields = ('name', 'description', 'owner__username')
    readonly_fields = ('github_repo_id', 'stars_count', 'forks_count', 'views_count', 'likes_count')

@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('project', 'file_path', 'file_type', 'size', 'created_at')
    list_filter = ('file_type', 'created_at')
    search_fields = ('project__name', 'file_path')

@admin.register(ProjectLike)
class ProjectLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'project__name')
