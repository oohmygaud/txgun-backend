from .models import Subscription
from django.contrib.auth.models import User
from rest_framework import serializers

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('notify_email', 'notify_sms', 'watched_address', 'user')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')