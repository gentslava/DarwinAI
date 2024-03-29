# Generated by Django 3.2 on 2021-07-12 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Call',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('script_matching', models.FloatField(null=True, verbose_name='Соответствие скрипту')),
                ('start_date', models.DateTimeField(auto_now=True, verbose_name='Начало разговора')),
            ],
        ),
        migrations.CreateModel(
            name='StopWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=150)),
                ('call', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='calls.call')),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record', models.FileField(null=True, upload_to='records/', verbose_name='Запись')),
                ('call', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='calls.call')),
            ],
        ),
        migrations.CreateModel(
            name='MandatoryQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Название кратко')),
                ('question', models.TextField(verbose_name='Вопрос')),
                ('call', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='calls.call')),
            ],
        ),
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel', models.CharField(max_length=15, null=True, verbose_name='Имя канала: "клиент", "оператор"')),
                ('start_speech', models.TimeField(null=True, verbose_name='Время начала фразы')),
                ('end_speech', models.TimeField(null=True, verbose_name='Время конца фразы')),
                ('text', models.TextField(default='', verbose_name='Распознанная фраза')),
                ('WPR', models.FloatField(default=0, verbose_name='Количество слов в секунду')),
                ('SPR', models.FloatField(default=0, verbose_name='Количество символов в секунду')),
                ('interception', models.IntegerField(default=0, verbose_name='Количество перебиваний')),
                ('loud_evaluation_avg', models.IntegerField(default=0, verbose_name='Оценка громкости [0: 10]')),
                ('result_loud', models.CharField(default='TOO QUIET', max_length=100, verbose_name='Текстовая оценка громкости')),
                ('negative', models.FloatField(default=0, verbose_name='Вероятность отрицательной эмоции')),
                ('neutral', models.FloatField(default=0, verbose_name='Вероятность нейтральной эмоции')),
                ('positive', models.FloatField(default=0, verbose_name='Вероятность положительной эмоции')),
                ('call', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='calls.call')),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calls', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='calls.call')),
            ],
        ),
        migrations.CreateModel(
            name='Advice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('call', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='calls.call')),
            ],
        ),
    ]
