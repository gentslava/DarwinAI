# Generated by Django 3.2.5 on 2021-08-27 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_customuser_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
