from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Question, Answer, Comment, Vote
from projects.models import Project

@login_required
def ask_question_view(request, project_id):
    """Create a new question about a project"""
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        file_path = request.POST.get('file_path', '').strip()
        line_number = request.POST.get('line_number', '')
        
        if not title or not content:
            messages.error(request, 'Title and content are required.')
            return redirect('community:ask_question', project_id=project.id)
        
        question = Question.objects.create(
            project=project,
            user=request.user,
            title=title,
            content=content,
            file_path=file_path if file_path else None,
            line_number=int(line_number) if line_number.isdigit() else None
        )
        
        messages.success(request, 'Question posted successfully!')
        return redirect('projects:detail', project_id=project.id)
    
    context = {
        'project': project,
    }
    return render(request, 'community/ask_question.html', context)

@login_required
def answer_question_view(request, question_id):
    """Create an answer to a question"""
    question = get_object_or_404(Question, id=question_id)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        
        if not content:
            messages.error(request, 'Answer content is required.')
            return redirect('community:answer_question', question_id=question.id)
        
        answer = Answer.objects.create(
            question=question,
            user=request.user,
            content=content
        )
        
        # Mark question as answered if this is the first answer
        if not question.is_answered:
            question.is_answered = True
            question.save()
        
        messages.success(request, 'Answer posted successfully!')
        return redirect('projects:detail', project_id=question.project.id)
    
    context = {
        'question': question,
    }
    return render(request, 'community/answer_question.html', context)

@login_required
def add_comment_view(request, project_id):
    """Add a comment to a project"""
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        file_path = request.POST.get('file_path', '').strip()
        
        if not content:
            messages.error(request, 'Comment content is required.')
            return redirect('projects:detail', project_id=project.id)
        
        comment = Comment.objects.create(
            project=project,
            user=request.user,
            content=content,
            file_path=file_path if file_path else None
        )
        
        messages.success(request, 'Comment added successfully!')
        return redirect('projects:detail', project_id=project.id)
    
    return redirect('projects:detail', project_id=project.id)

@login_required
@csrf_exempt
def vote_content(request):
    """Handle voting on questions, answers, and comments"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        content_type = data.get('content_type')
        object_id = data.get('object_id')
        vote_type = data.get('vote_type')
        
        if content_type not in ['question', 'answer', 'comment']:
            return JsonResponse({'error': 'Invalid content type'}, status=400)
        
        if vote_type not in ['upvote', 'downvote']:
            return JsonResponse({'error': 'Invalid vote type'}, status=400)
        
        # Get or create vote
        vote, created = Vote.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id,
            defaults={'vote_type': vote_type}
        )
        
        # Get the target object
        if content_type == 'question':
            target_obj = get_object_or_404(Question, id=object_id)
        elif content_type == 'answer':
            target_obj = get_object_or_404(Answer, id=object_id)
        else:  # comment
            target_obj = get_object_or_404(Comment, id=object_id)
        
        if not created:
            # User already voted, check if changing vote type
            if vote.vote_type == vote_type:
                # Remove vote
                vote.delete()
                if vote_type == 'upvote':
                    target_obj.upvotes = max(0, target_obj.upvotes - 1)
                else:
                    target_obj.downvotes = max(0, target_obj.downvotes - 1)
                voted = False
            else:
                # Change vote type
                old_vote_type = vote.vote_type
                vote.vote_type = vote_type
                vote.save()
                
                # Update counts
                if old_vote_type == 'upvote':
                    target_obj.upvotes = max(0, target_obj.upvotes - 1)
                    target_obj.downvotes += 1
                else:
                    target_obj.downvotes = max(0, target_obj.downvotes - 1)
                    target_obj.upvotes += 1
                voted = True
        else:
            # New vote
            if vote_type == 'upvote':
                target_obj.upvotes += 1
            else:
                target_obj.downvotes += 1
            voted = True
        
        target_obj.save()
        
        return JsonResponse({
            'voted': voted,
            'vote_type': vote_type,
            'upvotes': target_obj.upvotes,
            'downvotes': target_obj.downvotes
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
