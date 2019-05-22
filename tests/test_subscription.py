from django.test import TestCase
from django.core import mail
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.test import force_authenticate
from apps.subscriptions.models import Subscription, SubscribedTransaction
from apps.users.models import CustomUser as User
from apps.networks.models import TEST_SCANNER
from datetime import datetime, timedelta
from scripts.daily_summary import run as daily_summary
import json
import pytest
import io
import pytz
from pprint import pprint
from apps.subscriptions import views
from django.utils import timezone

def pytz_now():
    return timezone.now()

subscriptionView = views.SubscriptionViewSet.as_view({'get': 'list', 'post': 'create'})

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
            nickname = 'test',
            watched_address = "0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1",
            user = test_user,
            watch_token_transfers = True,
            network = scanner.network
        )

        # then process the transactions
        scanner.process_transactions(tx_list)

        # first we need to make subscription send the email...
        # then check if it got delivered
        # https://stackoverflow.com/a/3728594

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'test: Transaction Received')


    def test_summary_emails(self):
        scanner = TEST_SCANNER()
        tx_list = json.load(open('tests/transactions/block-5000015.json'))

        test_user = User.objects.create_user(username="audrey", email="test@audrey.com", password="audrey")
        
        # Create a subscription for an email address
        subscription = Subscription.objects.create(
            notify_email = test_user.email,
            watched_address = "0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1",
            user = test_user,
            watch_token_transfers = True,
            summary_notifications = True,
            network = scanner.network
        )

        # then process the transactions
        scanner.process_transactions(tx_list)
        today = pytz_now()
    
        subscription.transactions.all().update(created_at=today)

        daily_summary()
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, 'Notification Summary')

        two_days_ago = today - timedelta(days=2)
    
        subscription.transactions.all().update(created_at=two_days_ago)

        daily_summary()
        self.assertEqual(len(mail.outbox), 2, "Summary shouldn't be sent if no tx received today")


    def test_subscription_api(self):
        # Setup factory and user
        factory = APIRequestFactory()
        user = User.objects.create_user(username='audrey', password='testing')

        scanner = TEST_SCANNER()
        request = factory.get('/subscriptions/')
        force_authenticate(request, user=user)
        list_response = subscriptionView(request)
        self.assertEqual([], list_response.data['results'])

        request = factory.post('/subscriptions/', {
            'notify_email': 'audrey@test.com',
            'nickname': 'test',
            'watched_address': '0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1',
            'notify_url': 'https://webhook.site/cabfb6a8-714b-48b6-8138-78bda05fa9ff',
            'user': user.id,
            'watch_token_transfers': True,
            'network': scanner.network.id
        })
        force_authenticate(request, user=user)
        response = subscriptionView(request)     

        request = factory.get('/subscriptions/')
        force_authenticate(request, user=user)
        list_response = subscriptionView(request)
        self.assertEqual(1, list_response.data['count'])

        
        tx_list = json.load(open('tests/transactions/block-5000015.json'))
        scanner.process_transactions(tx_list)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'test: Transaction Received')
        self.assertEqual(SubscribedTransaction.objects.count(), 1)

        # print('You can visit this URL to see the webhook dump:')
        # print('https://webhook.site/#/cabfb6a8-714b-48b6-8138-78bda05fa9ff')

    def test_subscription_api_permissions(self):
        # Setup factory and user
        factory = APIRequestFactory()
        user1 = User.objects.create_user(username='audrey', password='testing')
        user2 = User.objects.create_user(username='lee', password='testing')

        scanner = TEST_SCANNER()
        Subscription.objects.create(
            watched_address = "0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1",
            user = user1,
            watch_token_transfers = True,
            network = scanner.network

        )

        request = factory.get('/subscriptions/')
        force_authenticate(request, user=user1)
        list_response = subscriptionView(request)
        self.assertEqual(1, len(list_response.data['results']))

        request = factory.get('/subscriptions/')
        force_authenticate(request, user=user2)
        list_response = subscriptionView(request)
        self.assertEqual(0, len(list_response.data['results']))

    def test_subscription_api_archiving(self):
        # Setup factory and user
        factory = APIRequestFactory()
        user = User.objects.create_user(username='lee', password='testing')
        scanner = TEST_SCANNER()
        Subscription.objects.create(
            watched_address = "0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1",
            archived_at=pytz_now() - timedelta(hours=1),
            user = user,
            watch_token_transfers = True,
            network = scanner.network
            
        )

        request = factory.get('/subscriptions/?show_archived=true')
        force_authenticate(request, user=user)
        list_response = subscriptionView(request)
        self.assertEqual(1, len(list_response.data['results']))

        request = factory.get('/subscriptions/')
        force_authenticate(request, user=user)
        list_response = subscriptionView(request)
        self.assertEqual(0, len(list_response.data['results']))

    def test_subscription_watched_tokens(self):
        test_user = User.objects.create_user(username="audrey", email="test@audrey.com", password="audrey")
        scanner = TEST_SCANNER()
        # Create a subscription for an email address
        subscription1 = Subscription.objects.create(
            notify_email = test_user.email,
            watched_address = "0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1",
            user = test_user,
            watch_token_transfers = False,
            network = scanner.network
        )

        self.assertEqual(0, subscription1.transactions.count())

        subscription2 = Subscription.objects.create(
            notify_email = test_user.email,
            watched_address = "0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1",
            user = test_user,
            watch_token_transfers = True,
            network = scanner.network
        )
        
        
        tx_list = json.load(open('tests/transactions/block-5000015.json'))
        scanner.process_transactions(tx_list)

        self.assertEqual(1, subscription2.transactions.count())

    def test_api_credit(self):
        test_user = User.objects.create_user(username="lee", email="test@lee.com", password="lee")

        self.assertEqual(1, test_user.api_credits.count())
        self.assertEqual(2500, test_user.current_credit_balance())

        scanner = TEST_SCANNER()

        subscription = Subscription.objects.create(
            notify_email = test_user.email,
            watched_address = "0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1",
            user = test_user,
            watch_token_transfers = True,
            network = scanner.network
        )
        
        tx_list = json.load(open('tests/transactions/block-5000015.json'))
        scanner.process_transactions(tx_list)

        self.assertEqual(1, subscription.transactions.count())
        self.assertEqual(2, test_user.api_credits.count())
        self.assertEqual(2499, test_user.current_credit_balance())

    def test_abi_methods(self):
        test_user = User.objects.create_user(username="audrey", email="test@audrey.com", password="audrey")
        scanner = TEST_SCANNER()
        # Create a subscription
        subscription = Subscription.objects.create(
            notify_email = test_user.email,
            watched_address = "0x86Fa049857E0209aa7D9e616F7eb3b3B78ECfdb0",
            user = test_user,
            watch_token_transfers = False,
            specific_contract_calls = True,
            abi_methods = 'transfer',
            network = scanner.network
        )

        scanner = TEST_SCANNER()
        tx_list = json.load(open('tests/transactions/block-5000015.json'))
        scanner.process_transactions(tx_list)

        self.assertEqual(4, subscription.transactions.count())
        
