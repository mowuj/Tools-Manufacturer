# Generated by Django 3.2.12 on 2022-12-21 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toolsapp', '0011_order_paid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
