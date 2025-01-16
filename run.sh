#!/bin/bash

# Función para obtener la IP local del host según el sistema operativo
get_host_ip() {
    case "$(uname -s)" in
        Linux*)     hostname -I | awk '{print $1}' ;;
        Darwin*)    ipconfig getifaddr en0 ;;  # macOS
        CYGWIN*|MINGW*|MSYS*)
            # Windows (Git Bash, Cygwin, etc.)
            ipconfig | grep -i "IPv4 Address" | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -n 1
            ;;
        *)          echo "Sistema operativo no soportado" >&2; exit 1 ;;
    esac
}

# Verificar si HOST_IP ya existe en .env
if ! grep -q "HOST_IP=" .env; then
    echo "HOST_IP=$(get_host_ip)" >> .env
fi

# Ejecutar docker-compose según el parámetro
case "$1" in
    up*)
        echo "Iniciando contenedores en modo no desacoplado..."
        if [ "$2" = "build" ]; then
            docker-compose up --build
        else
            docker-compose up
        fi
        ;;
    down)
        echo "Deteniendo y eliminando contenedores..."
        docker-compose down
        ;;
    *)
        echo "Uso: $0 {up|down}"
        exit 1
        ;;
esac
