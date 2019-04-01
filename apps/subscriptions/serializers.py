from .models import Subscription, SubscribedTransaction
from apps.users.models import CustomUser as User, APICredit, APIKey
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

class APICreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = APICredit
        fields = ('__all__')

class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ('__all__')
        read_only = ('key',)