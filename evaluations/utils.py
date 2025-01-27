import os
from lxml import etree
from django.core.files import File
from .models import Question, Option
from django.db.models import Q

# Verificamos si la pregunta existe para no duplicarla
def question_exists(question_text, subject):
    return Question.objects.filter(
        Q(question_text=question_text) & Q(subject=subject)
    ).exists()

# Función para convertir un elemento XML a su cadena HTML
def element_to_html(element):
    return etree.tostring(element, encoding='unicode', method='html')

def parse_qti_directory(base_path):
    base_path = os.path.expanduser(base_path)
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".xml"):
                file_path = os.path.join(root, file)
                parse_qti_file(file_path)

def parse_qti_file(file_path):
    try:
        tree = etree.parse(file_path)
        root = tree.getroot()

        namespace = {'qti': 'http://www.imsglobal.org/xsd/imsqti_v2p1'}
        assessment_items = root.xpath('//qti:assessmentItem', namespaces=namespace)

        if not assessment_items:
            return

        for item in assessment_items:
            subject = get_subject_from_path(file_path)
            difficulty = 'Medium'  # Asigna la dificultad que prefieras o extrae esta información del XML

            item_body = item.find('qti:itemBody', namespaces=namespace)
            if item_body is None:
                continue

            paragraphs = item_body.findall('qti:p', namespaces=namespace)
            paragraph_texts = [p.text.strip() for p in paragraphs if p.text]
            #print("paragraphs_texts.....")
            #print(paragraph_texts)
            
            # Iterate over each paragraph and find tables within it
            tables = item_body.findall('qti:table', namespaces=namespace)
            if tables:
                print("tables....")
                print(tables)
                for table in tables:
                    table_html = element_to_html(table)
                    paragraph_texts.append(table_html)

            question_text = ' '.join(paragraph_texts)
            #question_text = ' '.join(paragraphs)
            
            if not question_text:
                continue

            # Verificar si la pregunta ya existe
            if question_exists(question_text, subject):
                print(f"La pregunta ya existe en la base de datos. Archivo: {file_path}")
                continue

            options = {}
            correct_answer = ""

            choice_interaction = item_body.find('qti:choiceInteraction', namespaces=namespace)
            if choice_interaction is None:
                continue

            format_latex = item_body.find('qti:formatLatex', namespaces=namespace)
            if format_latex is not None:
                format_latex_value = format_latex.text.strip().lower() == 'true'
            else:
                format_latex_value = False#format_latex = item_body.find('{http://www.imsglobal.org/xsd/imsqti_v2p1}formatLatex')
            #format_latex_value = format_latex.text.strip().lower() == 'true' if format_latex is not None and format_latex.text is not None else False


            response_declaration = item.find('qti:responseDeclaration', namespaces=namespace)
            if response_declaration is not None:
                correct_response = response_declaration.find('qti:correctResponse/qti:value', namespaces=namespace)
                if correct_response is not None:
                    correct_answer = correct_response.text

            # if not options:
            #     print(f"No options found for item in {file_path}")
            #     continue

            question = Question(
                subject=subject,
                difficulty=difficulty,
                question_text=question_text,
                correct_answer=correct_answer,
                latex_format=format_latex_value
            )
            question.save()  # Save the question to generate an ID

            choices = choice_interaction.findall('qti:simpleChoice', namespaces=namespace)
            option_instances = []
            for choice in choices:
                option_id = choice.get('identifier')
                is_latex =  choice.get('is_latex')
                option_text = choice.text.strip() if choice.text else ''
                if is_latex:
                    options[option_id] = f"${option_text}$"
                else:
                    options[option_id] = option_text

                # Handle tables within options
                tables_in_option = choice.findall('.//qti:table', namespaces=namespace)
                if tables_in_option:
                    option_text_with_tables = option_text
                    for table in tables_in_option:
                        table_html = element_to_html(table)
                        option_text_with_tables += table_html
                    option_text = option_text_with_tables

                option_instance = Option(text=option_text, is_latex=is_latex)

                # Handle option images
                #option_image = choice.find('qti:img', namespaces=namespace)
                print(etree.tostring(choice, pretty_print=True).decode())
                #option_image = choice.find('.//{http://www.imsglobal.org/xsd/imsqti_v2p1}img')
                #print("option_image...", option_image)

                # Try finding the 'img' element with the namespace prefix
                option_image_src = choice.get('image')
                print("option_image_src: ", option_image_src)
                # Check if the image element was found
                if option_image_src is not None:
                    print("Yes Choice Image element found: ", option_image_src)
                    #image_filename = option_image.get('src').split('/')[-1]
                    image_path = os.path.join(os.path.dirname(file_path), 'images', option_image_src)
                    if os.path.exists(image_path):
                        with open(image_path, 'rb') as f:
                            option_instance.image.save(option_image_src, File(f), save=False)
                else:
                    print("No Choice Image element found within the simpleChoice.")

                option_instance.save()
                option_instances.append(option_instance)
            question.options.set(option_instances)  # Use set() to associate options with the question
            question.save()  # Guardar la pregunta nuevamente después de establecer las opciones


            # Process images if any
            #options(item_body, file_path, question)
            print("saving images process")
            save_images(item_body, file_path, question)

    except etree.XMLSyntaxError as e:
        print(f"XML Syntax Error while parsing {file_path}: {e}")
    except Exception as e:
        print(f"Error while parsing {file_path}: {type(e).__name__} - {str(e)}")


def get_subject_from_path(file_path):
    parts = file_path.split(os.sep)
    for part in parts:
        if part in ['QTI_Bank']:
            continue
        if part and part != '':
            return part
    return 'General'

def save_images(item_body, file_path, question):
    import re
    from lxml.etree import tostring
    item_body_str = tostring(item_body, encoding='unicode')
    image_filenames = re.findall(r'<img\s+src="images/([^"]+)"', item_body_str)
    print("image_filename var print in saving Question.imagen import_qti")
    print(image_filenames)
    if not image_filenames:
        return

    for image_filename in image_filenames:
        image_path = os.path.join(os.path.dirname(file_path), 'images', image_filename)
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                question.image.save(image_filename, File(f), save=False)
                question.save()


def number_to_letter(number):
    """
    Convert a number to a corresponding letter (a, b, c, ...).
    """
    return chr(number + 96)  # Sumamos 96 para obtener el valor ASCII correspondiente a 'a'

from django.core.files.storage import default_storage
import qrcode
from io import BytesIO
from django.conf import settings
from django.core.signing import TimestampSigner
from urllib.parse import quote

def generate_qr_code(user, request):
    base_url = settings.HOSTNAME
    signer = TimestampSigner()
    token = signer.sign(str(user.id))  # Firma el user_id
    login_url = f"{base_url}:8000/api/qr_login/?token={quote(token)}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(login_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    
    file_name = f"qr_code_{user.username}.png"
    file_path = os.path.join("media","QRs", file_name)
    
    with open(file_path, "wb") as f:
        f.write(buffer.getvalue())

    return f"{base_url}/media/QRs/{file_name}"
