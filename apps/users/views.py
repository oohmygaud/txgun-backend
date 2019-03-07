from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.subscriptions.models import Subscription, SubscribedTransaction
from datetime import datetime, timedelta
from django.db.models import Sum
from apps.subscriptions.serializers import SubscribedTransactionSerializer, APICreditSerializer
from apps.users.models import APICredit
from rest_framework import generics

# Create your views here.


class Dashboard(APIView):
    def get(self, request, format=None):
        if not self.request.user.is_authenticated:
            return Response({'error': 'You are not logged in'}, status=401)

        my_subscriptions = Subscription.objects.filter(
            user=self.request.user).exclude(archived_at__lte=datetime.utcnow())

        my_transactions = SubscribedTransaction.objects.filter(
            subscription__user=self.request.user)

        yesterday = datetime.utcnow() - timedelta(days=1)

        my_transactions_today = my_transactions.filter(
            created_at__gte=yesterday)

        total_ether = my_transactions_today.aggregate(Sum('value'))[
            'value__sum']

        total_tokens = my_transactions_today.aggregate(Sum('token_amount'))[
            'token_amount__sum']

        return Response({
            'active_subcriptions': my_subscriptions.count(),
            'transactions_today': my_transactions_today.count(),
            'total_ether': total_ether or 0,
            'total_tokens': total_tokens or 0,
            'transactions': SubscribedTransactionSerializer(my_transactions[:10], many=True).data
        })

class MyAPICredits(APIView):
    def get(self, request, format=None):
        if not self.request.user.is_authenticated:
            return Response({'error': 'You are not logged in'}, status=401)

        total_credits = APICredit.objects.filter(user=self.request.user).aggregate(Sum('amount'))

        return Response({
            'api_credit_balance': total_credits or 0
        })

class APICreditList(generics.ListAPIView):
    serializer_class = APICreditSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return APICredit.objects.none()
        return APICredit.objects.filter(user=self.request.user)



