# Generated by Django 5.1.3 on 2024-11-14 06:59

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imagesense', '0013_alter_family_relationship'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='family',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
