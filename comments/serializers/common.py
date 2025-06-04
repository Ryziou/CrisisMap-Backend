from rest_framework import serializers
from ..models import Comment

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_at', 'updated_at', 'author', 'author_username', 'event']