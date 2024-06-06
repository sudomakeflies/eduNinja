# # utils.py
# import os
# import xml.etree.ElementTree as ET
# from django.core.files import File
# from .models import Course, Question

# def parse_qti_directory(base_path):
#     for root, dirs, files in os.walk(base_path):
#         for file in files:
#             if file.endswith(".xml"):
#                 file_path = os.path.join(root, file)
#                 print(f"Processing file: {file_path}")  # Mensaje de depuración
#                 parse_qti_file("/Users/diego/evals/" + file_path)

# def parse_qti_file(file_path):   
#     namespace = {'qti': 'http://www.imsglobal.org/xsd/imsqti_v2p1'}  # Definir el namespace

#     tree = ET.parse(file_path)
#     root = tree.getroot()

#     # Encuentra todos los elementos 'assessmentItem' dentro del namespace
#     assessment_items = root.iter('{http://www.imsglobal.org/xsd/imsqti_v2p1}assessmentItem')
#     #ET.dump(root)

#     #print(assessment_items, tree, root, namespace)
#     # Imprime los elementos encontrados
#     for item in assessment_items:
#         subject = get_subject_from_path(file_path)
#         difficulty = 'Medium'  # Asigna la dificultad que prefieras o extrae esta información del XML
#         print(f"Subject: {subject}, Difficulty: {difficulty}")  # Mensaje de depuración

#         # Buscar todas las etiquetas <p> bajo <itemBody>
#         paragraphs = item.find('{http://www.imsglobal.org/xsd/imsqti_v2p1}itemBody').findall('.//{http://www.imsglobal.org/xsd/imsqti_v2p1}p')
#         # Inicializar una lista para almacenar los textos de las etiquetas <p>
#         paragraph_texts = []

#         # Iterar sobre las etiquetas <p> y obtener sus textos
#         for paragraph in paragraphs:
#             paragraph_text = paragraph.text.strip()  # Eliminar espacios en blanco al inicio y al final del texto
#             if paragraph_text:
#                 paragraph_texts.append(paragraph_text)

#         # Unir todos los textos de las etiquetas <p> en un solo string
#         question_text = ' '.join(paragraph_texts)
#         options = []
#         correct_answer = ""
#         for choice in item.find('{http://www.imsglobal.org/xsd/imsqti_v2p1}itemBody').find('{http://www.imsglobal.org/xsd/imsqti_v2p1}choiceInteraction').findall('{http://www.imsglobal.org/xsd/imsqti_v2p1}simpleChoice'):
#             print(choice.text)
#             options.append(choice.text)
#             if choice.get('identifier') == item.find('{http://www.imsglobal.org/xsd/imsqti_v2p1}responseDeclaration').find('{http://www.imsglobal.org/xsd/imsqti_v2p1}correctResponse').find('value').text:
#                 correct_answer = choice.text


#         question = Question(
#             subject=subject,
#             difficulty=difficulty,
#             question_text=question_text,
#             options=options,
#             correct_answer=correct_answer
#         )
#         # Save the question to generate an ID
#         question.save()

#         # Process images if any
#         image_tag = item.find('{http://www.imsglobal.org/xsd/imsqti_v2p1}itemBody').find('object')
#         if image_tag is not None:
#             image_path = os.path.join(os.path.dirname(file_path), image_tag.get('data'))
#             if os.path.exists(image_path):
#                 with open(image_path, 'rb') as f:
#                     question.image.save(os.path.basename(image_path), File(f))

#         question.save()
    
    
# def get_subject_from_path(file_path):
#     # Extract subject from file path or file name
#     # For example, if your path is /path/to/Math_Algebra/preguntas.xml, extract 'Math_Algebra'
#     parts = file_path.split(os.sep)
#     for part in parts:
#         if part.startswith('Math_') or part.startswith('Physics_'):
#             return part
#     return 'General'


# def number_to_letter(number):
#     """
#     Convert a number to a corresponding letter (a, b, c, ...).
#     """
#     # Asegúrate de que el número esté en el rango adecuado
#     #if not 1 <= number <= 26:
#     #    raise ValueError("Number must be between 1 and 26")

#     # Convierte el número en una letra usando el código ASCII
#     return chr(number + 96)  # Sumamos 96 para obtener el valor ASCII correspondiente a 'a'
# import os
# from lxml import etree
# from django.core.files import File
# from .models import Course, Question

# def parse_qti_directory(base_path):
#     base_path = os.path.expanduser(base_path)
#     for root, dirs, files in os.walk(base_path):
#         for file in files:
#             if file.endswith(".xml"):
#                 file_path = os.path.join(root, file)
#                 print(f"Processing file: {file_path}")  # Mensaje de depuración
#                 parse_qti_file(file_path)

