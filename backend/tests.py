from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


class RecipeAPITestCase(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='auth_user')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_exists(self):
        response = self.client.get('/api/recipes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_favorite(self):
        response = self.client.get('/api/favorite/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_shopping_list(self):
        response = self.client.get('/api/carts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_follow(self):
        response = self.client.get('/api/follow/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
