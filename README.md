# Project Title

## Description
A brief description of your project.

## Installation
To install the required packages, run the following command:
```
pip install -r requirements.txt
```

## Usage
Instructions for using the project.

## Contributing
Guidelines for contributing to the project.

## License
Information about the project's license.


# Переустановка проекта

## Python Django

Создайте виртуальную среду 
```
python -m venv venv
```

Активировать `venv`:
Windows:
```
source venv/Scripts/activate
```

Linux/Mac:
```
source venv/bin/activate
```

Перекинуть файл с зависимостями и использовать его:
```
pip install -r requirements.txt
```

Создать проект Django:
```
django-admin startproject conf .
```

Теперь перекинуть все рабочие приложения и конфигурацию.

Создать миграции:
```
python manage.py makemigrations
```

Применить миграции:
```
python manage.py migrate --run-syncdb
```

Создать для админ панели суперпользователя:
```
python manage.py createsuperuser
```

Запускаем сервер:
```
python manage.py runserver
```