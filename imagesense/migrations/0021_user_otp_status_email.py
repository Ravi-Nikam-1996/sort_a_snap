# Generated by Django 5.1.3 on 2024-11-20 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imagesense', '0020_blacklistedtoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='otp_status_email',
            field=models.BooleanField(default=False),
        ),
    ]
