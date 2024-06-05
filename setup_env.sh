#!/bin/bash

# Instalar dependencias
pip install -r requirements.txt

# Migrar la base de datos
python3 manage.py makemigrations
python3 manage.py migrate

# Crear superusuario
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')" | python3 manage.py shell

# Crear directorio para datos iniciales
#mkdir -p initial_data
