# Generated by Django 3.2.6 on 2021-09-30 11:14

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0037_rename_client_words_customuser_client_pos_words'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='client_neg_words',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255, null=True), blank=True, default=list, size=None),
        ),
    ]