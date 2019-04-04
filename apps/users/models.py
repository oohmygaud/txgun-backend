from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from uuid import uuid4

# Create your models here.


class CustomUser(AbstractUser):
    STATUS_CHOICES = [('active', 'active'), ('paused', 'paused')]
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='active')

    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)
        if(self.api_credits.count() == 0):
            self.api_credits.create(
                amount=settings.SIGNUP_BONUS_CREDITS,
                description='Signup Bonus Credits! Welcome!')

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


class APICredit(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='api_credits')
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    description = models.CharField(max_length=128)


def makeKey():
    return str(uuid4()).replace('-', '')


class APIKey(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='api_keys')
    key = models.CharField(max_length=32, default=makeKey)
    archived_at = models.DateTimeField(null=True, blank=True)
    nickname = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
