#!/bin/sh

set -e

# Variables de entorno
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"
DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-admin}"
DJANGO_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@example.com}"
DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-admin}"

# Función para manejar errores
handle_error() {
    echo "Error: $1" >&2
    exit 1
}

# Función para esperar que la base de datos esté disponible
wait_for_db() {
    echo "Esperando que la base de datos esté disponible..."
    while ! pg_isready -h $DB_HOST -p $DB_PORT -q; do
        sleep 1
    done
    echo "Base de datos disponible."
}

# Función para aplicar migraciones
apply_migrations() {
    echo "Aplicando migraciones..."
    python manage.py makemigrations
    python manage.py migrate
}

# Función para crear datos iniciales
create_initial_data() {
    echo "Generando datos iniciales..."
    python create_initial_data.py || handle_error "Error generando datos iniciales"
}

# Función para importar datos QTI
import_qti() {
    echo "Importando datos QTI..."
    python manage.py import_qti QTI_Bank || handle_error "Error importando datos QTI"
}

# Función para crear un superusuario si no existe
create_superuser() {
    echo "Creando superusuario si no existe..."
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@eduninja.co', 'admin')
    print("Superusuario creado.")
else:
    print("El superusuario ya existe.")
EOF
}

# Función principal
main() {
    wait_for_db
    apply_migrations
    create_initial_data
    import_qti
    create_superuser
    echo "Iniciando servidor Django..."
    python manage.py runserver 0.0.0.0:8000
}

# Ejecutar la función principal
main