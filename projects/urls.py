from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list_view, name='list'),
    path('<int:project_id>/', views.project_detail_view, name='detail'),
    path('import/', views.import_github_project, name='import'),
    path('learning/', views.learning_mode_view, name='learning_mode'),
    path('<int:project_id>/like/', views.toggle_like_project, name='toggle_like'),
    path('<int:project_id>/files/<int:file_id>/explain/', views.get_ai_explanation, name='ai_explanation'),
]