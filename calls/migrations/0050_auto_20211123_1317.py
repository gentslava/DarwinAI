# Generated by Django 3.2.8 on 2021-11-23 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0049_auto_20211115_0635'),
    ]

    operations = [
        migrations.AddField(
            model_name='call',
            name='debug_time_daiml_arrived',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='debug_time_daiml_sent',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='debug_time_uploaded',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='debug_time_wa_arrived',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='call',
            name='debug_time_wa_sent',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
