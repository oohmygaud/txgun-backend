# Generated by Django 2.0 on 2019-06-28 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0012_auto_20190620_2000'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscribedtransaction',
            name='parameters_json',
            field=models.TextField(blank=True, null=True),
        ),
    ]
