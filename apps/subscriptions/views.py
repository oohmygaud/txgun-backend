from .models import Subscription
from django.contrib.auth.models import User
from .serializers import SubscriptionSerializer, UserSerializer
from .permissions import IsOwner
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework import generics

class SubscriptionList(generics.ListCreateAPIView):
    permission_classes = (IsOwner,)
    serializer_class = SubscriptionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Subscription.objects.none()
        return Subscription.objects.filter(user=self.request.user)

class SubscriptionDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsOwner,)
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

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'subscriptions': reverse('subscription-list', request=request, format=format)
    })