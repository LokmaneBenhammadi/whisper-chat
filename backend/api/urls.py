from django.urls import path
from .views import api_status
from django.urls import include 

urlpatterns = [
    path('status/', api_status, name='api-status'),
    path('auth/', include('account.urls')),
]