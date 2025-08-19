from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectFileViewSet


router = DefaultRouter()
router.register(r'items', ProjectViewSet, basename='projects')
router.register(r'files', ProjectFileViewSet, basename='project-files')


urlpatterns = [
	path('', include(router.urls)),
]
