# Generated by Django 2.0 on 2019-05-02 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0003_auto_20190412_2008'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='specific_contract_calls',
            field=models.BooleanField(default=False),
        ),
    ]