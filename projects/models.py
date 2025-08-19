from django.db import models
from django.conf import settings

class Project(models.Model):
    """Model for imported GitHub projects"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    github_url = models.URLField()
    github_repo_id = models.CharField(max_length=50, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_projects')
    
    # Repository metadata
    primary_language = models.CharField(max_length=50, blank=True)
    languages = models.JSONField(default=dict, blank=True)  # Language percentages
    stars_count = models.IntegerField(default=0)
    forks_count = models.IntegerField(default=0)
    
    # Learning metadata
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    tags = models.JSONField(default=list, blank=True)
    
    # Engagement metrics
    views_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    github_created_at = models.DateTimeField(null=True, blank=True)
    github_updated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class ProjectFile(models.Model):
    """Model for storing project file structure and content"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file_path = models.CharField(max_length=500)
    content = models.TextField()
    file_type = models.CharField(max_length=50)
    size = models.IntegerField(default=0)
    
    # AI explanations cache
    ai_explanation = models.TextField(blank=True)
    explanation_generated_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['project', 'file_path']
    
    def __str__(self):
        return f"{self.project.name}/{self.file_path}"

class ProjectLike(models.Model):
    """Model for tracking user likes on projects"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='user_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'project']
    
    def __str__(self):
        return f"{self.user.username} likes {self.project.name}"
