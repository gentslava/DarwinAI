# Generated by Django 3.2.6 on 2021-09-13 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0032_auto_20210913_2304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='interseptions',
            field=models.CharField(default='-', max_length=255),
        ),
        migrations.AlterField(
            model_name='call',
            name='volume',
            field=models.CharField(default='-', max_length=255),
        ),
    ]
