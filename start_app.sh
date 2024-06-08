#!/bin/bash

# Variables de entorno
DB_NAME="evalsdb"
DB_USER="admin"
DB_PASS="password"
DB_HOST="localhost"
DB_PORT="5432"
DJANGO_SUPERUSER_USERNAME="admin"
DJANGO_SUPERUSER_EMAIL="admin@example.com"
DJANGO_SUPERUSER_PASSWORD="adminpassword"

# Función para mostrar la ayuda
function show_help {
    echo "Uso: $0 [opciones]"
    echo
    echo "Opciones:"
    echo "  --setup              Configurar el entorno"
    echo "  --initial-data       Generar datos iniciales"
    echo "  --run-server         Iniciar el servidor usando Daphne"
    echo "  --run-django-server  Iniciar el servidor usando el servidor de desarrollo de Django"
    echo "  --import-qti         Importar datos QTI"
    echo "  --create-admin       Crear un usuario administrador de Django"
    echo "  --all                Realizar todas las acciones anteriores"
    echo "  --delete-db          Borrar la base de datos existente"
    echo "  --help               Mostrar esta ayuda"
    echo
    echo "Ejemplos:"
    echo "  $0 --setup"
    echo "  $0 --initial-data"
    echo "  $0 --run-server"
    echo "  $0 --all"
}

# Función para manejar errores
function handle_error {
    echo "Error: $1"
    exit 1
}

# Función para configurar el entorno
function setup_env {
    echo "Log start_app.sh: Configurando el entorno..."
    bash setup_env.sh || handle_error "Error configurando el entorno"
}

# Función para crear datos iniciales
function create_initial_data {
    echo "Log start_app.sh: Generando datos iniciales..."
    python create_initial_data.py || handle_error "Error generando datos iniciales"
}

# Función para importar datos QTI
function import_qti {
    echo "Log start_app.sh: Importando datos QTI..."
    python manage.py import_qti QTI_Bank || handle_error "Error importando datos QTI"
}

# Función para iniciar el servidor con Daphne
function run_server {
    echo "Log start_app.sh: Iniciando el servidor con Daphne..."
    daphne -e ssl:8000:privateKey=./localhost-key.pem:certKey=./localhost.pem asgi:application || handle_error "Error iniciando el servidor con Daphne"
}

# Función para iniciar el servidor de desarrollo de Django
function run_django_server {
    echo "Log start_app.sh: Iniciando el servidor de desarrollo de Django..."
    python manage.py runserver_plus --cert-file localhost.pem --key-file localhost-key.pem || handle_error "Error iniciando el servidor de desarrollo de Django"
}

# Función para crear un usuario administrador de Django
function create_admin_user {
    echo "Log start_app.sh: Creando usuario administrador de Django..."
    python manage.py createsuperuser --no-input || handle_error "Error creando usuario administrador de Django"
}

# Función para borrar y recrear la base de datos y el usuario
function delete_database {
    read -p "¿Está seguro de que desea borrar la base de datos existente? (s/n): " confirm
    if [[ $confirm =~ ^[Ss]$ ]]; then
        echo "Eliminando la base de datos existente..."
        dropdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME || handle_error "Error eliminando la base de datos"
        echo "Creando la base de datos y el usuario..."
        psql -c "DROP DATABASE IF EXISTS $DB_NAME;" || handle_error "Error eliminando la base de datos"
        psql -c "DROP USER IF EXISTS $DB_USER;" || handle_error "Error eliminando el usuario"
        psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" || handle_error "Error creando el usuario"
        psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" || handle_error "Error creando la base de datos"
        echo "Log start_app.sh: Base de datos y usuario creados exitosamente."
    else
        echo "Log start_app.sh: Operación cancelada. La base de datos no ha sido eliminada."
    fi
}

# Eliminar las funciones relacionadas con la verificación e inicio del servicio PostgreSQL
# function start_postgresql_service {
#     echo "Log start_app.sh: Iniciando el servicio PostgreSQL..."
#     service postgresql start || handle_error "Error iniciando el servicio PostgreSQL"
# }

# function check_postgresql_service {
#     if ! ps aux | grep "[p]ostgres" >/dev/null; then
#         echo "Log start_app.sh El servicio PostgreSQL no está en ejecución. Iniciando..."
#         start_postgresql_service
#     fi
# }

# Argumentos por defecto
SETUP=false
INITIAL_DATA=false
IMPORT_QTI=false
RUN_SERVER=false
RUN_DJANGO_SERVER=false
CREATE_ADMIN=false
DELETE_DB=false

# Interpretar argumentos de línea de comandos
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --setup) SETUP=true ;;
        --initial-data) INITIAL_DATA=true ;;
        --run-server) RUN_SERVER=true ;;
        --run-django-server) RUN_DJANGO_SERVER=true ;;
        --import-qti) IMPORT_QTI=true ;;
        --create-admin) CREATE_ADMIN=true ;;
        --all) SETUP=true; INITIAL_DATA=true; IMPORT_QTI=true; CREATE_ADMIN=true; RUN_SERVER=true ;;
        --delete-db) DELETE_DB=true ;;
        --help) show_help; exit 0 ;;
        *) echo "Opción desconocida: $1"; show_help; exit 1 ;;
    esac
    shift
done

# Eliminar la llamada a check_postgresql_service
# check_postgresql_service

# Ejecutar acciones basadas en los argumentos
if $SETUP; then
    setup_env
fi

if $DELETE_DB; then
    delete_database
fi

if $INITIAL_DATA; then
    create_initial_data
fi

if $IMPORT_QTI; then
    import_qti
fi

if $CREATE_ADMIN; then
    create_admin_user
fi

if $RUN_SERVER; then
    run_server
fi

if $RUN_DJANGO_SERVER; then
    run_django_server
fi

# Si no se especifica ningún argumento, se asume que se quiere realizar todo el proceso en orden específico
if ! $DELETE_DB && ! $SETUP && ! $INITIAL_DATA && ! $IMPORT_QTI && ! $CREATE_ADMIN && ! $RUN_SERVER && ! $RUN_DJANGO_SERVER; then
    delete_database
    setup_env
    create_initial_data
    import_qti
    create_admin_user
    run_server
fi
