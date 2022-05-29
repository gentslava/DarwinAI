# Generated by Django 3.2.8 on 2021-11-14 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0048_call_script_statistics'),
    ]

    operations = [
        migrations.AddField(
            model_name='call',
            name='critical_crit_words',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='call',
            name='critical_emotional_negative_client',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='call',
            name='critical_emotional_negative_operator',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='call',
            name='critical_interceptions',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='call',
            name='critical_loud_control',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='call',
            name='critical_neg_words',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='call',
            name='critical_script_following',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='call',
            name='critical_speech_purity',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='call',
            name='critical_speed_control',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='call',
            name='critical_volume',
            field=models.BooleanField(default=False),
        ),
    ]