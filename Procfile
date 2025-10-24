web: gunicorn setup.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate --settings=setup.settings_render && python manage.py collectstatic --noinput --settings=setup.settings_render
