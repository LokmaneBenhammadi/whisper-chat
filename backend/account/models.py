from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone
from django.conf import settings

class Account(AbstractBaseUser):
    # --- Basic Info ---
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, unique=True)
    
    # --- Profile ---
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    about = models.CharField(max_length=150, default="Hey! I'm using Whisper.", blank=True)
    
    # --- Status ---
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    

    is_active = models.BooleanField(default=True)

    # Configuration
    USERNAME_FIELD = 'phone_number'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class OTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)

    @property
    def is_expired(self):
        return timezone.now() > (self.created_at + timezone.timedelta(minutes=5))

    def __str__(self):
        return f"OTP for {self.user.phone_number}"