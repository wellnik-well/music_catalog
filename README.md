[README.md](https://github.com/user-attachments/files/34626849/README.md)
# Каталог музыки (Django + PostgreSQL)

## 1. Подготовка базы данных
1. В DBeaver создайте подключение к PostgreSQL.
2. Создайте пустую базу данных `music_catalog` (ПКМ по «Databases» → Create → Database).

## 2. Установка
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Переменные окружения
Задайте значения из `.env.example` в своей среде (например, `export DB_PASSWORD=...`)
или впишите их в `config/settings.py` на время учёбы.

## 4. Миграции и запуск
```bash
python manage.py makemigrations catalog
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Сайт: http://127.0.0.1:8000/ , админка: http://127.0.0.1:8000/admin/

## 5. Импорт треков из CSV
Файл `tracks.csv` в кодировке UTF-8, первая строка — заголовки:
```
artist,album,year,title,track_number,duration,genre
Queen,A Night at the Opera,1975,Bohemian Rhapsody,11,5:55,Рок
```
Запуск: `python manage.py import_tracks tracks.csv`

## 6. Проверка в DBeaver
После `migrate` в схеме `public` появятся таблицы `catalog_artist`, `catalog_album`, `catalog_track`,
`catalog_genre`, `catalog_album_genres`, `catalog_playlist`, `catalog_playlisttrack`.
Внешние ключи и связи видны во вкладке ER-диаграммы.
