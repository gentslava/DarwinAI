# Generated by Django 3.2.8 on 2021-10-26 00:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
        ('scripts', '0008_script_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='script',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.product'),
        ),
    ]
