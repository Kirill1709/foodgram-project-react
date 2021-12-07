# FOODGRAM PROJECT
### Описание
"Продуктовый помощник" это проект на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
### Технологии
- Python 3.7
- Django 2.2.6
- Django Rest Framework
- PostgreSQL
- Docker
- Nginx
- Github action

### Зайдите на сервер и клонируйте проект 
```
ssh username@host
git clone git@github.com:Kirill1709/foodgram-project-react.git
```
### Создайте файл .env и внесите настройки базы данных:
```
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
SECRET_KEY=... (установить свой)
LOCAL_HOSTS=...
DEBUG=...
```

#### Для удобства, скопируйте docker-compose.yml и nginx.conf в корневой каталог. Зайдите в папку infra и выполните:
```
cp docker-compose.yml nginx.conf ~
```
### Запустите проект
```bash
docker-compose up -d --build
```
- Примените миграции
```bash
docker-compose exec backend python manage.py migrate --noinput
``` 
- Создайте суперпользователя и введите данные
```bash
docker-compose exec backend python manage.py createsuperuser
```
### Заполнение базы данных начальными данными
```bash
docker-compose exec backend python manage.py loaddata db.json
```
##### Проект запущен, теперь перейдем к настроке репозитория проекта на github
### Внесите secrets в github actions в разделе settings -> Secrets:
- DOCKER_PASSWORD - пароль от DockerHub;
- DOCKER_USERNAME - имя пользователя на DockerHub;
- HOST - ip-адрес сервера;
- SSH_KEY - приватный ssh ключ;
##### Теперь при изменении в репозитории, обновленный проект будет автоматически разворачиваться на сервере 
### Об авторе
##### Учебный проект студента ЯндексПрактикум 
##### [Ссылка на github](https://github.com/Kirill1709)
### Сайт
##### [Foodgram](http://84.252.140.108/)
### Доступ в админ панель
```
login: admin@yandex.ru
password: admin
```
