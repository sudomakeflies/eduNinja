"""
WSGI config for tu_proyecto project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evals.settings')  # Reemplaza 'tu_proyecto' con el nombre de tu proyecto Django

application = get_wsgi_application()
