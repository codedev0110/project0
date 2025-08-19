from django.db import models
from django.conf import settings

class Question(models.Model):
    """Model for user questions about projects"""
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='questions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=200)
    content = models.TextField()
    file_path = models.CharField(max_length=500, blank=True, null=True)  # Specific file being asked about
    line_number = models.IntegerField(blank=True, null=True)  # Specific line being asked about
    
    # Engagement metrics
    views_count = models.IntegerField(default=0)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    
    # Status
    is_answered = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return self.title

class Answer(models.Model):
    """Model for answers to questions"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    
    # Engagement metrics
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    
    # Status
    is_accepted = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_accepted', '-upvotes', '-created_at']
    
    def __str__(self):
        return f"Answer to: {self.question.title}"

class Comment(models.Model):
    """Model for general comments on projects"""
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    file_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Engagement metrics
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.project.name}"

class Vote(models.Model):
    """Model for tracking votes on questions, answers, and comments"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes')
    
    # Generic foreign key fields for voting on different content types
    content_type = models.CharField(
        max_length=20,
        choices=[
            ('question', 'Question'),
            ('answer', 'Answer'),
            ('comment', 'Comment'),
        ]
    )
    object_id = models.PositiveIntegerField()
    
    vote_type = models.CharField(
        max_length=10,
        choices=[
            ('upvote', 'Upvote'),
            ('downvote', 'Downvote'),
        ]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'content_type', 'object_id']
    
    def __str__(self):
        return f"{self.user.username} {self.vote_type} on {self.content_type} {self.object_id}"
