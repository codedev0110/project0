from django.urls import path
from django.shortcuts import get_object_or_404, render
from .models import Project


def project_detail(request, pk: int):
	project = get_object_or_404(Project, pk=pk)
	return render(request, 'projects/detail.html', {'project': project})


urlpatterns = [
	path('<int:pk>/', project_detail, name='project-detail'),
]
