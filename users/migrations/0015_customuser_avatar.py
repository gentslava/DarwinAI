# Generated by Django 3.2.5 on 2021-08-23 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_auto_20210822_0534'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='avatar',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
