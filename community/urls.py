from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('projects/<int:project_id>/ask/', views.ask_question_view, name='ask_question'),
    path('questions/<int:question_id>/answer/', views.answer_question_view, name='answer_question'),
    path('projects/<int:project_id>/comment/', views.add_comment_view, name='add_comment'),
    path('vote/', views.vote_content, name='vote'),
]