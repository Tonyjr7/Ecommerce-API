# Generated by Django 5.1.4 on 2025-01-21 20:15

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_user_image_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='image_url',
        ),
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=api.models.upload_to),
        ),
    ]
