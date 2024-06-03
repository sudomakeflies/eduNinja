#!/bin/bash

function setup_env {
    echo "Configurando el entorno..."
    bash setup_env.sh
}

function create_initial_data {
    echo "Generando datos iniciales..."
    python3 create_initial_data.py
}

function run_server {
    echo "Iniciando el servidor..."
    python3 manage.py runserver_plus --cert-file localhost.pem --key-file localhost-key.pem
}

# Argumentos por defecto
SETUP=false
INITIAL_DATA=false
RUN_SERVER=false

# Interpretar argumentos de línea de comandos
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --setup) SETUP=true ;;
        --initial-data) INITIAL_DATA=true ;;
        --run-server) RUN_SERVER=true ;;
        --all) SETUP=true; INITIAL_DATA=true; RUN_SERVER=true ;;
        *) echo "Opción desconocida: $1" ;;
    esac
    shift
done

# Ejecutar acciones basadas en los argumentos
if $SETUP; then
    setup_env
fi

if $INITIAL_DATA; then
    create_initial_data
fi

if $RUN_SERVER; then
    run_server
fi

# Si no se especifica ningún argumento, se asume que se quiere realizar todo el proceso
if ! $SETUP && ! $INITIAL_DATA && ! $RUN_SERVER; then
    setup_env
    create_initial_data
    run_server
fi
