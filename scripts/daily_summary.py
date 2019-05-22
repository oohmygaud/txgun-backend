from .utils import safe_script
import logging
from apps.subscriptions.models import Subscription, SubscribedTransaction
from apps.subscriptions.serializers import SubscribedTransactionSerializer
scanlog = logging.getLogger('scanner')
from django.core.mail import EmailMessage
import json
from datetime import datetime, timedelta
import csv
from io import StringIO

@safe_script
def run():
    yesterday = datetime.utcnow()-timedelta(days=1)
    daily_summaries_enabled = Subscription.objects.filter(daily_notifications=True)
    for subscription in daily_summaries_enabled:
        summary = [SubscribedTransactionSerializer(s).data
                    for s in subscription.transactions.filter(
                        created_at__gte=yesterday)]

        if not len(summary):
            continue
        csvfile = StringIO()
        fieldnames = list(summary[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for tx in summary:
            writer.writerow(tx)
        
        email = EmailMessage(
            '%s: Daily Summary' % subscription.nickname,
            'Attached as csv',
            'noreply@txgun.io',
            [subscription.notify_email],
        )
        email.attach('file.csv', csvfile.getvalue(), 'text/csv')
        email.send()
        

            

