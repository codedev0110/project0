#!/bin/bash

# CodeLearnAI Deployment Script

echo "🚀 Starting CodeLearnAI deployment..."

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Collect static files for production
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "👤 Setting up admin user..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin user created: admin/admin123')
else:
    print('Admin user already exists')
"

# Import sample projects (optional)
read -p "Import sample projects for testing? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📚 Importing sample projects..."
    python manage.py import_sample_projects
fi

echo "✅ Deployment completed!"
echo "🌐 You can now run: python manage.py runserver"
echo "🔧 Admin panel: http://localhost:8000/admin (admin/admin123)"