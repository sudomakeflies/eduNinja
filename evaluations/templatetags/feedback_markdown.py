import markdown
from django import template
from django.utils.safestring import mark_safe
from markdown.extensions.extra import ExtraExtension
from markdown.extensions.fenced_code import FencedCodeExtension

register = template.Library()

@register.filter(name='feedback_markdown')
def feedback_markdown_filter(text):
    if not isinstance(text, str):
        text = str(text)
    md = markdown.Markdown(extensions=[ExtraExtension(), FencedCodeExtension()])
    return mark_safe(md.convert(text))
