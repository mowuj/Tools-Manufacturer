# Generated by Django 4.1.4 on 2022-12-19 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toolsapp', '0002_product_minimum_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='discount',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
