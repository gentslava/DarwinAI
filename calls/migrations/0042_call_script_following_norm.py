# Generated by Django 3.2.8 on 2021-11-08 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0041_auto_20211108_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='call',
            name='script_following_norm',
            field=models.CharField(default='-', max_length=255),
        ),
    ]