# Generated by Django 5.0.6 on 2024-07-17 13:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0010_profile_send_reminders'),
    ]

    operations = [
        migrations.AlterField(
            model_name='set',
            name='exercise',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='Main.exercise'),
        ),
    ]
