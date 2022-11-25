![workflow status](https://github.com/IrinaPolt/stripe_project/actions/workflows/main.yml/badge.svg)
# stripe_project

 ### Описание проекта
 Тренировочный проект, направленный на изучение платежной системы stripe. Реализованы модели Item, Order, Tax и Discount. Оплата единичного товара доступна всем пользователям, добавление товаров в корзину и оплата заказа из нескольких товаров требуют регистрации

#### Детали
 Регистрация для сбора налогов была выбрана случайным образом для США, штат Техас (для тестирования функционала необходимо использовать подходящий адрес). Категория товаров для получения ставки налога выбрана случайным образом

### Шаблон наполнения .env файла для работы с базой данных

Создайте файл .env с переменными окружения для работы с базой данных:
```
DB_ENGINE=django.db.backends.postgresql <в проекте используется postgresql>
DB_NAME=<имя базы данных>
POSTGRES_USER=<логин для подключения к базе данных>
POSTGRES_PASSWORD=<пароль для подключения к БД>
DB_HOST=<название сервиса (контейнера)>
DB_PORT=<порт для подключения к БД>
STRIPE_PUBLIC_KEY=<ключ необходимо получить в панели управления stripe>
STRIPE_SECRET_KEY=<ключ необходимо получить в панели управления stripe>
STRIPE_WEBHOOK_SECRET = <ключ необходимо получить в панели управления stripe>
```
### Сборка и запуск приложения

```
docker-compose build
docker-compose up -d
```

### Выполнение миграций

```
docker-compose exec web python manage.py makemigrations items
docker-compose exec web python manage.py migrate
```

### Создание суперпользователя

```
docker-compose exec web python manage.py createsuperuser
```

### Сборка статики

```
docker-compose exec web python manage.py collectstatic --no-input
```
### Экспорт данных в файл

```
docker-compose exec web python manage.py dumpdata > fixtures.json
```

### Загрузка данных из файла

```
docker-compose exec web python manage.py loaddata fixtures.json
```

### Остановка приложения

```
docker-compose down
```

## http://51.250.84.171/
