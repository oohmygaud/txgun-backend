from .models import Subscription, SubscribedTransaction
from .serializers import SubscriptionSerializer, UserSerializer, SubscribedTransactionSerializer
from .permissions import IsOwner
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework import generics
from datetime import datetime
from django_filters import rest_framework as filters
from apps.users.models import CustomUser as User


class SubscriptionList(generics.ListCreateAPIView):
    serializer_class = SubscriptionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('notify_email',
                        'watched_address',
                        'notify_url',
                        'archived_at',
                        'watch_token_transfers',
                        'summary_notifications')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Subscription.objects.none()
        qs = Subscription.objects.filter(user=self.request.user)

        if self.request.query_params.get('show_archived', '').lower() != 'true':
            qs = qs.exclude(archived_at__lte=datetime.utcnow())

        return qs


class SubscriptionDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Subscription.objects.none()
        return Subscription.objects.filter(user=self.request.user)


class UserList(generics.ListAPIView):
    permission_classes = (IsOwner,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    permission_classes = (IsOwner,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TransactionList(generics.ListAPIView):
    serializer_class = SubscribedTransactionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('subscription',)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return SubscribedTransaction.objects.none()
        return SubscribedTransaction.objects.filter(subscription__user=self.request.user)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'subscriptions': reverse('subscription-list', request=request, format=format)
    })
