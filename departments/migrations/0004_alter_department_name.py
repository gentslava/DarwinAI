# Generated by Django 3.2.8 on 2021-10-21 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0003_department_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='name',
            field=models.CharField(default='Не задан', max_length=255, unique=True),
        ),
    ]
