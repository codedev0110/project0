from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction
from github import Github
from django.conf import settings
from .models import Project, ProjectFile
from .filters import ProjectFileByProjectFilter
from .serializers import ProjectSerializer, ProjectFileSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().select_related('owner')
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def import_github(self, request):
        token = request.data.get('token') or settings.SOCIALACCOUNT_PROVIDERS.get('github', {}).get('APP', {}).get('secret')
        repo_full_name = request.data.get('repo')
        if not token or not repo_full_name:
            return Response({'error': 'token and repo are required'}, status=400)

        gh = Github(token)
        try:
            repo = gh.get_repo(repo_full_name)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

        with transaction.atomic():
            project, _ = Project.objects.update_or_create(
                owner=request.user,
                repo_full_name=repo.full_name,
                defaults={
                    'name': repo.name,
                    'description': repo.description or '',
                    'language': repo.language or '',
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'html_url': repo.html_url,
                }
            )
            # Store only top-level tree (light import)
            try:
                contents = repo.get_contents("")
                ProjectFile.objects.filter(project=project).delete()
                for item in contents:
                    ProjectFile.objects.create(
                        project=project,
                        path=item.path,
                        sha=getattr(item, 'sha', ''),
                        size=getattr(item, 'size', 0) or 0,
                        is_dir=item.type == 'dir'
                    )
            except Exception:
                pass

        return Response(ProjectSerializer(project).data)


class ProjectFileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProjectFile.objects.all()
    serializer_class = ProjectFileSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [ProjectFileByProjectFilter]

# Create your views here.
