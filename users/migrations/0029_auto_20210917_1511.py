# Generated by Django 3.2.6 on 2021-09-17 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0028_customuser_critical_speed_podstr'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='critical_negative_emotions',
            new_name='critical_negative_emotions_client',
        ),
        migrations.AddField(
            model_name='customuser',
            name='critical_negative_emotions_operator',
            field=models.CharField(default='‒', max_length=255),
        ),
    ]