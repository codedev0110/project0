from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db.models import Q, Count
import requests
import json
import openai
from .models import Project, ProjectFile, ProjectLike
from community.models import Question, Comment
from .services import GitHubService, AIExplanationService, ProjectRecommendationService

def home_view(request):
    """Homepage with project recommendations"""
    projects = Project.objects.all()
    
    # Filter by user preferences if logged in
    if request.user.is_authenticated and request.user.preferred_languages:
        projects = projects.filter(
            primary_language__in=request.user.preferred_languages
        )
    
    # Get recent projects
    recent_projects = projects.order_by('-created_at')[:6]
    popular_projects = projects.order_by('-likes_count', '-views_count')[:6]
    
    context = {
        'recent_projects': recent_projects,
        'popular_projects': popular_projects,
    }
    return render(request, 'projects/home.html', context)

def project_detail_view(request, project_id):
    """Detailed view of a project with code viewer and community features"""
    project = get_object_or_404(Project, id=project_id)
    
    # Increment view count
    project.views_count += 1
    project.save()
    
    # Get project files
    files = project.files.all().order_by('file_path')
    
    # Get community content
    questions = project.questions.all()[:10]
    comments = project.comments.all()[:10]
    
    # Check if user has liked this project
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = ProjectLike.objects.filter(
            user=request.user, project=project
        ).exists()
    
    context = {
        'project': project,
        'files': files,
        'questions': questions,
        'comments': comments,
        'user_has_liked': user_has_liked,
    }
    return render(request, 'projects/detail.html', context)

def project_list_view(request):
    """List view with filtering and search"""
    projects = Project.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(primary_language__icontains=search_query)
        )
    
    # Filter by language
    language_filter = request.GET.get('language', '')
    if language_filter:
        projects = projects.filter(primary_language=language_filter)
    
    # Filter by difficulty
    difficulty_filter = request.GET.get('difficulty', '')
    if difficulty_filter:
        projects = projects.filter(difficulty_level=difficulty_filter)
    
    # Sorting
    sort_by = request.GET.get('sort', 'recent')
    if sort_by == 'popular':
        projects = projects.order_by('-likes_count', '-views_count')
    elif sort_by == 'stars':
        projects = projects.order_by('-stars_count')
    else:  # recent
        projects = projects.order_by('-created_at')
    
    # Get unique languages for filter dropdown
    languages = Project.objects.values_list('primary_language', flat=True).distinct()
    
    context = {
        'projects': projects,
        'languages': languages,
        'search_query': search_query,
        'language_filter': language_filter,
        'difficulty_filter': difficulty_filter,
        'sort_by': sort_by,
    }
    return render(request, 'projects/list.html', context)

@login_required
def import_github_project(request):
    """Import a project from GitHub"""
    if request.method == 'POST':
        github_url = request.POST.get('github_url', '').strip()
        
        if not github_url:
            messages.error(request, 'Please provide a GitHub URL.')
            return redirect('projects:import')
        
        # Parse GitHub URL to get owner and repo
        try:
            # Expected format: https://github.com/owner/repo
            parts = github_url.rstrip('/').split('/')
            owner = parts[-2]
            repo = parts[-1]
        except (IndexError, ValueError):
            messages.error(request, 'Invalid GitHub URL format.')
            return redirect('projects:import')
        
        # Fetch repository data from GitHub API
        repo_data = GitHubService.get_repository_info(owner, repo)
        
        if not repo_data:
            messages.error(request, 'Repository not found or not accessible.')
            return redirect('projects:import')
        
        # Check if project already exists
        if Project.objects.filter(github_repo_id=str(repo_data['id'])).exists():
            messages.error(request, 'This project has already been imported.')
            return redirect('projects:import')
        
        # Create project
        project = Project.objects.create(
            name=repo_data['name'],
            description=repo_data.get('description', ''),
            github_url=github_url,
            github_repo_id=str(repo_data['id']),
            owner=request.user,
            primary_language=repo_data.get('language', ''),
            stars_count=repo_data.get('stargazers_count', 0),
            forks_count=repo_data.get('forks_count', 0),
        )
        
        # Fetch repository languages
        languages = GitHubService.get_repository_languages(owner, repo)
        if languages:
            project.languages = languages
            project.save()
        
        # Import project files in the background
        files_imported = GitHubService.import_project_files(project)
        if files_imported > 0:
            messages.success(request, f'Successfully imported {project.name} with {files_imported} files!')
        else:
            messages.success(request, f'Successfully imported {project.name}! Files will be imported shortly.')
        
        return redirect('projects:detail', project_id=project.id)
    
    return render(request, 'projects/import.html')

@login_required
@csrf_exempt
def toggle_like_project(request, project_id):
    """Toggle like status for a project"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    project = get_object_or_404(Project, id=project_id)
    
    like, created = ProjectLike.objects.get_or_create(
        user=request.user,
        project=project
    )
    
    if not created:
        # Unlike
        like.delete()
        project.likes_count = max(0, project.likes_count - 1)
        liked = False
    else:
        # Like
        project.likes_count += 1
        liked = True
    
    project.save()
    
    return JsonResponse({
        'liked': liked,
        'likes_count': project.likes_count
    })

@csrf_exempt
def get_ai_explanation(request, project_id, file_id):
    """Get AI explanation for a specific file or code block"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    project = get_object_or_404(Project, id=project_id)
    project_file = get_object_or_404(ProjectFile, id=file_id, project=project)
    
    # Check if we have a cached explanation
    if project_file.ai_explanation:
        return JsonResponse({
            'explanation': project_file.ai_explanation,
            'cached': True
        })
    
    # Generate new explanation using OpenAI
    if not settings.OPENAI_API_KEY:
        return JsonResponse({'error': 'AI explanation service not configured'}, status=503)
    
    try:
        # Get specific code selection if provided
        data = json.loads(request.body)
        selected_code = data.get('selected_code', project_file.content)
        
        explanation = AIExplanationService.generate_explanation(
            selected_code,
            project_file.file_path,
            project.name,
            project_file.file_type
        )
        
        # Cache the explanation if it's for the whole file
        if selected_code == project_file.content:
            project_file.ai_explanation = explanation
            project_file.save()
        
        return JsonResponse({
            'explanation': explanation,
            'cached': False
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Failed to generate explanation: {str(e)}'}, status=500)

def learning_mode_view(request):
    """Learning mode with project recommendations"""
    if request.method == 'POST':
        skill_level = request.POST.get('skill_level', 'beginner')
        languages = request.POST.getlist('languages')
        
        # Get recommendations using the service
        projects = ProjectRecommendationService.get_recommendations(
            request.user, skill_level, languages
        )
        
        context = {
            'projects': projects,
            'selected_skill_level': skill_level,
            'selected_languages': languages,
        }
        return render(request, 'projects/learning_results.html', context)
    
    # Get available languages
    languages = Project.objects.values_list('primary_language', flat=True).distinct()
    languages = [lang for lang in languages if lang]  # Remove empty values
    
    context = {
        'languages': sorted(languages),
    }
    return render(request, 'projects/learning_mode.html', context)
