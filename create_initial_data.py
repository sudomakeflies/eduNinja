import os
import django
#from django.template.defaultfilters import escapejs
#import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from evaluations.models import Course, Question, Evaluation

def create_courses():
    courses_data = [
        {'name': f'Matemáticas {grade}', 'description': f'Curso de matemáticas para grado {grade} IETC San Juan Bosco'} for grade in range(8, 12)
    ] + [
        {'name': f'Física {grade}', 'description': f'Curso de física matemática {grade} IETC San Juan Bosco'} for grade in range(10, 12)
    ]

    for course_data in courses_data:
        Course.objects.get_or_create(name=course_data['name'], defaults=course_data)
    print("Cursos creados o verificados.")

def create_questions():
    questions_data = [
        {
            'subject': "Math_Number Theory",
            'difficulty': 'Easy',
            'question_text': 'What is the result of \\( 2 + 2 \\)?',
            'latex_format': True,
            'options': {'ChoiceA': '3', 'ChoiceB': '4', 'ChoiceC': '5'},
            'correct_answer': 'ChoiceB'
        },
        # ... (otros datos de preguntas)
    ]

    for question_data in questions_data:
        Question.objects.get_or_create(question_text=question_data['question_text'], defaults=question_data)
    print("Preguntas creadas o verificadas.")

def create_students():
    students_data = [
        {'username': 'student1', 'email': 'student1@example.com', 'password': 'password'},
        {'username': 'student2', 'email': 'student2@example.com', 'password': 'password'}
    ]

    for student_data in students_data:
        User.objects.get_or_create(username=student_data['username'], defaults={
            'email': student_data['email']
        })
    print("Estudiantes creados o verificados.")

def create_evaluations():
    evaluations_data = [
        {'name': 'Primer Quiz', 'course': Course.objects.get(name='Matemáticas 8'), 'period': 'I', 'max_score': 5, 'value_per_question': 5, 'date': '2024-05-30'},
        {'name': 'Quiz Sorpresa', 'course': Course.objects.get(name='Matemáticas 9'), 'period': 'II', 'max_score': 5, 'value_per_question': 5, 'date': '2024-06-01'},
        {'name': 'Test Estadística', 'course': Course.objects.get(name='Matemáticas 9'), 'period': 'II', 'max_score': 5, 'value_per_question': 2.5, 'date': '2024-06-01'}
    ]

    for eval_data in evaluations_data:
        Evaluation.objects.get_or_create(name=eval_data['name'], defaults=eval_data)
    print("Evaluaciones creadas o verificadas.")

def assign_questions_to_evaluations():
    evaluation_questions = {
        'Primer Quiz': ['What is the result of \\( 2 + 2 \\)?'],
        'Quiz Sorpresa': ['Solve \\( x^2 - 4 = 0 \\).'],
        'Test Estadística': ['Dado el siguiente conjunto de datos: \[ 5, 7, 8, 6, 9, 7, 8, 7, 6, 9 \] ¿Cuál es la varianza $\sigma^2$ de los datos?',
                             'En una clase de 25 estudiantes, se registraron las calificaciones de su último examen de la siguiente manera: \[ 85, 90, 78, 92, 88, 76, 84, 85, 79, 91, 82, 75, 89, 80, 87, 83, 88, 77, 85, 86, 90, 84, 79, 81, 82 \] ¿Cuál es la mediana de las calificaciones obtenidas por los estudiantes?']
    }

    for eval_name, question_texts in evaluation_questions.items():
        evaluation = Evaluation.objects.get(name=eval_name)
        for question_text in question_texts:
            question = Question.objects.get(question_text=question_text)
            evaluation.questions.add(question)
    print("Preguntas asignadas a evaluaciones.")

if __name__ == "__main__":
    create_courses()
    #create_questions()
    create_students()
    create_evaluations()
    #assign_questions_to_evaluations()
    print("Initial data created or verified successfully.")