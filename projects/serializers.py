from rest_framework import serializers
from .models import Project, ProjectFile


class ProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = ['id', 'path', 'sha', 'size', 'is_dir']


class ProjectSerializer(serializers.ModelSerializer):
    files = ProjectFileSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'owner', 'repo_full_name', 'name', 'description', 'language',
            'difficulty', 'tags', 'stars', 'forks', 'html_url', 'created_at', 'files'
        ]
        read_only_fields = ['owner', 'created_at']
