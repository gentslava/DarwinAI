# Generated by Django 3.2.5 on 2021-08-31 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0029_auto_20210831_0930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='status',
            field=models.CharField(default='Обрабатывается', max_length=255),
        ),
    ]
