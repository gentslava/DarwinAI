# Generated by Django 3.2.8 on 2021-10-21 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=255, null=True, unique=True),
        ),
    ]
