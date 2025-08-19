from django.contrib import admin
from .models import Question, Answer, Comment, Vote

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'project', 'upvotes', 'downvotes', 'is_answered', 'is_pinned', 'created_at')
    list_filter = ('is_answered', 'is_pinned', 'created_at', 'project__primary_language')
    search_fields = ('title', 'content', 'user__username', 'project__name')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'upvotes', 'downvotes', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('content', 'user__username', 'question__title')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'upvotes', 'downvotes', 'created_at')
    list_filter = ('created_at', 'project__primary_language')
    search_fields = ('content', 'user__username', 'project__name')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_id', 'vote_type', 'created_at')
    list_filter = ('content_type', 'vote_type', 'created_at')
    search_fields = ('user__username',)
