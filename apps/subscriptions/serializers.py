from .models import Subscription, SubscribedTransaction
from django.contrib.auth.models import User
from rest_framework import serializers

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('__all__')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

class SubscribedTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscribedTransaction
        fields = ('__all__')