# Generated by Django 3.2.8 on 2021-10-21 06:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('departments', '0002_remove_department_manager'),
        ('users', '0043_customuser_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='departments.department'),
        ),
    ]
