# Generated by Django 2.0 on 2019-05-22 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0007_auto_20190522_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribedtransaction',
            name='tx_hash',
            field=models.CharField(db_index=True, max_length=128),
        ),
    ]
