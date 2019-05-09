from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from uuid import uuid4
from .. import model_base
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail



class CustomUser(AbstractUser):
    STATUS_CHOICES = [('active', 'active'), ('paused', 'paused')]
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='active')
    default_notify_url = models.CharField(max_length=2048, blank=True, null=True)

    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)
        if(self.api_credits.count() == 0):
            self.api_credits.create(
                amount=settings.SIGNUP_BONUS_CREDITS,
                description='Signup Bonus Credits! Welcome!'
            )

    def current_credit_balance(self):
        return self.api_credits.aggregate(Sum('amount'))['amount__sum']

    def subtract_credit(self, amount, description):
        if self.current_credit_balance() < amount:
            self.status = 'paused'
            self.save()
            return False
        else:
            self.api_credits.create(
                amount=amount * -1, description=description)
            return True

    def add_monthly_credit(self):
        received = self.api_credits.filter(description__icontains='bonus credits')
        thirty_days = timezone.now()-timedelta(days=30)
        if received.filter(created_at__gte=thirty_days).count() == 0:
            self.api_credits.create(
                amount=settings.MONTHLY_BONUS_CREDITS,
                description='Monthly Bonus Credits!'
            )
    
    def low_credit_balance_email(self):
        if self.current_credit_balance() == 0:
            send_mail(
                'ZERO Credit Balance',
                "Warning! You're credit balance is zero. Please add more credit to your account to continue service.",
                'noreply@txgun.io',
                [self.email],
                fail_silently=False
            )
        elif self.current_credit_balance() <= 100:
            send_mail(
                'Low Credit Balance',
                "Warning! You're credit balance is low. Your current balance is " + self.current_credit_balance,
                'noreply@txgun.io',
                [self.email],
                fail_silently=True
            )
        
    

class APICredit(model_base.RandomPKBase):
    objects = models.Manager()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='api_credits')
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    description = models.CharField(max_length=128)

    class Meta:
        ordering = ('-created_at',)


def makeKey():
    return str(uuid4()).replace('-', '')


class APIKey(model_base.RandomPKBase):
    objects = models.Manager()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='api_keys')
    key = models.CharField(max_length=32, default=makeKey)
    archived_at = models.DateTimeField(null=True, blank=True)
    nickname = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    
