# Generated by Django 3.2.8 on 2021-11-24 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0055_auto_20211124_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='call',
            name='debug_time_calls_showing',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='debug_time_first_stats_showing',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='debug_time_postanalyze_spent',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]