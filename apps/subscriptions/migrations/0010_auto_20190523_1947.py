# Generated by Django 2.0 on 2019-05-23 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0009_auto_20190523_1940'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='realtime_emails',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='subscription',
            name='realtime_webhooks',
            field=models.BooleanField(default=False),
        ),
    ]
