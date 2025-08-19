import requests
import base64
from django.conf import settings
from .models import Project, ProjectFile

class GitHubService:
    """Service for interacting with GitHub API"""
    
    BASE_URL = "https://api.github.com"
    
    @classmethod
    def get_repository_info(cls, owner, repo):
        """Get repository information from GitHub API"""
        url = f"{cls.BASE_URL}/repos/{owner}/{repo}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    @classmethod
    def get_repository_languages(cls, owner, repo):
        """Get repository languages from GitHub API"""
        url = f"{cls.BASE_URL}/repos/{owner}/{repo}/languages"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()
        return {}
    
    @classmethod
    def get_repository_contents(cls, owner, repo, path="", max_files=50):
        """Get repository file contents recursively"""
        url = f"{cls.BASE_URL}/repos/{owner}/{repo}/contents/{path}"
        response = requests.get(url)
        
        if response.status_code != 200:
            return []
        
        contents = response.json()
        files = []
        
        for item in contents:
            if len(files) >= max_files:
                break
                
            if item['type'] == 'file':
                # Skip large files and binary files
                if item['size'] > 100000:  # Skip files larger than 100KB
                    continue
                
                # Skip common binary file types
                skip_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.exe', '.dll']
                if any(item['name'].lower().endswith(ext) for ext in skip_extensions):
                    continue
                
                # Get file content
                file_content = cls.get_file_content(item['download_url'])
                if file_content:
                    files.append({
                        'path': item['path'],
                        'content': file_content,
                        'size': item['size'],
                        'type': cls.get_file_type(item['name'])
                    })
            
            elif item['type'] == 'dir' and len(files) < max_files:
                # Recursively get directory contents
                subfiles = cls.get_repository_contents(owner, repo, item['path'], max_files - len(files))
                files.extend(subfiles)
        
        return files
    
    @classmethod
    def get_file_content(cls, download_url):
        """Get file content from download URL"""
        try:
            response = requests.get(download_url)
            if response.status_code == 200:
                # Try to decode as text
                try:
                    return response.text
                except UnicodeDecodeError:
                    # Skip binary files
                    return None
            return None
        except Exception:
            return None
    
    @classmethod
    def get_file_type(cls, filename):
        """Determine file type from filename"""
        extension = filename.split('.')[-1].lower() if '.' in filename else ''
        
        type_mapping = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'jsx': 'javascript',
            'tsx': 'typescript',
            'html': 'html',
            'css': 'css',
            'scss': 'scss',
            'sass': 'sass',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'h': 'c',
            'hpp': 'cpp',
            'cs': 'csharp',
            'php': 'php',
            'rb': 'ruby',
            'go': 'go',
            'rs': 'rust',
            'swift': 'swift',
            'kt': 'kotlin',
            'scala': 'scala',
            'r': 'r',
            'sql': 'sql',
            'sh': 'bash',
            'bash': 'bash',
            'yml': 'yaml',
            'yaml': 'yaml',
            'json': 'json',
            'xml': 'xml',
            'md': 'markdown',
            'txt': 'text',
        }
        
        return type_mapping.get(extension, 'text')
    
    @classmethod
    def import_project_files(cls, project, max_files=30):
        """Import files for a project from GitHub"""
        try:
            # Parse GitHub URL to get owner and repo
            parts = project.github_url.rstrip('/').split('/')
            owner = parts[-2]
            repo = parts[-1]
            
            # Get repository files
            files = cls.get_repository_contents(owner, repo, max_files=max_files)
            
            # Create ProjectFile objects
            for file_data in files:
                ProjectFile.objects.get_or_create(
                    project=project,
                    file_path=file_data['path'],
                    defaults={
                        'content': file_data['content'],
                        'file_type': file_data['type'],
                        'size': file_data['size']
                    }
                )
            
            return len(files)
            
        except Exception as e:
            print(f"Error importing files for project {project.name}: {str(e)}")
            return 0

class AIExplanationService:
    """Service for generating AI explanations of code"""
    
    @classmethod
    def generate_explanation(cls, code, file_path, project_name, file_type):
        """Generate AI explanation for code using OpenAI"""
        if not settings.OPENAI_API_KEY:
            raise Exception("OpenAI API key not configured")
        
        prompt = f"""
        Please explain this {file_type} code from the file '{file_path}' in the project '{project_name}':

        ```{file_type}
        {code}
        ```

        Provide a clear, beginner-friendly explanation that covers:
        1. What this code does (main purpose)
        2. How it works (step by step)
        3. Key concepts or patterns used
        4. Any important details for learning
        5. How it fits into the larger project

        Keep the explanation concise but informative, suitable for someone learning programming.
        """
        
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful coding instructor explaining code to students. Be clear, encouraging, and educational."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Failed to generate AI explanation: {str(e)}")

class ProjectRecommendationService:
    """Service for recommending projects based on user preferences"""
    
    @classmethod
    def get_recommendations(cls, user, skill_level=None, languages=None, limit=12):
        """Get project recommendations for a user"""
        from .models import Project
        
        # Start with all projects
        projects = Project.objects.all()
        
        # Filter by skill level
        if skill_level:
            projects = projects.filter(difficulty_level=skill_level)
        elif user and user.is_authenticated:
            projects = projects.filter(difficulty_level=user.skill_level)
        
        # Filter by languages
        if languages:
            projects = projects.filter(primary_language__in=languages)
        elif user and user.is_authenticated and user.preferred_languages:
            projects = projects.filter(primary_language__in=user.preferred_languages)
        
        # Order by popularity and relevance
        projects = projects.order_by('-likes_count', '-views_count', '-stars_count')
        
        return projects[:limit]