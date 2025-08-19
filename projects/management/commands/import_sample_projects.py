from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projects.models import Project
from projects.services import GitHubService

User = get_user_model()

class Command(BaseCommand):
    help = 'Import sample projects for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            default='admin',
            help='Username to assign projects to (default: admin)'
        )
    
    def handle(self, *args, **options):
        username = options['user']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist. Create it first.')
            )
            return
        
        # Sample projects to import
        sample_repos = [
            {
                'url': 'https://github.com/microsoft/vscode',
                'difficulty': 'advanced',
                'description_override': 'Visual Studio Code - A powerful, lightweight code editor'
            },
            {
                'url': 'https://github.com/django/django',
                'difficulty': 'advanced',
                'description_override': 'The Django web framework for Python'
            },
            {
                'url': 'https://github.com/facebook/react',
                'difficulty': 'intermediate',
                'description_override': 'A JavaScript library for building user interfaces'
            },
            {
                'url': 'https://github.com/tensorflow/tensorflow',
                'difficulty': 'advanced',
                'description_override': 'An Open Source Machine Learning Framework'
            },
            {
                'url': 'https://github.com/python/cpython',
                'difficulty': 'advanced',
                'description_override': 'The Python programming language'
            }
        ]
        
        for repo_info in sample_repos:
            try:
                # Parse GitHub URL
                parts = repo_info['url'].rstrip('/').split('/')
                owner = parts[-2]
                repo = parts[-1]
                
                # Get repository data
                repo_data = GitHubService.get_repository_info(owner, repo)
                
                if not repo_data:
                    self.stdout.write(
                        self.style.WARNING(f'Could not fetch data for {repo_info["url"]}')
                    )
                    continue
                
                # Check if already exists
                if Project.objects.filter(github_repo_id=str(repo_data['id'])).exists():
                    self.stdout.write(
                        self.style.WARNING(f'Project {repo_data["name"]} already exists')
                    )
                    continue
                
                # Create project
                project = Project.objects.create(
                    name=repo_data['name'],
                    description=repo_info.get('description_override', repo_data.get('description', '')),
                    github_url=repo_info['url'],
                    github_repo_id=str(repo_data['id']),
                    owner=user,
                    primary_language=repo_data.get('language', ''),
                    stars_count=repo_data.get('stargazers_count', 0),
                    forks_count=repo_data.get('forks_count', 0),
                    difficulty_level=repo_info['difficulty']
                )
                
                # Get languages
                languages = GitHubService.get_repository_languages(owner, repo)
                if languages:
                    project.languages = languages
                    project.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully imported {project.name}')
                )
                
                # Import a few sample files (limited to avoid rate limits)
                files_imported = GitHubService.import_project_files(project, max_files=10)
                self.stdout.write(
                    self.style.SUCCESS(f'Imported {files_imported} files for {project.name}')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error importing {repo_info["url"]}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Sample project import completed!')
        )