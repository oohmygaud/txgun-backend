from .models import Subscription, SubscribedTransaction
from .serializers import SubscriptionSerializer, SubscribedTransactionSerializer
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework import generics
from datetime import datetime
from django_filters import rest_framework as filters
from rest_framework import viewsets
import pytz

class SubscriptionViewSet(viewsets.ModelViewSet):
    model = Subscription
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
    
    @action(detail=True, methods=['post'])
    def archive(self):
        instance = self.get_object()
        if not instance.archived_at:
            instance.archived_at = datetime.now(pytz.utc)
        instance.status = 'paused'
        instance.save()
        return Response(self.serializer_class(instance).data)
    
    @action(detail=True, methods=['post'])
    def unarchive(self):
        instance = self.get_object()
        instance.archived_at = None
        instance.save()
        return Response(self.serializer_class(instance).data)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        instance = self.get_object()
        instance.status = 'paused'
        instance.save()
        return Response(self.serializer_class(instance).data)

    @action(detail=True, methods=['post'])
    def unpause(self, request, pk=None):
        instance = self.get_object()
        instance.status = 'active'
        instance.save()
        return Response(self.serializer_class(instance).data)

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    model = SubscribedTransaction
    serializer_class = SubscribedTransactionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('subscription',)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return SubscribedTransaction.objects.none()
        return SubscribedTransaction.objects.filter(subscription__user=self.request.user)


