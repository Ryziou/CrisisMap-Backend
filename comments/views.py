from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from lib.permissions import CommentOwnerOrReadOnly
from .models import Comment
from .serializers.common import CommentSerializer
from rest_framework.exceptions import ValidationError

class CommentListView(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        event_id = self.request.query_params.get('event')
        user_id = self.request.query_params.get('user')

        if event_id:
            return Comment.objects.filter(event=event_id).order_by('-created_at')
        elif user_id:
            return Comment.objects.filter(author=user_id).order_by('-created_at')
        else:
            raise ValidationError({ 'detail': 'Query parameter for event or user is required'})

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [CommentOwnerOrReadOnly]