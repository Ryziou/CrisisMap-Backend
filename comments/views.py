from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from lib.permissions import isOwnerOrReadOnly
from .models import Comment
from .serializers.common import CommentSerializer
from rest_framework.exceptions import ValidationError

class CommentListView(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        event_id = self.request.query_params.get('event')
        if not event_id:
            raise ValidationError({ 'event': 'Event ID is required in query parameters'})
        return Comment.objects.filter(event=event_id).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [isOwnerOrReadOnly]