# Generated by Django 5.1.3 on 2024-11-18 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0003_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customgroup',
            name='access',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='groupmember',
            name='role',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]