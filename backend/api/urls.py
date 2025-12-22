from django.urls import path
from .views import api_status  # Import your new view

urlpatterns = [
    path('status/', api_status, name='api-status'),
]