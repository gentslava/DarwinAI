# Generated by Django 3.2.5 on 2021-08-03 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20210724_0524'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='call',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='calls_count',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='success',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
