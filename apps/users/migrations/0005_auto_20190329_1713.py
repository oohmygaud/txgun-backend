# Generated by Django 2.0 on 2019-03-29 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_apikey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apicredit',
            name='amount',
            field=models.IntegerField(),
        ),
    ]