# def parse_qti_file(file_path):
#     try:
#         tree = etree.parse(file_path)
#         root = tree.getroot()

#         # Print the entire XML for debugging
#         print("Complete XML Tree:")
#         print(etree.tostring(root, pretty_print=True).decode())

#         namespace = {'qti': 'http://www.imsglobal.org/xsd/imsqti_v2p1'}
#         assessment_items = root.xpath('//qti:assessmentItem', namespaces=namespace)

#         print(f"Found {len(assessment_items)} assessment items in {file_path}")
#         if not assessment_items:
#             print(f"No assessment items found in {file_path}")
#             return

#         for item in assessment_items:
#             subject = get_subject_from_path(file_path)
#             difficulty = 'Medium'  # Asigna la dificultad que prefieras o extrae esta información del XML
#             print(f"Subject: {subject}, Difficulty: {difficulty}")  # Mensaje de depuración

#             item_body = item.find('qti:itemBody', namespaces=namespace)
#             if item_body is None:
#                 print(f"No itemBody found for item in {file_path}")
#                 continue

#             paragraphs = item_body.findall('qti:p', namespaces=namespace)
#             paragraph_texts = [p.text.strip() for p in paragraphs if p.text]
#             question_text = ' '.join(paragraph_texts)
#             if not question_text:
#                 print(f"No question text found for item in {file_path}")
#                 continue

#             options = []
#             correct_answer = ""

#             choice_interaction = item_body.find('qti:choiceInteraction', namespaces=namespace)
#             if choice_interaction is None:
#                 print(f"No choiceInteraction found for item in {file_path}")
#                 continue

#             choices = choice_interaction.findall('qti:simpleChoice', namespaces=namespace)
#             for choice in choices:
#                 options.append(choice.text.strip())
            
#             response_declaration = item.find('qti:responseDeclaration', namespaces=namespace)
#             if response_declaration is not None:
#                 correct_response = response_declaration.find('qti:correctResponse', namespaces=namespace)
#                 if correct_response is not None:
#                     correct_value = correct_response.find('qti:value', namespaces=namespace)
#                     if correct_value is not None:
#                         correct_identifier = correct_value.text
#                         correct_choice = next((choice.text.strip() for choice in choices if choice.get('identifier') == correct_identifier), None)
#                         correct_answer = correct_choice if correct_choice else ""

#             if not options:
#                 print(f"No options found for item in {file_path}")
#                 continue

#             print(f"Question Text: {question_text}")
#             print(f"Options: {options}")
#             print(f"Correct Answer: {correct_answer}")

#             question = Question(
#                 subject=subject,
#                 difficulty=difficulty,
#                 question_text=question_text,
#                 options=options,
#                 correct_answer=correct_answer
#             )

#             # Save the question to generate an ID
#             question.save()

#             # Process images if any
#             image_tag = item_body.find('qti:object', namespaces=namespace)
#             if image_tag is not None:
#                 image_path = os.path.join(os.path.dirname(file_path), image_tag.get('data'))
#                 if os.path.exists(image_path):
#                     with open(image_path, 'rb') as f:
#                         question.image.save(os.path.basename(image_path), File(f))

#             question.save()
#     except etree.XMLSyntaxError as e:
#         print(f"XML Syntax Error while parsing {file_path}: {e}")
#     except Exception as e:
#         print(f"Error while parsing {file_path}: {e}")

# def get_subject_from_path(file_path):
#     # Extract subject from file path or file name
#     # For example, if your path is /path/to/Math_Algebra/preguntas.xml, extract 'Math_Algebra'
#     parts = file_path.split(os.sep)
#     for part in parts:
#         if part.startswith('Math_') or part.startswith('Physics_'):
#             return part
#     return 'General'

# def number_to_letter(number):
#     """
#     Convert a number to a corresponding letter (a, b, c, ...).
#     """
#     return chr(number + 96)  # Sumamos 96 para obtener el valor ASCII correspondiente a 'a'

import json
import os
from lxml import etree
from django.core.files import File

def parse_qti_directory(base_path):
    base_path = os.path.expanduser(base_path)
    for root, dirs, files in os.walk(base_path):
        print("files....")
        print(files)
        for file in files:
            if file.endswith(".xml"):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")  # Mensaje de depuración
                parse_qti_file(file_path)

