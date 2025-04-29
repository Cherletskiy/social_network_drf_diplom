from django.test import TestCase
from rest_framework.test import APIRequestFactory
from social_network_app.permissions import IsOwnerOrAdmin
from social_network_app.models import Post, User


class PermissionTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.admin = User.objects.create_superuser(username='admin', password='adminpass')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.post = Post.objects.create(author=self.user, text='Test post')
        self.permission = IsOwnerOrAdmin()

    def test_owner_has_permission(self):
        request = self.factory.get('/')
        request.user = self.user
        self.assertTrue(self.permission.has_object_permission(request, None, self.post))

    def test_admin_has_permission(self):
        request = self.factory.get('/')
        request.user = self.admin
        self.assertTrue(self.permission.has_object_permission(request, None, self.post))

    def test_non_owner_has_no_permission(self):
        request = self.factory.get('/')
        request.user = self.other_user
        self.assertFalse(self.permission.has_object_permission(request, None, self.post))