# Generated by Django 5.0.6 on 2024-07-08 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0009_remove_user_bmi_alter_weightheightentry_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='send_reminders',
            field=models.BooleanField(default=True),
        ),
    ]