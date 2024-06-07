#!/bin/bash

# Función para instalar dependencias
function install_dependencies {
    echo "Instalando dependencias..."
    pip install -r requirements.txt
}

# Función para migrar la base de datos
function migrate_database {
    # Verificar si la base de datos ya existe
    if ! psql -h localhost -p 5432 -U sudomf -lqt | cut -d \| -f 1 | grep -qw posgresdb; then
        # La base de datos no existe, crearla
        echo "Creando la base de datos posgresdb..."
        createdb -h localhost -p 5432 -U sudomf posgresdb
        echo "Base de datos creada exitosamente."
    fi

    echo "Migrando la base de datos..."
    python manage.py makemigrations
    python manage.py migrate
}


# Función para crear superusuario si no existe
function create_superuser {
    echo "Verificando si el superusuario ya existe..."
    if python manage.py shell -c "from django.contrib.auth.models import User; exit(0) if User.objects.filter(username='admin').exists() else exit(1)"; then
        echo "El superusuario 'admin' ya existe."
    else
        echo "Creando superusuario 'admin'..."
        python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')"
        echo "Superusuario 'admin' creado exitosamente."
    fi
}

# Ejecutar todas las funciones en orden
function setup_env {
    install_dependencies
    migrate_database
    create_superuser
}

# Ejecutar la configuración del entorno
setup_env
