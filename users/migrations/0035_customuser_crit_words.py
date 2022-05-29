# Generated by Django 3.2.6 on 2021-09-29 15:19

import django.contrib.postgres.fields
from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_customuser_script_following'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='crit_words',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255, null=True), blank=True, default=users.models.default_par_words, size=None),
        ),
    ]
