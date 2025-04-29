# Social Network API (Django REST Framework)

## Описание проекта
RESTful API для социальной сети с возможностью:
- Создания постов с текстом и изображениями
- Комментирования постов
- Лайков постов

## Технологии
- Python 3.9+
- Django 4.0+
- Django REST Framework 3.14+
- PostgreSQL (рекомендуется) / SQLite

## Установка

1. Клонировать репозиторий:
```bash
git clone https://github.com/Cherletskiy/social_network_drf_diplom.git
```

2. Создать и активировать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Настройка базы данных (для PostgreSQL):
```bash
# Создать БД в PostgreSQL
# Обновить настройки в settings.py:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'имя_БД',
        'USER': 'пользователь',
        'PASSWORD': 'пароль',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

5. Применить миграции:
```bash
cd social_network
python manage.py migrate
```

6. Создать суперпользователя:
```bash
python manage.py createsuperuser
```

## Запуск сервера
```bash
python manage.py runserver
```

## API Endpoints

- `GET /api/posts/` — список постов
- `GET /api/posts/{id}/` — детали поста
- `POST /api/posts/` — создать пост *(только для авторизованных)*
- `POST /api/posts/{id}/like/` — лайк / дизлайк поста *(только для авторизованных)*
- `GET/POST /api/posts/{id}/comments/` — комментарии к посту *(только для авторизованных)*


## Примеры запросов

### Запросы для проверки находятся в файле `requests.http`

### Создание поста с изображениями
```http
POST {{HOST}}/api/posts/
Authorization: Token {{TOKEN}}
Content-Type: multipart/form-data; boundary=WebAppBoundary

--WebAppBoundary
Content-Disposition: form-data; name="text"

Новый пост!!!
--WebAppBoundary
Content-Disposition: form-data; name="location"

45.05515709416117, 39.01727907829566
--WebAppBoundary
Content-Disposition: form-data; name="images"; filename="photo3.jpg"
Content-Type: image/jpeg

< ./media/post_images/photo3.jpg
--WebAppBoundary
Content-Disposition: form-data; name="images"; filename="gif1.gif"
Content-Type: image/gif

< ./media/post_images/gif1.gif
--WebAppBoundary--
```

### Обновление поста (замена изображений)
```http
PATCH /api/posts/3/
Content-Type: multipart/form-data; boundary=WebAppBoundary
Authorization: Token ваш_токен

--WebAppBoundary
Content-Disposition: form-data; name="images"; filename="new_photo.jpg"
Content-Type: image/jpeg

< ./new_photo.jpg
--WebAppBoundary--
```

## Настройки
Основные настройки можно изменить в файле `settings.py`:
- `MEDIA_ROOT` - Папка для загружаемых файлов
- `MEDIA_URL` - URL для доступа к медиафайлам
- `PAGE_SIZE` - Количество постов на странице
