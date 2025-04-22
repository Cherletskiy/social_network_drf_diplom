from rest_framework.decorators import action
from rest_framework.viewsets import  ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Post, Comment, Like
from .serializers import PostListSerializer, PostDetailSerializer, PostCreateSerializer, CommentSerializer

# Create your views here.


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().select_related('author').prefetch_related('images', 'likes', 'comments')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateSerializer
        if self.action == 'list':
            return PostListSerializer
        return PostDetailSerializer

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        like, created = Like.objects.get_or_create(user=user, post=post)

        if not created:
            like.delete()

        return self.retrieve(request, pk)

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs['post_pk']
        return self.queryset.filter(post_id=post_id)


