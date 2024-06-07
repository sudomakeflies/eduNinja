#!/bin/bash

function show_help {
    echo "Uso: $0 [opciones]"
    echo
    echo "Opciones:"
    echo "  --setup              Configurar el entorno"
    echo "  --initial-data       Generar datos iniciales"
    echo "  --run-server         Iniciar el servidor usando Daphne"
    echo "  --run-django-server  Iniciar el servidor usando el servidor de desarrollo de Django"
    echo "  --import-qti         Importar datos QTI"
    echo "  --all                Realizar todas las acciones anteriores"
    echo "  --delete-db          Borrar la base de datos existente"
    echo "  --help               Mostrar esta ayuda"
}

function setup_env {
    echo "Configurando el entorno..."
    bash setup_env.sh
}

function create_initial_data {
    echo "Generando datos iniciales..."
    python create_initial_data.py
}

function import_qti {
    echo "Importando datos QTI..."
    python manage.py import_qti QTI_Bank
}

function run_server {
    echo "Iniciando el servidor con Daphne..."
    daphne -e ssl:8000:privateKey=./localhost-key.pem:certKey=./localhost.pem asgi:application
}

function run_django_server {
    echo "Iniciando el servidor de desarrollo de Django..."
    python manage.py runserver_plus --cert-file localhost.pem --key-file localhost-key.pem
}

# Función para borrar y recrear la base de datos y el usuario
function delete_database {
    read -p "¿Está seguro de que desea borrar la base de datos existente? (s/n): " confirm
    if [[ $confirm =~ ^[Ss]$ ]]; then
        echo "Eliminando la base de datos existente..."
        dropdb -h localhost -p 5432 -U sudomf posgresdb
        echo "Creando la base de datos y el usuario..."
        sudo -u postgres psql -c "DROP DATABASE IF EXISTS posgresdb;"
        sudo -u postgres psql -c "DROP USER IF EXISTS sudomf;"
        sudo -u postgres psql -c "CREATE USER sudomf WITH PASSWORD 'sudomakingflies';"
        sudo -u postgres psql -c "CREATE DATABASE posgresdb OWNER sudomf;"
        echo "Base de datos y usuario creados exitosamente."
    else
        echo "Operación cancelada. La base de datos no ha sido eliminada."
    fi
}

function start_postgresql_service {
    echo "Iniciando el servicio PostgreSQL..."
    sudo service postgresql start
}

function check_postgresql_service {
    if ! pgrep -x "postgres" >/dev/null; then
        echo "El servicio PostgreSQL no está en ejecución. Iniciando..."
        start_postgresql_service
    fi
}

# Argumentos por defecto
SETUP=false
INITIAL_DATA=false
IMPORT_QTI=false
RUN_SERVER=false
RUN_DJANGO_SERVER=false
DELETE_DB=false

# Interpretar argumentos de línea de comandos
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --setup) SETUP=true ;;
        --initial-data) INITIAL_DATA=true ;;
        --run-server) RUN_SERVER=true ;;
        --run-django-server) RUN_DJANGO_SERVER=true ;;
        --import-qti) IMPORT_QTI=true ;;
        --all) SETUP=true; INITIAL_DATA=true; IMPORT_QTI=true; RUN_SERVER=true ;;
        --delete-db) DELETE_DB=true ;;
        --help) show_help; exit 0 ;;
        *) echo "Opción desconocida: $1"; show_help; exit 1 ;;
    esac
    shift
done

# Verificar y comenzar el servicio PostgreSQL si es necesario
check_postgresql_service

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

if $RUN_SERVER; then
    run_server
fi

if $RUN_DJANGO_SERVER; then
    run_django_server
fi

# Si no se especifica ningún argumento, se asume que se quiere realizar todo el proceso en orden específico
if ! $DELETE_DB && ! $SETUP && ! $INITIAL_DATA && ! $IMPORT_QTI && ! $RUN_SERVER && ! $RUN_DJANGO_SERVER; then
    delete_database
    setup_env
    create_initial_data
    import_qti
    run_server
fi
