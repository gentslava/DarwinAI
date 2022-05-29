# DarwinAI

## Запуск
Для запуска необходимо установить в виртуальное окружение пакеты из requirements.txt
(все команды вводятся из папки DarwinAI/DarwinAI) 
>pip install -r requirements_web.txt

Также необходимо наличие установленного PostgresSQL и настроек для подключения к базе в файле settings.py

	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.postgresql_psycopg2',
        		'NAME': '<имя базы данных>',
        		'USER': '<имя пользователя>',
        		'PASSWORD': '<пароль>',
        		'HOST': 'localhost', # ip сервера базы данных
        		'PORT': '5432',      # номер порта
    		}
	}

После настройки доступа к бд, необходимо провести миграции
>python manage.py migrate


Сервер разработки запускается из виртуального окружения 
>python manage.py runserver

После запуска клиентская часть доступна по адресу из консоли
Starting development server at http://127.0.0.1:8000/
Файл app/urls.py содержит доступные конечные точки

Приложение users содержит модель пользователя и методы для работы с ней: сериализатор и набор представлений.
Приложение app содержит остальные модели

## Функциональность
Функции-представления хранятся в модуле app/views.py. Они вызываются с помощью роутера в app/urls.py

>daphne -p 8001 DarwinAI.asgi:application

>uvicorn DarwinAI.asgi_prod:application --port 8001 --log-config log_config.yaml --workers 16 --reload

## Доступ к БД

Под админом:
>sudo -i -u postgres

Под пользователем БД:
>psql -h localhost -U bassist -d darwin

>Rfrfie4rf

Дамп:
>sudo su - postgres

>pg_dump darwin > darwin.sql

>cd /var/lib/postgresql

>sudo mv darwin.sql ~

>psql -d darwin -f darwin.sql
