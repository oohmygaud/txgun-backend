# Generated by Django 2.0 on 2019-04-05 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0002_pricelookup'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricelookup',
            name='currency',
            field=models.CharField(default='USD', max_length=4),
        ),
    ]
