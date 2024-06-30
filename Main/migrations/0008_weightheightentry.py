# Generated by Django 5.0.6 on 2024-06-30 14:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0007_workoutsession_curr_body_weight_alter_exercise_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeightHeightEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField()),
                ('height', models.FloatField()),
                ('date_recorded', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]