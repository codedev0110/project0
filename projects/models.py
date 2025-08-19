from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    repo_full_name = models.CharField(max_length=300)  # e.g., owner/name
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=100, blank=True)
    difficulty = models.CharField(max_length=50, choices=[
        ('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')
    ], default='beginner')
    tags = models.CharField(max_length=300, blank=True)
    stars = models.IntegerField(default=0)
    forks = models.IntegerField(default=0)
    html_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    path = models.CharField(max_length=500)
    sha = models.CharField(max_length=200, blank=True)
    size = models.IntegerField(default=0)
    is_dir = models.BooleanField(default=False)

    class Meta:
        unique_together = ('project', 'path')

    def __str__(self):
        return f"{self.project.name}: {self.path}"

# Create your models here.
