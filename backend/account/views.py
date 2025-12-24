from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
import secrets
from .models import Account, OTP
from django.utils import timezone
from django.conf import settings
from twilio.rest import Client

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def send_sms(phone_number, otp):
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=f"Your Whisper code is: {otp}",
            messaging_service_sid=settings.TWILIO_MESSAGING_SERVICE_SID,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"Twilio Error: {e}")
        return False

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    phone = data.get('phone_number')
    
    if Account.objects.filter(phone_number=phone).exists():
        return Response({"error": "User already exists. Please login."}, status=400)

    user = Account.objects.create(
        phone_number=phone,
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        verified=False
    )
    
    code = secrets.randbelow(1000000)
    OTP.objects.create(user=user, otp_code=f"{code:06d}")
    
    sms_sent = send_sms(phone, f"{code:06d}")
    
    if not sms_sent:
        return Response({"error": "Failed to send SMS."}, status=500)
    return Response({"message": "User created. OTP sent."}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    phone = request.data.get('phone_number')

    if not phone:
        return Response({"error": "Phone number is required"}, status=400)

    try:
        user = Account.objects.get(phone_number=phone)
    except Account.DoesNotExist:
        return Response({"error": "User not found. Please register."}, status=404)

    code = secrets.randbelow(1000000)
    
    OTP.objects.filter(user=user).delete()
    
    OTP.objects.create(user=user, otp_code=f"{code:06d}")
    
    sms_sent = send_sms(phone, f"{code:06d}")
    
    if not sms_sent:
        return Response({"error": "Failed to send SMS."}, status=500)
    return Response({"message": "OTP sent."}, status=200)



@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    phone = request.data.get('phone_number')
    otp_code = request.data.get('otp_code')

    if not phone or not otp_code:
        return Response({"error": "Phone and OTP code are required"}, status=400)

    user = get_object_or_404(Account, phone_number=phone)

    otp_entry = OTP.objects.filter(user=user).last()

    if not otp_entry:
        return Response({"error": "No OTP found for this user"}, status=400)
    
    if otp_entry.otp_code != otp_code:
        otp_entry.attempts += 1
        if otp_entry.attempts >= 5:
            otp_entry.delete()
            return Response({"error": "Too many failed attempts. OTP invalidated."}, status=400)
        otp_entry.save()
        return Response({"error": "Invalid OTP code"}, status=400)

    if otp_entry.is_expired:
        otp_entry.delete()
        return Response({"error": "OTP expired. Please request a new one."}, status=400)
    
    if otp_entry.attempts >= 5:
        otp_entry.delete()
        return Response({"error": "Too many failed attempts. OTP invalidated."}, status=400)
    
    # --- SUCCESS! ---
    user.last_login = timezone.now()
    user.save()

    otp_entry.delete()
    tokens = get_tokens_for_user(user)

    return Response({
        "message": "Login successful",
        "tokens": tokens,
        "user_id": user.id
    }, status=200)