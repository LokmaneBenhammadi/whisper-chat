from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_status(request):
    """
    A simple health check or status view.
    """
    return Response({
        "status": "online",
        "message": "Whisper Chat API is running!",
        "version": "1.0.0"
    })