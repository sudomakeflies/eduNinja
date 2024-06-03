import markdown2
from django import template
from evaluations.utils import number_to_letter

register = template.Library()

@register.filter
def convert_number_to_letter(number):
    return number_to_letter(number)

@register.filter(name='markdown_katex')
def markdown_katex_filter(value):
    extras = ["fenced-code-blocks", "footnotes", "tables", "cuddled-lists", "metadata"]
    markdown = markdown2.Markdown(extras=extras)
    html = markdown.convert(value)
    
    # Añadir scripts de KaTeX
    katex_script = '''
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.13.13/katex.min.css">
    <script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.13.13/katex.min.js"></script>
    <script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.13.13/contrib/auto-render.min.js"></script>
    <script>
      document.addEventListener("DOMContentLoaded", function() {
        renderMathInElement(document.body, {
          delimiters: [
            {left: "$$", right: "$$", display: true},
            {left: "$", right: "$", display: false},
            {left: "\\(", right: "\\)", display: false},
            {left: "\\[", right: "\\]", display: true}
          ]
        });
      });
    </script>
    '''
    return html + katex_script
