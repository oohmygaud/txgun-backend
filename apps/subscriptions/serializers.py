from .models import Subscription, SubscribedTransaction
from apps.users.models import CustomUser as User, APICredit, APIKey
from rest_framework import serializers
import re

from rest_registration.api.serializers import DefaultRegisterUserSerializer

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('__all__')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

class RegisterUserSerializer(DefaultRegisterUserSerializer):
    email = serializers.EmailField(required=True)

    def validate_username(self, username):
        if len(username) <= 3:
            raise serializers.ValidationError('Username must be more than 3 characters long')
        return username

    def validate_password(self, password):
        password = super(RegisterUserSerializer, self).validate_password(password)
        pattern = re.compile(r'^(?=.*[a-z])(?=.*\d)(?=.*[A-Z])(?:.{8,})$')
        if not pattern.match(password):
            raise serializers.ValidationError('Password must at least 8 characters long and contain an uppercase, lowercase, and number.')
        return password

class SubscribedTransactionSerializer(serializers.ModelSerializer):
    pricing_info = serializers.SerializerMethodField()
    token_info = serializers.SerializerMethodField()
    def get_pricing_info(self, obj):
        if not obj.price_lookup:
            return {}
        return {
            'price': obj.get_price(),
            'currency': obj.get_currency(),
            'fiat': obj.get_fiat(),
            'asset': obj.get_asset()
        }
    
    def get_token_info(self, obj):
        token = obj.get_token()
        
        if not token:
            return {}
        
        return {
            'symbol': token.symbol,
            'nickname': token.nickname,
            'decimal_places': token.decimal_places,
            'contract': token.contract.address
        }

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