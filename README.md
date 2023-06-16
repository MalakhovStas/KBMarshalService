# КБ Маршал сервис
Внутренний сервис компании Маршал для работы с информациео о должниках

## Как установить
Для работы микросервиса нужен Python версии не ниже 3.10 и установленное ПО для контейнеризации - [Docker](https://docs.docker.com/engine/install/).    

Настройка переменных окружения  
1. Скопируйте файл .env.dist в .env
2. Заполните .env файл. Пример:  
```yaml
DATABASE_URL = postgresql://skillbox:secret@127.0.0.1:5434/market
REDIS_URL = redis://127.0.0.1:6379/0
```

Запуск СУБД Postgresql
```shell
docker run --name skillbox-db -e POSTGRES_USER=skillbox -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=market -p 5434:5432 -d postgres
```
Запуск брокера сообщений REDIS
```shell
docker run --name redis-db -p 6379:6379 -d redis 
```
Установка виртуального окружения для среды разработки на примере ОС Windows
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements\dev.txt
```
Установка виртуального окружения для продовой среды на примере ОС Linux
```shell
python -m venv venv
. venv/bin/activate
pip install -r requirements/base.txt
```  
### Как удалить контейнеры
СУБД Postgres  
```
 docker rm -f -v skillbox-db
```

Брокер сообщений REDIS  
```
 docker rm -f -v skillbox-db
```

## Проверка форматирования кода
Проверка кода выполняется из корневой папки репозитория.    
* Анализатор кода flake8  
```shell
flake8
```
* Линтер pylint  
```shell
pylint --rcfile=.pylintrc market/* 
```

## Как запустить web-сервер
Запуск сервера производится в активированном локальном окружение из папки `market/`
```shell
python manage.py runserver 0.0.0.0:8000
```

## Разработка
### Работа в оболочке
```shell
python manage.py shell_plus
```
### Приложение users:

Загрузка данных в модель User выполняется из папки `market/` следующей командой:

```shell
python manage.py loaddata fixtures/005_users.json --app users.User
```

#### Данные cуперпользователя:

email: admin@admin.ru password: admin

#### Данные зарегистрированных пользователей:

1. email: david@test.ru password: 1304test
2. email: kevin@test.ru password: 1304test
3. email: robert@test.ru password: 1304test
4. email: skott@test.ru password: 1304test

#### Данные зарегистрированных пользователей, у которых есть магазин:

1. email: kenneth@test.ru password: 1304test
2. email: willard@test.ru password: 1304test
3. email: kyle@test.ru password: 1304test
4. email: glenn@test.ru password: 1304test
5. email: keith@test.ru password: 1304test  

#### Данные для доступа к серверной электронной почте:

email: service.megano@gmail.com password: 2023Django

### Приложение imports:

Команды для выполнения импорта:

- выполнения импорта всех файлов
````shell
python manage.py imports all
````
- выполнения импорта одного файла
````shell
python manage.py imports <имя файла>
````
- выполнения импорта нескольких файлов
````shell
python manage.py imports <имена файлов через пробел>
````

#### CELERY

Также импорт можно поставить на периодическое выполнение задачи.
Для настройки времени периодов выполнения задач необходимо задать требуемые параметры 
в админ панели, подробнее можно посмотреть в статье [Сергея Климова](https://habr.com/ru/articles/711590/).

Команды запуска выполнения задач в фоновом режиме:

- Запуск брокера сообщений Redis
````shell
redis-server
````
- Запуск Celery для выполнения задачи по импорту
````shell
celery -A config worker -l info
````
- Запускаем службу beat
````shell
celery -A config beat -l info
````
- Запускаем сервер
````shell
python manage.py runserver
````