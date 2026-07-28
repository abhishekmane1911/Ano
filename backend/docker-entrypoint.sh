set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  sleep 1
done
echo "PostgreSQL is ready!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser if needed..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
# Check both email and username to avoid duplicate key errors
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists() and not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD'
    )
    print('Superuser created')
else:
    print('Superuser already exists')
EOF

if [ "$SERVER_TYPE" = "asgi" ]; then
    echo "Starting Daphne (ASGI) server..."
    exec daphne -b 0.0.0.0 -p 8001 ano_backend.asgi:application
else
    echo "Starting Gunicorn (WSGI) server..."
    exec gunicorn ano_backend.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers ${GUNICORN_WORKERS:-4} \
        --threads ${GUNICORN_THREADS:-2} \
        --timeout 120 \
        --access-logfile - \
        --error-logfile - \
        --log-level info
fi
