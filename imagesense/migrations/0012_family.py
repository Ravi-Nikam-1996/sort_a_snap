# Generated by Django 5.1.3 on 2024-11-14 06:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imagesense', '0011_alter_user_profile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='family',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='family_images/')),
                ('name', models.CharField(max_length=50)),
                ('relationship', models.CharField(help_text='Relationship to the user', max_length=50)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='family_members', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]