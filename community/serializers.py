from rest_framework import serializers
from .models import Question, Answer


class AnswerSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'author', 'author_username', 'body', 'score', 'created_at']
        read_only_fields = ['author', 'score', 'created_at']


class QuestionSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'project', 'author', 'author_username', 'title', 'body', 'score', 'created_at', 'answers']
        read_only_fields = ['author', 'score', 'created_at']
