# Generated by Django 5.1.3 on 2024-11-15 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imagesense', '0018_alter_contactus_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactus',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
    ]
