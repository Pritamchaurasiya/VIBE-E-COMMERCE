from rest_framework import generics, permissions
from .models import ForumPost, ForumComment, MarketPrice
from .serializers import ForumPostSerializer, ForumCommentSerializer, MarketPriceSerializer

class ForumPostListCreateView(generics.ListCreateAPIView):
    """API view to list and create forum posts."""
    queryset = ForumPost.objects.all().order_by('-created_at')
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class ForumPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view to retrieve, update or delete a forum post."""
    queryset = ForumPost.objects.all()
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ForumCommentCreateView(generics.CreateAPIView):
    """API view to add a comment to a post."""
    serializer_class = ForumCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        serializer.save(author=self.request.user, post_id=post_id)

class MarketPriceListView(generics.ListAPIView):
    """API view to list daily market prices."""
    queryset = MarketPrice.objects.all().order_by('-date')
    serializer_class = MarketPriceSerializer
    permission_classes = [permissions.AllowAny]
