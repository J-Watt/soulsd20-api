web: cd soulsd20api && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn soulsd20api.wsgi --bind 0.0.0.0:$PORT
