# Generated by Django 2.0 on 2019-03-04 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0003_subscribedtransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='archived_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
