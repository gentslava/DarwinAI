# Generated by Django 3.2.6 on 2021-09-13 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0031_alter_call_start_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='call',
            options={'verbose_name': 'Звонок', 'verbose_name_plural': 'Звонки'},
        ),
        migrations.AlterField(
            model_name='call',
            name='volume',
            field=models.CharField(default='‒', max_length=255),
        ),
    ]
