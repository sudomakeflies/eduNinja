#!/bin/bash

# Instalar dependencias
pip install -r requirements.txt

# Migrar la base de datos
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'diego.beltran@sedtolima.edu.co', 'adminEVA')" | python manage.py shell

# Crear directorio para datos iniciales
mkdir -p initial_data
