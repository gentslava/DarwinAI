# Generated by Django 3.2.6 on 2021-09-16 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0036_alter_call_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='call',
            name='critical',
            field=models.BooleanField(default=False),
        ),
    ]