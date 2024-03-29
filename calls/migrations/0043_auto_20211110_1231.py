# Generated by Django 3.2.8 on 2021-11-10 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0042_call_script_following_norm'),
    ]

    operations = [
        migrations.AddField(
            model_name='call',
            name='crit_words',
            field=models.CharField(default='-', max_length=255),
        ),
        migrations.AddField(
            model_name='call',
            name='neg_client',
            field=models.CharField(default='-', max_length=255),
        ),
        migrations.AddField(
            model_name='call',
            name='neg_operator',
            field=models.CharField(default='-', max_length=255),
        ),
        migrations.AddField(
            model_name='call',
            name='neg_words',
            field=models.CharField(default='-', max_length=255),
        ),
        migrations.AddField(
            model_name='call',
            name='pos_client',
            field=models.CharField(default='-', max_length=255),
        ),
        migrations.AddField(
            model_name='call',
            name='pos_operator',
            field=models.CharField(default='-', max_length=255),
        ),
    ]
