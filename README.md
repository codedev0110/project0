# CodeLearnAI - AI-Powered Project Learning Platform

A Django-based platform where developers can learn programming by exploring real GitHub projects with AI-powered code explanations and community discussions.

## Features

### 🤖 AI-Powered Learning
- **Smart Code Explanations**: Click the "?" button on any code block to get AI-generated explanations
- **Beginner-Friendly**: Explanations are tailored to help learners understand complex concepts
- **Context-Aware**: AI understands the project context and provides relevant insights

### 📚 Real Project Learning
- **GitHub Integration**: Import any public GitHub repository
- **File Explorer**: Browse project files with syntax highlighting
- **Multiple Languages**: Support for Python, JavaScript, Java, Go, and more
- **Difficulty Levels**: Projects categorized by beginner, intermediate, and advanced levels

### 👥 Community Features
- **Q&A System**: Ask questions about specific code or general project concepts
- **Comments**: Leave feedback and insights on projects
- **Voting System**: Upvote/downvote questions, answers, and comments
- **Reputation System**: Build reputation by providing helpful answers

### 🎯 Personalized Learning
- **Learning Mode**: Get project recommendations based on your skill level and interests
- **Progress Tracking**: Track your learning journey and favorite projects
- **Skill Assessment**: Set your skill level and preferred programming languages

### 🔐 Authentication
- **Email/Password**: Traditional account creation and login
- **GitHub OAuth**: Sign in with your GitHub account for seamless integration
- **User Profiles**: Customize your profile with bio, skills, and preferences

## Tech Stack

- **Backend**: Django 5.2.5 with Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **AI**: OpenAI GPT-3.5-turbo API
- **Code Highlighting**: Prism.js
- **Authentication**: Django Auth + GitHub OAuth

## Installation

### Prerequisites
- Python 3.8+ 
- pip
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd codelearn_platform
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```
   SECRET_KEY=your-django-secret-key
   DEBUG=True
   GITHUB_CLIENT_ID=your-github-oauth-client-id
   GITHUB_CLIENT_SECRET=your-github-oauth-client-secret
   OPENAI_API_KEY=your-openai-api-key
   ```

5. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Import Sample Projects (Optional)**
   ```bash
   python manage.py import_sample_projects
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

   Visit http://localhost:8000 to see the application.

## Configuration

### GitHub OAuth Setup

1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Create a new OAuth App with:
   - **Application name**: CodeLearnAI
   - **Homepage URL**: http://localhost:8000
   - **Authorization callback URL**: http://localhost:8000/accounts/github/callback/
3. Copy Client ID and Client Secret to your `.env` file

### OpenAI API Setup

1. Create an account at https://platform.openai.com/
2. Generate an API key
3. Add the API key to your `.env` file
4. Ensure you have sufficient credits for API usage

## Usage

### For Learners

1. **Sign Up**: Create an account or sign in with GitHub
2. **Set Preferences**: Choose your skill level and preferred programming languages
3. **Explore Projects**: Browse projects or use Learning Mode for recommendations
4. **Learn with AI**: Click "?" on any code block for AI explanations
5. **Engage**: Ask questions, leave comments, and vote on content

### For Project Owners

1. **Import Projects**: Use the "Import Project" feature to add your GitHub repositories
2. **Community Management**: Respond to questions and comments on your projects
3. **Set Difficulty**: Categorize your projects by difficulty level for better recommendations

### For Contributors

1. **Answer Questions**: Help other learners by answering their questions
2. **Share Insights**: Leave helpful comments on projects
3. **Build Reputation**: Earn reputation points through community engagement

## API Endpoints

The platform includes REST API endpoints for:

- `/api/projects/` - Project CRUD operations
- `/api/community/questions/` - Question management
- `/api/community/votes/` - Voting system
- `/api/accounts/profile/` - User profile management

## Project Structure

```
codelearn_platform/
├── accounts/           # User authentication and profiles
├── projects/          # Project management and GitHub integration
├── community/         # Q&A, comments, and voting system
├── templates/         # HTML templates
├── static/           # Static files (CSS, JS, images)
├── requirements.txt  # Python dependencies
└── manage.py        # Django management script
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:

1. Check the existing GitHub issues
2. Create a new issue with detailed information
3. Join our community discussions

## Roadmap

- [ ] Mobile-responsive design improvements
- [ ] Advanced code search and filtering
- [ ] Project comparison features
- [ ] Learning path recommendations
- [ ] Integration with more code hosting platforms
- [ ] Advanced AI features (code generation, debugging help)
- [ ] Team collaboration features
- [ ] Gamification elements

---

Built with ❤️ for the developer learning community.