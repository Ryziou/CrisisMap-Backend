from .models import User
from lib.permissions import IsUserItself
from .serializers.common import UserSerializer
from .serializers.populated import ProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.generics import RetrieveUpdateDestroyAPIView

class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serialized_user = UserSerializer(data=request.data)
        serialized_user.is_valid(raise_exception=True)
        serialized_user.save()
        return Response({ 'detail': 'You have created an account!'})
    
class ProfileView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        profile = ProfileSerializer(request.user)
        return Response(profile.data)
    
    def put(self, request):
        user = request.user
        edit_serializer = UserSerializer(user, data=request.data, partial=True)
        edit_serializer.is_valid(raise_exception=True)
        edit_serializer.save()
        return Response(edit_serializer.data)
    
    def delete(self, request):
        request.user.delete()
        return Response({ 'detail': 'User deleted'}, status=204)
    
class PublicProfileView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsUserItself()]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProfileSerializer

        return UserSerializer