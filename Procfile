web: gunicorn codelearn_platform.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate