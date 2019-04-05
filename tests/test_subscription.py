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

def pytz_now():
    return datetime.now(pytz.utc)

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
            watched_address = "0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1",
            user = test_user,
            watch_token_transfers = True,
        )

        # then process the transactions
        scanner.process_transactions(tx_list)

        # first we need to make subscription send the email...
        # then check if it got delivered
        # https://stackoverflow.com/a/3728594

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Transaction Received')


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
        )

        # then process the transactions
        scanner.process_transactions(tx_list)

        daily_summary()
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, 'Notification Summary')

        two_days_ago = pytz_now() - timedelta(days=2)
    
        subscription.transactions.all().update(created_at=two_days_ago)

        daily_summary()
        self.assertEqual(len(mail.outbox), 2, "Summary shouldn't be sent if no tx received today")


    def test_subscription_api(self):
        # Setup factory and user
        factory = APIRequestFactory()
        user = User.objects.create_user(username='audrey', password='testing')

        request = factory.get('/subscriptions/')
        force_authenticate(request, user=user)
        list_response = subscriptionView(request)
        self.assertEqual([], list_response.data['results'])

        request = factory.post('/subscriptions/', {
            'notify_email': 'audrey@test.com',
            'watched_address': '0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1',
            'notify_url': 'https://webhook.site/cabfb6a8-714b-48b6-8138-78bda05fa9ff',
            'user': user.id,
            'watch_token_transfers': True
        })
        force_authenticate(request, user=user)
        response = subscriptionView(request)     

        request = factory.get('/subscriptions/')
        force_authenticate(request, user=user)
        list_response = subscriptionView(request)
        self.assertEqual(1, list_response.data['count'])

        scanner = TEST_SCANNER()
        tx_list = json.load(open('tests/transactions/block-5000015.json'))
        scanner.process_transactions(tx_list)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Transaction Received')
        self.assertEqual(SubscribedTransaction.objects.count(), 1)

        # print('You can visit this URL to see the webhook dump:')
        # print('https://webhook.site/#/cabfb6a8-714b-48b6-8138-78bda05fa9ff')

    def test_subscription_api_permissions(self):
        # Setup factory and user
        factory = APIRequestFactory()
        user1 = User.objects.create_user(username='audrey', password='testing')
        user2 = User.objects.create_user(username='lee', password='testing')

        Subscription.objects.create(
            watched_address = "0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1",
            user = user1,
            watch_token_transfers = True

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

        Subscription.objects.create(
            watched_address = "0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1",
            archived_at=pytz_now() - timedelta(hours=1),
            user = user,
            watch_token_transfers = True
            
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
        
        # Create a subscription for an email address
        subscription1 = Subscription.objects.create(
            notify_email = test_user.email,
            watched_address = "0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1",
            user = test_user,
            watch_token_transfers = False
        )

        self.assertEqual(0, subscription1.transactions.count())

        subscription2 = Subscription.objects.create(
            notify_email = test_user.email,
            watched_address = "0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1",
            user = test_user,
            watch_token_transfers = True
        )
        
        scanner = TEST_SCANNER()
        tx_list = json.load(open('tests/transactions/block-5000015.json'))
        scanner.process_transactions(tx_list)

        self.assertEqual(1, subscription2.transactions.count())

    def test_api_credit(self):
        test_user = User.objects.create_user(username="lee", email="test@lee.com", password="lee")

        self.assertEqual(1, test_user.api_credits.count())
        self.assertEqual(1000, test_user.current_credit_balance())

        subscription = Subscription.objects.create(
            notify_email = test_user.email,
            watched_address = "0x4D468cf47eB6DF39618dc9450Be4B56A70A520c1",
            user = test_user,
            watch_token_transfers = True
        )
        scanner = TEST_SCANNER()
        tx_list = json.load(open('tests/transactions/block-5000015.json'))
        scanner.process_transactions(tx_list)

        self.assertEqual(1, subscription.transactions.count())
        self.assertEqual(2, test_user.api_credits.count())
        self.assertEqual(999, test_user.current_credit_balance())

