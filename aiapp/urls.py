from django.urls import path
from .views import ExplainCodeView


urlpatterns = [
	path('explain/', ExplainCodeView.as_view(), name='ai-explain'),
]
