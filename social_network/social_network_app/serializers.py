from django.contrib.auth.models import Group, User
from rest_framework import serializers

from .models import Post, Comment, Like, PostImage


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'author', 'author_username', 'text', 'created_date']
        read_only_fields = ['author', 'created_date']


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image']


class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'author_username', 'text', 'created_date',
            'images', 'comments', 'likes_count', 'is_liked'
        ]
        read_only_fields = ['author', 'created_date']


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