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
    md = markdown.Markdown(extensions=[ExtraExtension(), KatexExtension()])
    return md.convert(text)

@register.filter
def parse_json_options(value):
    # Convertir la cadena JSON a un diccionario de Python
    options_dict = json.loads(value)
    # Obtener los pares clave-valor del diccionario
    options_items = options_dict.items()
    return options_items