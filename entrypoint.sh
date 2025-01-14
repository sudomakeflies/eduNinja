#!/bin/sh

# Wait for the PostgreSQL database to be ready
'''until pg_isready -h db -p 5432 -U admin; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 1
done


# Generate migration files based on the models
python manage.py makemigrations

# Apply database migrations
python manage.py migrate

# Start the Django server
exec "$@"
'''

#!/bin/sh
set -e  # Detener el script si algún comando falla

# Esperar a que PostgreSQL esté listo
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h db -p 5432 -U admin; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Generar migraciones
echo "Generating migrations..."
python manage.py makemigrations

# Verificar si hay conflictos de migraciones
if python manage.py showmigrations | grep "conflict"; then
  echo "Conflicting migrations detected. Running makemigrations --merge..."
  python manage.py makemigrations --merge
fi

# Aplicar migraciones
echo "Applying migrations..."
python manage.py migrate

# Crear superusuario (si no existe)
echo "Creating superuser..."
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin') if not User.objects.filter(username='admin').exists() else None"

# Recopilar archivos estáticos (si es necesario)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Iniciar el servidor de Django
echo "Starting Django server..."
exec "$@"