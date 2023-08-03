# Foodgram

![N](https://logodix.com/logo/72187.jpg)
  

### Продуктовый помощник - Foodgram
#### Поможет найти или поделиться рецептом
____
# Запуск проекта
##### В папке infra выполните команду docker-compose up.
##### Проект запустится на адресе http://localhost, увидеть спецификацию API вы сможете по адресу http://localhost/api/docs/
____


### Как запустить проект

* Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Vichynaa/foodgram-project-react
```

```
cd foodgram-project-react
```

* Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

```
source venv/bin/activate
```

* Если у вас windows

```
source venv/scripts/activate
```

```
python3 -m pip install --upgrade pip
```

* Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

* Выполнить миграции:

```
python3 manage.py migrate
```

* Запустить проект:

```
python3 manage.py runserver
```
--------
# Импорт данных
```
python3 manage.py load_csv
```
-------

# Технологии
* Python 3.9
* Django 3.2
* Django Rest Framework 3.12.4
* Simple-JWT 4.7.2
* GitHub
* Postman
* Redoc
----------
