from rest_framework import serializers
from ..models import User
from comments.serializers.common import CommentSerializer

class ProfileSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'comments']