import os
from lxml import etree
from django.core.files import File
from .models import Question, Option, Answer
from django.db.models import Q, Avg, Count, F, FloatField, Min, Max
from django.db.models.functions import Cast
from collections import defaultdict
from decimal import Decimal
import json

# Keep existing functions
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
            
            # Iterate over each paragraph and find tables within it
            tables = item_body.findall('qti:table', namespaces=namespace)
            if tables:
                print("tables....")
                print(tables)
                for table in tables:
                    table_html = element_to_html(table)
                    paragraph_texts.append(table_html)

            question_text = ' '.join(paragraph_texts)
            
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
                format_latex_value = False

            response_declaration = item.find('qti:responseDeclaration', namespaces=namespace)
            if response_declaration is not None:
                correct_response = response_declaration.find('qti:correctResponse/qti:value', namespaces=namespace)
                if correct_response is not None:
                    correct_answer = correct_response.text

            question = Question(
                subject=subject,
                difficulty=difficulty,
                question_text=question_text,
                correct_answer=correct_answer,
                latex_format=format_latex_value
            )
            question.save()

            choices = choice_interaction.findall('qti:simpleChoice', namespaces=namespace)
            option_instances = []
            for choice in choices:
                option_id = choice.get('identifier')
                is_latex = choice.get('is_latex')
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

                option_image_src = choice.get('image')
                if option_image_src is not None:
                    image_path = os.path.join(os.path.dirname(file_path), 'images', option_image_src)
                    if os.path.exists(image_path):
                        with open(image_path, 'rb') as f:
                            option_instance.image.save(option_image_src, File(f), save=False)

                option_instance.save()
                option_instances.append(option_instance)
            question.options.set(option_instances)
            question.save()

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
    login_url = f"{base_url}/api/qr_login/?token={quote(token)}"
    
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

# New functions for technical-pedagogical report
def calculate_question_statistics(evaluation):
    """Calculate statistical indicators for each question in the evaluation."""
    questions = evaluation.questions.all()
    statistics = []
    
    for question in questions:
        # Get all answers for this question
        answers = Answer.objects.filter(evaluation=evaluation)
        total_answers = answers.count()
        
        # Initialize counters
        correct_count = 0
        answer_distribution = defaultdict(int)
        
        # Analyze each answer
        for answer in answers:
            if answer.selected_options:
                selected_options = answer.selected_options
                # Convert to list if it's a string representation of JSON
                if isinstance(selected_options, str):
                    selected_options = json.loads(selected_options)
                
                # Count correct answers and collect response distribution
                question_id = str(question.id)
                if question_id in selected_options:
                    student_answer = selected_options[question_id].get('answer', 'No contestada')
                    answer_distribution[student_answer] += 1
                    if selected_options[question_id].get('is_correct', False):
                        correct_count += 1
        
        # Calculate success rate
        success_rate = (correct_count / total_answers * 100) if total_answers > 0 else 0
        
        # Determine difficulty level based on success rate
        if success_rate >= 70:
            difficulty_level = "Fácil"
        elif success_rate >= 40:
            difficulty_level = "Medio"
        else:
            difficulty_level = "Difícil"
        
        # Get most common answers (top 3)
        common_answers = [{k: v} for k, v in 
                         sorted(answer_distribution.items(), 
                               key=lambda x: x[1], 
                               reverse=True)[:3]]
        
        stat_dict = {
            'id': question.id,
            'text': question.question_text,
            'success_rate': float(round(success_rate, 2)),
            'correct_count': int(correct_count),
            'total_answers': int(total_answers),
            'difficulty_level': difficulty_level,
            'common_answers': [{k: int(v)} for item in common_answers for k, v in item.items()]
        }
        statistics.append(stat_dict)
    
    return statistics

def prepare_report_context(evaluation):
    """Prepare the context data for the technical-pedagogical report."""
    # Get all answers for this evaluation
    answers = Answer.objects.filter(evaluation=evaluation)
    
    # Calculate basic statistics
    total_students = answers.count()
    average_score = answers.aggregate(
        avg_score=Avg(Cast('score', FloatField()))
    )['avg_score'] or 0
    
    # Get score range
    if total_students > 0:
        score_stats = answers.exclude(score__isnull=True).aggregate(
            min_score=Min(Cast('score', FloatField())),
            max_score=Max(Cast('score', FloatField()))
        )
        if score_stats['min_score'] is not None and score_stats['max_score'] is not None:
            score_range = f"{score_stats['min_score']:.2f} - {score_stats['max_score']:.2f}"
        else:
            score_range = "No scores recorded"
    else:
        score_range = "No submissions"
    
    # Calculate question statistics
    question_stats = calculate_question_statistics(evaluation)
    
    # Prepare student results for analysis
    student_results = []
    for answer in answers:
        result = {
            'student_id': answer.student.id,
            'score': answer.score,
            'answers': answer.selected_options if isinstance(answer.selected_options, dict) 
                      else json.loads(answer.selected_options) if answer.selected_options 
                      else {}
        }
        student_results.append(result)
    
    # Convert Decimal objects to float for JSON serialization
    def decimal_to_float(obj):
        if hasattr(obj, 'student_id'):  # Answer object
            return {
                'student_id': obj.student_id,
                'score': float(obj.score) if obj.score is not None else None
            }
        return obj

    # Prepare context for LLM analysis
    context = {
        'evaluation_name': evaluation.name,
        'course_name': evaluation.course.name,
        'student_results': student_results,
        'average_score': float(round(average_score, 2)),
        'max_score': float(evaluation.max_score),
        'score_range': score_range,
        'question_stats': question_stats
    }
    
    # Convert any remaining Decimal objects in student_results
    for result in context['student_results']:
        if 'score' in result and isinstance(result['score'], (Decimal, float)):
            result['score'] = float(result['score'])
    
    return context
