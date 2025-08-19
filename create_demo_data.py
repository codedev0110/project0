#!/usr/bin/env python
"""
Quick script to create demo data for testing the CodeLearnAI platform
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codelearn_platform.settings')
django.setup()

from accounts.models import User
from projects.models import Project, ProjectFile
from community.models import Question, Answer, Comment

def create_demo_data():
    print("🎭 Creating demo data for CodeLearnAI...")
    
    # Create demo users
    users = []
    for i, (username, skill) in enumerate([
        ('alice_dev', 'beginner'),
        ('bob_coder', 'intermediate'), 
        ('charlie_pro', 'advanced')
    ], 1):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'skill_level': skill,
                'bio': f'Demo user {i} - {skill} level developer',
                'preferred_languages': ['Python', 'JavaScript'] if i <= 2 else ['Python', 'Go', 'Rust']
            }
        )
        if created:
            user.set_password('demo123')
            user.save()
            print(f"✅ Created user: {username} (password: demo123)")
        users.append(user)
    
    # Create demo projects
    demo_projects = [
        {
            'name': 'Simple Todo App',
            'description': 'A basic todo application built with Python and Django',
            'github_url': 'https://github.com/demo/todo-app',
            'github_repo_id': '12345',
            'primary_language': 'Python',
            'difficulty_level': 'beginner',
            'stars_count': 42,
            'owner': users[0]
        },
        {
            'name': 'React Dashboard',
            'description': 'Modern dashboard built with React and TypeScript',
            'github_url': 'https://github.com/demo/react-dashboard',
            'github_repo_id': '12346',
            'primary_language': 'JavaScript',
            'difficulty_level': 'intermediate',
            'stars_count': 128,
            'owner': users[1]
        },
        {
            'name': 'Microservices API',
            'description': 'Scalable microservices architecture with Go and Docker',
            'github_url': 'https://github.com/demo/microservices-api',
            'github_repo_id': '12347',
            'primary_language': 'Go',
            'difficulty_level': 'advanced',
            'stars_count': 256,
            'owner': users[2]
        }
    ]
    
    projects = []
    for project_data in demo_projects:
        project, created = Project.objects.get_or_create(
            github_repo_id=project_data['github_repo_id'],
            defaults=project_data
        )
        if created:
            print(f"✅ Created project: {project.name}")
            
            # Create sample files
            sample_files = [
                {
                    'file_path': 'main.py' if project.primary_language == 'Python' else 'index.js',
                    'content': f'# Sample {project.primary_language} code\nprint("Hello from {project.name}!")' if project.primary_language == 'Python' else f'// Sample {project.primary_language} code\nconsole.log("Hello from {project.name}!");',
                    'file_type': 'python' if project.primary_language == 'Python' else 'javascript',
                    'size': 100
                },
                {
                    'file_path': 'README.md',
                    'content': f'# {project.name}\n\n{project.description}\n\n## Installation\n\n```bash\ngit clone {project.github_url}\n```',
                    'file_type': 'markdown',
                    'size': 200
                }
            ]
            
            for file_data in sample_files:
                ProjectFile.objects.create(
                    project=project,
                    **file_data
                )
            
        projects.append(project)
    
    # Create demo questions and answers
    for i, project in enumerate(projects):
        # Create questions
        question = Question.objects.create(
            project=project,
            user=users[(i + 1) % len(users)],
            title=f"How does {project.name} handle user authentication?",
            content=f"I'm trying to understand the authentication system in {project.name}. Can someone explain how it works?",
            upvotes=5 + i * 2
        )
        
        # Create answer
        Answer.objects.create(
            question=question,
            user=users[(i + 2) % len(users)],
            content=f"Great question! In {project.name}, authentication is handled through... [This would be a detailed explanation]",
            upvotes=3 + i,
            is_accepted=True
        )
        
        # Mark question as answered
        question.is_answered = True
        question.save()
        
        # Create comments
        Comment.objects.create(
            project=project,
            user=users[i % len(users)],
            content=f"This is a really well-structured project! Great for learning {project.primary_language}.",
            upvotes=2 + i
        )
        
        print(f"✅ Created community content for: {project.name}")
    
    print("\n🎉 Demo data creation completed!")
    print("\nDemo Users (password: demo123):")
    for user in users:
        print(f"  • {user.username} ({user.skill_level})")
    
    print(f"\nDemo Projects: {len(projects)}")
    print("🌐 Visit http://localhost:8000 to see the platform!")

if __name__ == '__main__':
    create_demo_data()