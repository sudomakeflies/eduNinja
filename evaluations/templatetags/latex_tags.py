from django import template
import markdown
from markdown.extensions import Extension
from markdown.extensions.extra import ExtraExtension
import markdown_katex

register = template.Library()

@register.filter
def render_latex(value):
    """
    Renderiza el contenido de LaTeX usando la extensión KaTeX de Markdown.
    """
    extensions = [
        ExtraExtension(),
        markdown_katex.KaTeXExtension(
            no_inline_svg=True,
            insert_fonts_css=False
        ),
    ]
    return markdown.markdown(value, extensions=extensions)

