from django import template
from django.utils.safestring import mark_safe
import re

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
