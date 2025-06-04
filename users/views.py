from .models import User
from .serializers.common import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

class RegisterUserView(APIView):
    def post(self, request):
        serialized_user = UserSerializer(data=request.data)
        serialized_user.is_valid(raise_exception=True)
        serialized_user.save()
        return Response({ 'detail': 'You have created an account!'})