from django.contrib.auth.models import Group, User
from rest_framework import serializers

from .models import Post, Comment, Like, PostImage


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'author_username', 'text', 'created_date']
        read_only_fields = ['author', 'created_date']

    def create(self, validated_data):
        user = self.context['request'].user
        post_id = self.context['view'].kwargs['post_pk']
        validated_data['post_id'] = post_id
        comment = Comment.objects.create(author=user, **validated_data)
        return comment


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image']


class PostListSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'author_username', 'text', 'created_date',
            'images', 'comments_count', 'likes_count', 'is_liked'
        ]
        read_only_fields = ['author', 'created_date']

    def get_is_liked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.likes.filter(user=user).exists()
        return False


class PostCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        user = self.context['request'].user
        post = Post.objects.create(author=user, **validated_data)

        for image_data in images_data:
            PostImage.objects.create(post=post, image=image_data)

        return post

    class Meta:
        model = Post
        fields = ['text', 'images']


class PostDetailSerializer(PostListSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = PostListSerializer.Meta.fields + ['comments']