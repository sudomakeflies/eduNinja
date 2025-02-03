from django import template
from django.utils.safestring import mark_safe
import re
import json

register = template.Library()

@register.filter(is_safe=True)
def render_textblock(text_content):
    if isinstance(text_content, str):
        # Usa una expresión regular para extraer el contenido de 'text'
        match = re.search(r"text='(.*?)', type='text'", text_content, re.DOTALL)
        if match:
            content = match.group(1)
            # Reemplaza los saltos de línea literales (\n) por <br>
            content = content.replace('\\n', '<br>')
            return mark_safe(content)
        else:
            # Si no encuentra el patrón, devuelve el contenido original
            return mark_safe(text_content.replace('\n', '<br>'))
    return '[Contenido no es una cadena de texto]'

@register.filter
def split_string(value, delimiter):
    return value.split(delimiter)

@register.filter
def zip_lists(a, b):
    return zip(a, b)

@register.filter
def convert_number_to_letter(number):
    """
    Convierte un número a su letra correspondiente (1=A, 2=B, etc.)
    """
    return chr(64 + int(number))

@register.filter
def get_item(dictionary, key):
    """
    Obtiene un item de un diccionario.
    Maneja casos donde la clave puede ser un entero o string.
    """
    if dictionary is None:
        return None
    
    # Convertir la clave a string ya que en el template siempre será string
    str_key = str(key)
    return dictionary.get(str_key, None)

@register.filter
def parse_feedback_json(value):
    """
    Parsea una cadena JSON y devuelve un diccionario.
    Retorna None si el parsing falla.
    """
    try:
        if not value:
            print("Empty feedback value")
            return None
            
        print(f"Attempting to parse JSON: {value[:200]}...")  # Print first 200 chars for debugging
        return json.loads(value)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        print(f"Problematic JSON content: {value}")
        return None
    except TypeError as e:
        print(f"Type error: {str(e)}")
        return None
