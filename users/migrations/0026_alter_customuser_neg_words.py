# Generated by Django 3.2.6 on 2021-09-13 16:43

import django.contrib.postgres.fields
from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_alter_customuser_neg_words'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='neg_words',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255, null=True), blank=True, default=users.models.default_par_words, size=None),
        ),
    ]
