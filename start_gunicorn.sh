#!/bin/sh
set -e

# Iniciar Gunicorn con el archivo de configuración
exec gunicorn wsgi:application -c gunicorn_config.py