import json
import markdown
from django import template
from markdown.extensions.extra import ExtraExtension
from markdown_katex import KatexExtension
from evaluations.utils import number_to_letter

register = template.Library()

@register.filter
def convert_number_to_letter(number):
    return number_to_letter(number)

@register.filter(name='markdown_katex')
def markdown_katex_filter(text):
    if not isinstance(text, str):
        text = str(text)  # Ensure text is a string
    md = markdown.Markdown(extensions=[ExtraExtension(), KatexExtension()])
    return md.convert(text)

# @register.filter
# def parse_json_options(value):
#     # Convertir la cadena JSON a un diccionario de Python
#     options_dict = json.loads(value)
#     # Obtener los pares clave-valor del diccionario
#     options_items = options_dict.items()
#     return options_items
# @-register.filter
# def parse_json_options(value):
#     # Verificar si value es una cadena
#     if not isinstance(value, str):
#         return value

#     try:
#         # Convertir la cadena JSON a un diccionario de Python
#         options_dict = json.loads(value)
#         # Obtener los pares clave-valor del diccionario
#         options_items = options_dict.items()
#         return options_items
#     except json.JSONDecodeError:
#         # En caso de que no se pueda decodificar como JSON, devolver el valor original
#         return value

@register.filter
def parse_json_options(value):
    # Verificar si el valor es una cadena
    if not isinstance(value, str):
        # Si no es una cadena, devolver el valor tal cual
        return value

    try:
        # Intentar analizar la cadena como JSON
        options_dict = json.loads(value)
        # Verificar si el JSON analizado es un diccionario
        if isinstance(options_dict, dict):
            # Si es un diccionario, devolver sus elementos
            options_items = options_dict.items()
            return options_items
        else:
            # Si no es un diccionario, devolver el valor tal cual
            return value
    except json.JSONDecodeError:
        # Si falla el análisis como JSON, devolver el valor tal cual
        return value
    
@register.filter(name='chr')
def chr_filter(value):
    try:
        return chr(value)
    except (TypeError, ValueError):
        return ''