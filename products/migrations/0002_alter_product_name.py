# Generated by Django 3.2.8 on 2021-10-26 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(default='Не задан', max_length=255, unique=True),
        ),
    ]
