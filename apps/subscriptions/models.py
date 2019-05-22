from .. import model_base
from django.db import models
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import json
import requests
import logging
from django.conf import settings
from decimal import Decimal
from apps.networks.models import MAIN_NETWORK
from apps.metrics import count_metrics

log = logging.getLogger('subscriptions')
log.setLevel(logging.DEBUG)


class Subscription(model_base.NicknamedBase):
    objects = models.Manager()
    notify_email = models.CharField(max_length=128, null=True, blank=True)
    watched_address = models.CharField(max_length=64)
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING)
    notify_url = models.CharField(max_length=2048, null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    watch_token_transfers = models.BooleanField(default=False)
    daily_notifications = models.BooleanField(default=False)
    monthly_notifications = models.BooleanField(default=False)
    include_pricing_data = models.BooleanField(default=False)
    specific_contract_calls = models.BooleanField(default=False)
    abi_methods = models.TextField(null=True, blank=True)
    network = models.ForeignKey(
        "networks.Network", null=True, on_delete=models.DO_NOTHING)
    STATUS_CHOICES = [('active', 'active'), ('paused', 'paused')]
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='active')

    def found_transaction(self, tx):
        from apps.contracts.models import PriceLookup, Contract
        # Too noisy, getting expensive
        #log.info('Found transaction: %s' % tx)

        if self.status == 'paused':
            log.debug(
                'Subscription is paused, skipping transaction')
            count_metrics('tx.subscription_paused', {
                          'network': self.network.nickname})
            return

        if tx['hasData'] and self.specific_contract_calls:
            contract = Contract.LOOKUP(tx['to'])
            function = contract.get_web3_contract(
            ).get_function_by_selector(tx['input'][:10])
            if function.fn_name not in self.abi_methods.split(','):
                log.debug('Not watching this function: %s' % function.fn_name)
                count_metrics('tx.function_not_watched', {
                              'network': self.network.nickname})
                return

        elif self.watch_token_transfers == False and tx['isToken']:
            log.debug(
                'Its a token transaction and we arent watching tokens, skip')
            count_metrics('tx.tokens_not_watched', {
                          'network': self.network.nickname})
            return

        if SubscribedTransaction.objects.filter(tx_hash=tx['hash'], subscription=self):
            log.debug('Already seen this transaction before, skipping')
            count_metrics('tx.duplicate_transaction', {
                          'network': self.network.nickname})
            return

        if not 'datetime' in tx:
            log.error('WHAT THE HELL GUY, NO DATETIME')
            count_metrics('tx.error_missing_datetime', {
                          'network': self.network.nickname})
            return

        price_info = self.include_pricing_data and PriceLookup.get_latest(
            'ETH') or None

        stx = SubscribedTransaction.objects.create(
            subscription=self,
            created_at=tx['datetime'],
            block_hash=tx['blockHash'],
            block_number=tx['blockNumber'],
            from_address=tx['from'],
            gas=tx['gas'],
            gas_price=tx['gasPrice'],
            tx_hash=tx['hash'],
            tx_input=tx['input'],
            nonce=tx['nonce'],
            to_address=tx['to'],
            transaction_index=tx['transactionIndex'],
            value=tx['value'],
            has_data=tx['hasData'],
            is_token=tx['isToken'],
            token_amount=tx.get('tokenAmount', 0),
            token_to=tx.get('tokenTo', ''),
            price_lookup=price_info
        )

        tx.pop('datetime', '')  # not serializable

        output = {
            'transaction': stx.serialize(),
            'subscription': self.serialize()
        }

        if self.notify_url and self.user.subtract_credit(
                settings.NOTIFICATION_CREDIT_COST, 'Webhook Notification'):
            log.debug('Webhook TX Notification to %s' % self.notify_url)
            try:
                r = requests.post(self.notify_url, data=output)
                log.debug('Webhook response: %s' % r.content)
                count_metrics('tx.notify_webhook_success', {
                              'network': self.network.nickname})
            except Exception as e:
                count_metrics('tx.notify_webhook_error', {
                              'network': self.network.nickname})

        if self.notify_email and self.user.subtract_credit(
                settings.NOTIFICATION_CREDIT_COST, 'Email Notification'):
            log.debug('Email TX Notification to %s' % self.notify_email)
            try:
                send_mail(
                    '%s: Transaction Received' % self.nickname,
                    json.dumps(output, indent=2),
                    'noreply@txgun.io',
                    [self.notify_email],
                )
                count_metrics('tx.notify_email_success', {
                              'network': self.network.nickname})
            except Exception as e:
                count_metrics('tx.notify_email_error', {
                              'network': self.network.nickname})

    def serialize(self):
        from .serializers import SubscriptionSerializer
        return SubscriptionSerializer(self).data

    class Meta:
        ordering = ('-created_at',)


class SubscribedTransaction(model_base.RandomPKBase):
    objects = models.Manager()
    created_at = models.DateTimeField()
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE,
                                     related_name='transactions')
    block_hash = models.TextField()
    block_number = models.PositiveIntegerField()
    from_address = models.CharField(max_length=64)
    gas = models.PositiveIntegerField()
    gas_price = models.DecimalField(max_digits=50, decimal_places=0)
    tx_hash = models.TextField()
    tx_input = models.TextField()
    nonce = models.PositiveIntegerField()
    to_address = models.CharField(max_length=64)
    transaction_index = models.PositiveIntegerField()
    value = models.DecimalField(max_digits=50, decimal_places=0)
    has_data = models.BooleanField()
    is_token = models.BooleanField()
    token_amount = models.DecimalField(max_digits=50, decimal_places=0)
    token_to = models.CharField(max_length=64)
    price_lookup = models.ForeignKey('contracts.PriceLookup',
                                     null=True, blank=True, on_delete=models.DO_NOTHING)

    def serialize(self):
        from .serializers import SubscribedTransactionSerializer
        return SubscribedTransactionSerializer(self).data

    def get_pricing_info(self):
        if self.price_lookup:
            return {
                'price': self.get_price(),
                'currency': self.get_currency(),
                'fiat': self.get_fiat(),
                'asset': self.get_asset()
            }

    def get_price(self):
        if self.price_lookup:
            return self.price_lookup.price

    def get_asset(self):
        if self.price_lookup:
            return self.price_lookup.asset

    def get_currency(self):
        if self.price_lookup:
            return self.price_lookup.currency

    def get_fiat(self):
        if self.price_lookup and self.value:
            return self.price_lookup.price * self.value/Decimal(10E18)

    def get_token(self):
        from apps.contracts.models import ERC20
        if not self.is_token:
            return None
        try:
            return ERC20.objects.get(contract__address=self.to_address)
        except ERC20.DoesNotExist:
            return None

    class Meta:
        ordering = ('-created_at',)
