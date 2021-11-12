# YAMDB
### Описание
"Продуктовый помощник" это проект на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
### Технологии
- Python 3.7
- Django 2.2.6
- Django Rest Framework
- PostgreSQL
### Создайте файл .env и внесите настройки базы данных:
```
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
SECRET_KEY=... (установить свой)
```

### Клонирование проекта 
```
git clone git@github.com:Kirill1709/foodgram-project-react.git
```
### Запуск проекта
- Примените миграции
```bash
python manage.py migrate
``` 
- Создайте суперпользователя и введите данные
```bash
python manage.py createsuperuser
```
### Заполнение базы данных начальными данными
```bash
python manage.py loaddata ingredients.json
```
### Об авторе
##### Учебный проект студента ЯндексПрактикум 