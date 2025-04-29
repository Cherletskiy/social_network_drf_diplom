from django.test import TestCase
from django.contrib.auth.models import User
from social_network_app.models import Post, PostImage, Comment, Like
from django.utils import timezone


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(
            author=self.user, text='Test post', location='40.7128, -74.0060'
        )

    def test_post_creation(self):
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.text, 'Test post')
        self.assertTrue(self.post.created_date <= timezone.now())
        self.assertEqual(str(self.post), self.post.text[:50])

    def test_post_ordering(self):
        post2 = Post.objects.create(author=self.user, text='Second post')
        posts = Post.objects.all()
        self.assertEqual(posts[0], post2)

    def test_post_image_creation(self):
        image = PostImage.objects.create(post=self.post, image='path/to/image.jpg')
        self.assertEqual(image.post, self.post)

    def test_comment_creation(self):
        comment = Comment.objects.create(post=self.post, author=self.user, text='Test comment')
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)

    def test_like_uniqueness(self):
        Like.objects.create(user=self.user, post=self.post)
        with self.assertRaises(Exception):
            Like.objects.create(user=self.user, post=self.post)