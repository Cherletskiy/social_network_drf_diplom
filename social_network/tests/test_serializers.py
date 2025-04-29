from django.test import TestCase
from rest_framework.test import APIRequestFactory
from social_network_app.serializers import PostListSerializer, PostCreateSerializer, CommentSerializer
from social_network_app.models import Post, Comment, User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io


class SerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        Post.objects.all().delete()
        self.post = Post.objects.create(author=self.user, text='Test post')
        self.request_factory = APIRequestFactory()

    def test_post_list_serializer(self):
        request = self.request_factory.get('/')
        request.user = self.user
        serializer = PostListSerializer(self.post, context={'request': request})
        data = serializer.data
        self.assertEqual(data['author_username'], 'testuser')
        self.assertEqual(data['text'], 'Test post')
        self.assertEqual(data['likes_count'], 0)
        self.assertFalse(data['is_liked'])

    def test_post_create_serializer(self):
        image_file = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(image_file, format='JPEG')
        image_file.seek(0)
        image = SimpleUploadedFile("test.jpg", image_file.read(), content_type="image/jpeg")

        data = {
            'text': 'New post',
            'location': 'New York',
            'images': [image]
        }
        request = self.request_factory.post('/')
        request.user = self.user
        serializer = PostCreateSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        post = serializer.save()
        self.assertEqual(post.text, 'New post')
        self.assertEqual(post.images.count(), 1)

    def test_comment_serializer(self):
        data = {'text': 'Test comment'}
        request = self.request_factory.post('/')
        request.user = self.user
        serializer = CommentSerializer(
            data=data, context={'request': request, 'view': type('obj', (), {'kwargs': {'post_pk': self.post.pk}})}
        )
        self.assertTrue(serializer.is_valid())
        comment = serializer.save()
        self.assertEqual(comment.text, 'Test comment')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)