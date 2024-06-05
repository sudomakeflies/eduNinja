import os
import django
from django.template.defaultfilters import escapejs
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from evaluations.models import Course, Question, Evaluation

# Crear cursos
courses_data = [
    {'name': f'Matemáticas {grade}', 'description': f'Curso de matemáticas para grado {grade} IETC San Juan Bosco'} for grade in range(8, 12)
] + [
    {'name': f'Física {grade}', 'description': f'Curso de física matemática {grade} IETC San Juan Bosco'} for grade in range(10, 12)
]

courses = []
for course_data in courses_data:
    course = Course(**course_data)
    course.save()
    courses.append(course)


# Crear preguntas de ejemplo
questions_data = [
    {
        'subject': "Math_Number Theory",
        'difficulty': 'Easy',
        'question_text': 'What is the result of \\( 2 + 2 \\)?',
        'latex_format': True,
        'options': {'ChoiceA': '3', 'ChoiceB': '4', 'ChoiceC': '5'},  # Sin json.dumps
        'correct_answer': 'ChoiceB'
    },
    {
        'subject': "Math_Algebra",
        'difficulty': 'Easy',
        'question_text': 'Solve \\( x^2 - 4 = 0 \\).',
        'latex_format': True,
        'options': {'ChoiceA': '\\( x = 2 \\)', 'ChoiceB': '\\( x = -2 \\)', 'ChoiceC': '\\( x = \\pm 2 \\)'},  # Sin json.dumps
        'correct_answer': 'ChoiceC'
    },
    {
        'subject': "Math_Statistics",
        'difficulty': 'Easy',
        'question_text': 'Dado el siguiente conjunto de datos: \[ 5, 7, 8, 6, 9, 7, 8, 7, 6, 9 \] ¿Cuál es la varianza $\sigma^2$ de los datos?',
        'latex_format': True,
        'options': {"ChoiceA": "$\\sigma^2 = 1.36$", "ChoiceB": "$\\sigma^2 = 1.76$", "ChoiceC": "$\\sigma^2 = 2.16$"},
        'correct_answer': 'ChoiceB'
    },
    {
        'subject': "Math_Statistics",
        'difficulty': 'Easy',
        'question_text': 'En una clase de 25 estudiantes, se registraron las calificaciones de su último examen de la siguiente manera: \[ 85, 90, 78, 92, 88, 76, 84, 85, 79, 91, 82, 75, 89, 80, 87, 83, 88, 77, 85, 86, 90, 84, 79, 81, 82 \] ¿Cuál es la mediana de las calificaciones obtenidas por los estudiantes?',
        'latex_format': True,
        'options': {"ChoiceA": "84","ChoiceB": "85","ChoiceC": "86", "ChoiceD": "89"},
        'correct_answer': 'ChoiceB'
    }
]

# Convertir las opciones a JSON en cada pregunta
# for question_data in questions_data:
#     question = Question.objects.create(**question_data)
#     question.save()



# Crear estudiantes
students_data = [
    {'username': 'student1', 'email': 'student1@example.com', 'password': 'password'},
    {'username': 'student2', 'email': 'student2@example.com', 'password': 'password'}
]

for student_data in students_data:
    student = User.objects.create_user(username=student_data['username'], email=student_data['email'], password=student_data['password'])
    student.save()

# Crear evaluaciones
evaluations_data = [
    {'name': 'Primer Quiz', 'course': courses[0], 'period': 'I', 'max_score': 5, 'value_per_question': 5, 'date': '2024-05-30'},
    {'name': 'Quiz Sorpresa', 'course': courses[1], 'period': 'II', 'max_score': 5, 'value_per_question': 5, 'date': '2024-06-01'},
    {'name': 'Test Estadística', 'course': courses[1], 'period': 'II', 'max_score': 5, 'value_per_question': 2.5, 'date': '2024-06-01'}
]

for eval_data in evaluations_data:
    evaluation = Evaluation(**eval_data)
    evaluation.save()

# Asignar preguntas a evaluaciones
evaluation_questions = {
    'Primer Quiz': [1],
    'Quiz Sorpresa': [2],
    'Test Estadística': [3,4]
}

# for eval_name, pki in evaluation_questions.items():
#     evaluation = Evaluation.objects.get(name=eval_name)
#     for i in pki:
#         question = Question.objects.get(pk=i)
#         evaluation.questions.add(question)
#     evaluation.save()

print("Initial data created successfully.")