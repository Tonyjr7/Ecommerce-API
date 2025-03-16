# Generated by Django 5.1.4 on 2025-01-21 18:16

import api.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_product_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image_url',
            field=models.ImageField(blank=True, null=True, upload_to=api.models.upload_to),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='api.category'),
        ),
    ]
