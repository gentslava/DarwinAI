# Generated by Django 3.2.5 on 2021-07-24 05:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calls', '0005_rename_calls_call'),
        ('users', '0002_alter_customuser_calls'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='calls',
        ),
        migrations.AddField(
            model_name='customuser',
            name='call',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='calls.call'),
        ),
    ]
