# Generated by Django 3.1.1 on 2020-09-17 17:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0003_customer_data_created'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='data_created',
        ),
    ]
