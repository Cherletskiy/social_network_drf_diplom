from django.contrib.auth.models import Group, User
from rest_framework import serializers

from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from geopy.geocoders import Nominatim

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
    location_name = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'author_username', 'location_name', 'text', 'created_date',
            'images', 'comments_count', 'likes_count', 'is_liked'
        ]
        read_only_fields = ['author', 'created_date']

    def get_is_liked(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.likes.filter(user=user).exists()
        return False

    def get_location_name(self, obj):
        if not obj.location:
            return None

        try:
            geolocator = Nominatim(user_agent='myGeocoder')
            location = geolocator.reverse(obj.location.split(','))
            return location.address if location else None
        except (GeocoderTimedOut, GeocoderServiceError):
            return obj.location



class PostCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(
            max_length=10 * 1024 * 1024,
            allow_empty_file=False,
            use_url=False
        ),
        write_only=True,
        required=False,
        max_length=10
    )

    class Meta:
        model = Post
        fields = ['text', 'images', 'location']
        read_only_fields = ['author']

    def validate_location(self, value):
        if not value:
            return None

        try:
            geolocator = Nominatim(user_agent='myGeocoder')
            location = geolocator.geocode(value)
            if not location:
                raise serializers.ValidationError("Не удалось определить координаты для указанного места")
            return f"{location.latitude}, {location.longitude}"
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            raise serializers.ValidationError(f"Ошибка при указании локации {e}. Попробуйте иные координаты или оставьте поле пустым")

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        user = self.context['request'].user
        post = Post.objects.create(author=user, **validated_data)

        for image_data in images_data:
            PostImage.objects.create(post=post, image=image_data)

        return post

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)

        if images_data is not None:
            instance.images.all().delete()
            self._create_images(instance, images_data)

        return super().update(instance, validated_data)

    def _create_images(self, post, images_data):
        for image_data in images_data:
            PostImage.objects.create(post=post, image=image_data)


class PostDetailSerializer(PostListSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = PostListSerializer.Meta.fields + ['comments']