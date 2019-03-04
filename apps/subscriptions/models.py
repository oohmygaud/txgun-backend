from .. import model_base
from django.db import models
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import json
import requests
import logging

log = logging.getLogger('subscriptions')

class Subscription(model_base.NicknamedBase):
    objects = models.Manager()
    notify_email = models.CharField(max_length=128, null=True, blank=True)
    watched_address = models.CharField(max_length=64)
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING)
    notify_url = models.CharField(max_length=2048, null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    watch_token_transfers = models.BooleanField(default=False)

    def found_transaction(self, tx):
        log.info('Found transaction: %s' % tx)        
        if self.watch_token_transfers == False and tx['isToken']:
            log.debug('Its a token transaction and we arent watching tokens, skip')
            return

        
        if self.notify_email:
            log.debug('Email TX Notification to %s'%self.notify_email)
            send_mail(
                'Transaction Received',
                json.dumps(tx, indent=2),
                'noreply@txgun.io',
                [self.notify_email],
                fail_silently=False,
            )

        if self.notify_url:
            log.debug('Webhook TX Notification to %s'%self.notify_url)
            r = requests.post(self.notify_url, data=tx)
            log.debug('Webhook response: %s'%r.content)


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
            token_amount=tx['tokenAmount'],
            token_to=tx['tokenTo']
        )
    class Meta:
        ordering = ('-created_at',)


class SubscribedTransaction(models.Model):
    objects = models.Manager()
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE,
                                     related_name='transactions')
    block_hash = models.TextField()
    block_number = models.CharField(max_length=64)
    from_address = models.CharField(max_length=64)
    gas = models.CharField(max_length=64)
    gas_price = models.CharField(max_length=64)
    tx_hash = models.TextField()
    tx_input = models.TextField()
    nonce = models.CharField(max_length=64)
    to_address = models.CharField(max_length=64)
    transaction_index = models.CharField(max_length=64)
    value = models.CharField(max_length=64)
    has_data = models.BooleanField()
    is_token = models.BooleanField()
    token_amount = models.CharField(max_length=64)
    token_to = models.CharField(max_length=64)
