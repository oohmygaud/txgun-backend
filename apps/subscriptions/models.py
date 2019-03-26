from .. import model_base
from django.db import models
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import json
import requests
import logging
from django.conf import settings

log = logging.getLogger('subscriptions')


class Subscription(model_base.NicknamedBase):
    objects = models.Manager()
    notify_email = models.CharField(max_length=128, null=True, blank=True)
    watched_address = models.CharField(max_length=64)
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING)
    notify_url = models.CharField(max_length=2048, null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    watch_token_transfers = models.BooleanField(default=False)
    summary_notifications = models.BooleanField(default=False)
    STATUS_CHOICES = [('active', 'active'), ('paused', 'paused')]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def found_transaction(self, tx):
        log.info('Found transaction: %s' % tx)
        if self.watch_token_transfers == False and tx['isToken']:
            log.debug(
                'Its a token transaction and we arent watching tokens, skip')
            return
        
        if self.status == 'paused':
            log.debug(
                'Subscription is paused, skipping transaction')
            return

        SubscribedTransaction.objects.create(
            subscription=self,
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
            token_to=tx.get('tokenTo', '')
        )

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


class SubscribedTransaction(models.Model):
    objects = models.Manager()
    created_at = models.DateTimeField(auto_now_add=True)
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
