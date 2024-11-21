# Generated by Django 5.1.3 on 2024-11-12 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imagesense', '0006_alter_user_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status'),
        ),
    ]