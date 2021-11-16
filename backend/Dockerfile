FROM python:3.8.5

WORKDIR /code

COPY . .

RUN pip install -r requirements.txt && \
    python manage.py collectstatic --no-input

CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000