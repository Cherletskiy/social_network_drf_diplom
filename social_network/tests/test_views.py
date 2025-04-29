from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from social_network_app.models import Post, User, Like
from rest_framework import status


class PostViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.admin = User.objects.create_superuser(username='admin', password='adminpass')
        Post.objects.all().delete()
        self.post = Post.objects.create(author=self.user, text='Test post')

    def test_list_posts(self):
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_post_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        data = {'text': 'New post', 'location': 'New York'}
        response = self.client.post(reverse('post-list'), data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)

    def test_create_post_unauthenticated(self):
        data = {'text': 'New post'}
        response = self.client.post(reverse('post-list'), data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_post_as_owner(self):
        self.client.login(username='testuser', password='testpass')
        data = {'text': 'Updated post'}
        response = self.client.patch(reverse('post-detail', kwargs={'pk': self.post.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, 'Updated post')

    def test_update_post_as_non_owner(self):
        self.client.login(username='otheruser', password='otherpass')
        data = {'text': 'Updated post'}
        response = self.client.patch(reverse('post-detail', kwargs={'pk': self.post.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_like_post(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('post-like', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Like.objects.filter(user=self.user, post=self.post).exists())

    def test_unlike_post(self):
        Like.objects.create(user=self.user, post=self.post)
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('post-like', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Like.objects.filter(user=self.user, post=self.post).exists())