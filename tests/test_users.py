from django.test import TestCase
from django.core import mail
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.test import force_authenticate
from apps.subscriptions.models import Subscription, SubscribedTransaction
from apps.users.models import CustomUser as User, APIKey
from apps.networks.models import TEST_SCANNER
from datetime import datetime, timedelta
from scripts.daily_summary import run as daily_summary
import json
import pytest
import io
from pprint import pprint


@pytest.mark.django_db
class UserTestCase(TestCase):
    @classmethod
    def setup_class(cls):
        cls.client = APIClient()
        cls.factory = APIRequestFactory()
        

    def test_make_api_key(self):
        test_user = User.objects.create_user(username="audrey", email="test@audrey.com", password="audrey")
        key = test_user.api_keys.create(nickname='testkey')
        self.assertEqual(len(key.key), 32)
        self.assertEqual(key.nickname, 'testkey')
        self.assertEqual(key.user, test_user)

    def api_key_api(self):
        from apps.users import views

        factory = APIRequestFactory()
        test_user = User.objects.create_user(username='audrey', email='test@audrey.com', password='audrey')

        request = factory.get('/keys/')
        force_authenticate(request, user=test_user)
        list_response = views.APIKeyList.as_view()(request)
        self.assertEqual([], list_response.data['results'])

        request = factory.post('/keys/', {
            'user': test_user.id,
            'key': '12345678987654321',
            'nickname': 'test api'
        })
        force_authenticate(request, user=test_user)
        response = views.APIKeyList.as_view()(request)

        request = factory.get('/keys/')
        force_authenticate(request, user=test_user)
        list_response= views.APIKeyList.as_view()(request)
        self.assertEqual(APIKey.objects.count(), 1)