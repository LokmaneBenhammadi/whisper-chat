from django.urls import path
from .views import register,login,verify_otp      # Import your new view

urlpatterns = [
    path('register', register, name='register'),
    path('login', login, name='login'),
    path('verify-otp', verify_otp, name='verify_otp'),
]