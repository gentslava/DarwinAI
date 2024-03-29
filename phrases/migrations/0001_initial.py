# Generated by Django 3.2.6 on 2021-10-05 07:09

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('scripts', '0002_auto_20211005_1336'),
    ]

    operations = [
        migrations.CreateModel(
            name='Phrase',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('text', models.CharField(max_length=255, null=True)),
                ('analogs', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(default=list, max_length=255), blank=True, default=list, size=None)),
                ('number', models.IntegerField(blank=True, null=True)),
                ('script', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='scripts.script')),
            ],
            options={
                'verbose_name': 'Фраза',
                'verbose_name_plural': 'Фразы',
            },
        ),
    ]
