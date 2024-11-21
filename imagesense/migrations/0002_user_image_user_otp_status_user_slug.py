# Generated by Django 5.1.3 on 2024-11-12 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imagesense', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.BinaryField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='otp_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
