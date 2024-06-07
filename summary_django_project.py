# summary_django_project.py
import os
import sys
import django
from django.apps import apps
import inspect
from django.views import View
from django.conf import settings
from django.urls import get_resolver, URLPattern, URLResolver

# Añadir la ruta del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Inicializar Django
django.setup()

def list_models():
    #print("\nMODELOS")
    for app in apps.get_app_configs():
        #print(f"\nApp: {app.label}")
        for model in app.get_models():
            #print(f"  Model: {model.__name__}")

def list_views():
    #print("\nVISTAS")
    for app in apps.get_app_configs():
        #print(f"\nApp: {app.label}")
        try:
            module = __import__(f"{app.name}.views", fromlist=[''])
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, View):
                    #print(f"  View Class: {name}")
                elif inspect.isfunction(obj):
                    #print(f"  View Function: {name}")
        except ModuleNotFoundError:
            #print(f"  No views module in {app.label}")

def list_urls(urlpatterns=None, prefix=''):
    if urlpatterns is None:
        #print("\nURLS")
        resolver = get_resolver()
        urlpatterns = resolver.url_patterns
    for pattern in urlpatterns:
        if isinstance(pattern, URLPattern):
            #print(f"{prefix}{pattern.pattern}")
        elif isinstance(pattern, URLResolver):
            #print(f"{prefix}{pattern.pattern}/")
            list_urls(pattern.url_patterns, prefix + '    ')

if __name__ == "__main__":
    try:
        list_models()
        list_views()
        list_urls()
    except AttributeError as e:
        #print(f"Error: {e}")
        if not hasattr(settings, 'ROOT_URLCONF'):
            #print("Asegúrate de que la configuración de Django esté correcta y que 'ROOT_URLCONF' esté definida en tu archivo settings.py.")
