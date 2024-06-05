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
    echo "  --delete-db          Borrar la base de datos existente (db.sqlite3)"
    echo "  --help               Mostrar esta ayuda"
}

function setup_env {
    echo "Configurando el entorno..."
    bash setup_env.sh
}

function create_initial_data {
    echo "Generando datos iniciales..."
    python3 create_initial_data.py
}

function import_qti {
    echo "Importando datos QTI..."
    python3.10 manage.py import_qti QTI_Bank
}

function run_server {
    echo "Iniciando el servidor con Daphne..."
    daphne -e ssl:8000:privateKey=./localhost-key.pem:certKey=./localhost.pem asgi:application
}

function run_django_server {
    echo "Iniciando el servidor de desarrollo de Django..."
    python3 manage.py runserver_plus --cert-file localhost.pem --key-file localhost-key.pem
}

function delete_db {
    if [ -f "db.sqlite3" ]; then
        read -p "¿Está seguro de que desea eliminar db.sqlite3? (s/n): " confirm
        if [[ $confirm == [sS] ]]; then
            rm db.sqlite3
            echo "Base de datos db.sqlite3 eliminada."
        else
            echo "Operación cancelada."
        fi
    else
        echo "No se encontró la base de datos db.sqlite3."
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

# Ejecutar acciones basadas en los argumentos
if $SETUP; then
    setup_env
fi

if $DELETE_DB; then
    delete_db
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
    delete_db
    setup_env
    create_initial_data
    import_qti
    run_server
fi
