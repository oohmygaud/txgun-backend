from .. import model_base
from django.db import models
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
import json

class Subscription(model_base.NicknamedBase) :
    notify_email = models.CharField(max_length=128, null=True, blank=True)
    notify_sms = models.CharField(max_length=128, null=True, blank=True)
    watched_address = models.CharField(max_length=64)
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING)

    def found_transaction(self, tx):
        print("subscription fired")
        if self.notify_email:
            print("sending email")
            send_mail(
                'Transaction Received',
                json.dumps(tx, indent=2),
                'noreply@txgun.io',
                [self.notify_email],
                fail_silently=False,
            )