def parse_qti_file(file_path):
    try:
        tree = etree.parse(file_path)
        root = tree.getroot()

        # Print the entire XML for debugging
        print("Complete XML Tree:")
        print(etree.tostring(root, pretty_print=True).decode())

        namespace = {'qti': 'http://www.imsglobal.org/xsd/imsqti_v2p1'}
        assessment_items = root.xpath('//qti:assessmentItem', namespaces=namespace)

        print(f"Found {len(assessment_items)} assessment items in {file_path}")
        if not assessment_items:
            print(f"No assessment items found in {file_path}")
            return

        for item in assessment_items:
            subject = get_subject_from_path(file_path)
            difficulty = 'Medium'  # Asigna la dificultad que prefieras o extrae esta información del XML
            print(f"Subject: {subject}, Difficulty: {difficulty}")  # Mensaje de depuración

            item_body = item.find('qti:itemBody', namespaces=namespace)
            if item_body is None:
                print(f"No itemBody found for item in {file_path}")
                continue

            paragraphs = item_body.findall('qti:p', namespaces=namespace)
            paragraph_texts = [p.text.strip() for p in paragraphs if p.text]
            question_text = ' '.join(paragraph_texts)
            if not question_text:
                print(f"No question text found for item in {file_path}")
                continue

            options = {}
            correct_answer = ""

            choice_interaction = item_body.find('qti:choiceInteraction', namespaces=namespace)
            if choice_interaction is None:
                print(f"No choiceInteraction found for item in {file_path}")
                continue

            choices = choice_interaction.findall('qti:simpleChoice', namespaces=namespace)
            # Modificación de la forma en que se almacenan las opciones en el diccionario
            for choice in choices:
                option_id = choice.get('identifier')
                option_text = choice.text.strip()
                # Eliminar caracteres innecesarios y formatear correctamente
                # Limpiar la cadena
                option_text = option_text.replace('$$', '$').replace(r'\\', '\\')
                print(option_text)
                options[option_id] = f"${option_text}$"
            print("options.......")
            print(options)

            response_declaration = item.find('qti:responseDeclaration', namespaces=namespace)
            if response_declaration is not None:
                correct_response = response_declaration.find('qti:correctResponse/qti:value', namespaces=namespace)
                print("correct_response")
                print(correct_response.text)
                if correct_response is not None:
                    correct_answer = correct_response.text
                    
            if not options:
                print(f"No options found for item in {file_path}")
                continue

            # Eliminar los dobles signos de dólar y los saltos de línea
            options = {key: value.replace('$$', '$').replace('\n', '').replace('\\\\', '\\') for key, value in options.items()}

            # Construir el JSON manualmente
            """options_json = "{"
            for key, value in options.items():
                options_json += f'"{key}": "{value}", '
            options_json = options_json.rstrip(', ') + "}"
            """
            options_json = json.dumps(options, ensure_ascii=False)
            
            print("options_json.....")
            print(options_json)

            print(f"Question Text: {question_text}")
            print(f"Options: {options}")
            print(f"Correct Answer: {correct_answer}")
            from .models import Question
            question = Question(
                subject=subject,
                difficulty=difficulty,
                question_text=question_text,
                options=options_json,
                correct_answer=correct_answer
            )

            # Save the question to generate an ID
            # Process images if any
            save_images(item_body, file_path, question)
            question.save()
            
    except etree.XMLSyntaxError as e:
        print(f"XML Syntax Error while parsing {file_path}: {e}")
    except Exception as e:
        print(f"Error while parsing {file_path}: {e}")

def get_subject_from_path(file_path):
    # Extract subject from file path or file name
    # For example, if your path is /path/to/Math_Algebra/preguntas.xml, extract 'Math_Algebra'
    parts = file_path.split(os.sep)
    for part in parts:
        if part.startswith('Math_') or part.startswith('Physics_'):
            return part
    return 'General'

def save_images(item_body, file_path, question):
    print("Save images QTI")
    print(item_body, file_path, question)
    namespace = {'qti': 'http://www.imsglobal.org/xsd/imsqti_v2p1'}
    #image_tags = item_body.findall('.//{http://www.w3.org/1999/xhtml}img')  # Cambiado para buscar imágenes en el namespace XHTML
    import re
    from lxml.etree import tostring
    item_body_str = tostring(item_body, encoding='unicode')
    image_filenames = re.findall(r'<img\s+src="images/([^"]+)"', item_body_str)

    print("images_filenames...")
    print(image_filenames)
    # If no image filenames found, skip image saving process
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

import requests
from requests.exceptions import ConnectionError

class FeedbackService:
    @staticmethod
    def send_feedback(data):
        try:
            response = requests.post("http://localhost:8000/ws/feedback/", json=data, headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            return response.json()  # Return the JSON response if needed
        except ConnectionError:
            # Handle the connection error
            raise FeedbackServiceError("Error connecting to the feedback service.")

class FeedbackServiceError(Exception):
    print("FeedbackServiceError Exception")