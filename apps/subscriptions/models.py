from .. import model_base
from django.db import models
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import json
import requests
import logging
from django.conf import settings
from decimal import Decimal

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
    summary_notifications = models.BooleanField(default=False)
    include_pricing_data = models.BooleanField(default=False)
    specific_contract_calls = models.BooleanField(default=False)
    abi_methods = models.TextField(null=True, blank=True)
    STATUS_CHOICES = [('active', 'active'), ('paused', 'paused')]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def found_transaction(self, tx):
        from apps.contracts.models import PriceLookup, Contract
        log.info('Found transaction: %s' % tx)

        
        if self.status == 'paused':
            log.debug(
                'Subscription is paused, skipping transaction')
            return

        if tx['hasData'] and self.specific_contract_calls:
            contract = Contract.LOOKUP(tx['to'])
            print(tx['input'][:10], contract.abi)
            function = contract.get_web3_contract().get_function_by_selector(tx['input'][:10])
            if function.fn_name not in self.abi_methods.split(','):
                log.debug('Not watching this function: %s'%function.fn_name)
                return
        
        elif self.watch_token_transfers == False and tx['isToken']:
            log.debug(
                'Its a token transaction and we arent watching tokens, skip')
            return

        if SubscribedTransaction.objects.filter(tx_hash=tx['hash'], subscription=self):
            log.debug('Already seen this transaction before, skipping')
            return
        
        
        if not 'datetime' in tx:
            log.error('WHAT THE HELL GUY, NO DATETIME')
            return

        SubscribedTransaction.objects.create(
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
            price_lookup=self.include_pricing_data and PriceLookup.get_latest('ETH') or None
        )
        
        tx.pop('datetime', '') # not serializable

        if self.notify_url and self.user.subtract_credit(
                settings.NOTIFICATION_CREDIT_COST, 'Webhook Notification'):
            log.debug('Webhook TX Notification to %s' % self.notify_url)
            r = requests.post(self.notify_url, data=tx)
            log.debug('Webhook response: %s' % r.content)

        
        if self.notify_email and self.user.subtract_credit(
                settings.NOTIFICATION_CREDIT_COST, 'Email Notification'):
            log.debug('Email TX Notification to %s' % self.notify_email)
            send_mail(
                'Transaction Received',
                json.dumps(tx, indent=2),
                'noreply@txgun.io',
                [self.notify_email],
                fail_silently=False,
            )

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
