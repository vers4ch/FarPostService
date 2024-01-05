# Используйте официальный образ Python
FROM python:3.8

# Установите зависимости
RUN pip install Flask gunicorn psycopg2-binary SQLAlchemy flask_sqlalchemy

# Скопируйте код приложения в контейнер
COPY . /app
WORKDIR /app

# Определите переменные окружения
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5005

# Запустите приложение
CMD ["gunicorn", "-b", "0.0.0.0:5005", "app:app"]
