# Generated by Django 3.2.5 on 2021-07-25 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0006_auto_20210725_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='call',
            name='start_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Начало разговора'),
        ),
    ]
