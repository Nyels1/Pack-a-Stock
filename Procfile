web: gunicorn pack_a_stock_api.wsgi --log-file -
release: python manage.py migrate --noinput
worker: celery -A pack_a_stock_api worker --loglevel=info
beat: celery -A pack_a_stock_api beat --loglevel=info
