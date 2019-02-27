from django.test import TestCase
from django.core import mail
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.test import force_authenticate
from apps.subscriptions.models import Subscription
from django.contrib.auth.models import User
from apps.networks.models import TEST_SCANNER
import json
import pytest
import io
from pprint import pprint


@pytest.mark.django_db
class SubscriptionTestCase(TestCase):
    @classmethod
    def setup_class(cls):
        cls.client = APIClient()
        cls.factory = APIRequestFactory()
        

    def test_subscription(self):
        scanner = TEST_SCANNER()
        tx_list = json.load(open('tests/transactions/block-5000015.json'))

        test_user = User.objects.create_user(username="audrey", email="test@audrey.com", password="audrey")
        
        # Create a subscription for an email address
        Subscription.objects.create(
            notify_email = test_user.email,
            watched_address = "0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1",
            user = test_user

        )

        # then process the transactions
        scanner.process_transactions(tx_list)

        # first we need to make subscription send the email...
        # then check if it got delivered
        # https://stackoverflow.com/a/3728594

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Transaction Received')

    def test_subscription_api(self):
        from apps.subscriptions import views

        # Setup factory and user
        factory = APIRequestFactory()
        user = User.objects.create_user(username='audrey', password='testing')

        request = factory.get('/subscriptions/')
        force_authenticate(request, user=user)
        list_response = views.SubscriptionList.as_view()(request)
        self.assertEqual([], list_response.data['results'])

        request = factory.post('/subscriptions/', {
            'notify_email': 'audrey@test.com',
            'watched_address': '0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1',
            'notify_sms': '8675309',
            'user': user.id
        })
        force_authenticate(request, user=user)
        views.SubscriptionList.as_view()(request)     

        request = factory.get('/subscriptions/')
        force_authenticate(request, user=user)
        list_response = views.SubscriptionList.as_view()(request)
        self.assertEqual(1, list_response.data['count'])

        scanner = TEST_SCANNER()
        tx_list = json.load(open('tests/transactions/block-5000015.json'))
        scanner.process_transactions(tx_list)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Transaction Received')