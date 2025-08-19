from django.contrib import admin
from .models import Project, ProjectFile


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'language', 'difficulty', 'stars')
    search_fields = ('name', 'repo_full_name', 'owner__username')


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'path', 'is_dir', 'size')
    search_fields = ('path',)

# Register your models here.
