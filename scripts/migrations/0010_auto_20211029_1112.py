# Generated by Django 3.2.8 on 2021-10-29 04:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scripts', '0009_script_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='script',
            name='department_old',
        ),
        migrations.RemoveField(
            model_name='script',
            name='product_old',
        ),
    ]
