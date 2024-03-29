# Generated by Django 3.2.6 on 2021-09-13 16:41

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_alter_customuser_neg_words'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='neg_words',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255, null=True), blank=True, default=['щ', 'а', 'с', ',', ' ', 'ч', 'е', ',', ' ', 'э', ',', ' ', 'э', 'э', ',', ' ', 'э', 'э', 'э', ',', ' ', 'а', 'а', ',', ' ', 'а', 'а', 'а', ',', ' ', 'н', 'и', 'ч', 'е', ',', ' ', 'т', 'и', 'п', 'а', ',', ' ', 'н', 'у', ',', ' ', 'м', 'м', ',', ' ', 'м', 'м', 'м', ',', ' ', 'с', 'к', 'о', 'к', 'а', ',', ' ', 'н', 'и', 'с', 'к', 'о', 'к', 'а', ',', ' ', 'с', 'к', 'о', 'к', 'о', ',', ' ', 'н', 'и', 'с', 'к', 'о', 'к', 'о', ',', ' ', 'а', 'л', 'е', ',', ' ', 'з', 'д', 'р', 'а', 'с', 'ь', 'т', 'е'], size=None),
        ),
    ]
