from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Course, Question, Evaluation, Answer, Option
from .llm_utils import get_llm_feedback
from django.contrib.admin import AdminSite
from django.core.exceptions import ObjectDoesNotExist
import logging


# Configuración básica del logging
logging.basicConfig(
    level=logging.DEBUG,  # Nivel de logging
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato del mensaje
    handlers=[
        logging.FileHandler("evaluation_debug.log"),  # Guardar logs en un archivo
        logging.StreamHandler()  # Mostrar logs en la consola
    ]
)

class CustomAdminSite(AdminSite):
    site_header = 'eduNinja Admin'
    site_title = 'eduNinja Admin'
    index_title = 'Welcome to eduNinja Admin'

custom_admin_site = CustomAdminSite(name='customadmin')

class ScoreFilter(admin.SimpleListFilter):
    title = 'Puntaje'
    parameter_name = 'score'

    def lookups(self, request, model_admin):
        return (
            ('gte_3', 'Mayor o igual a 3.0'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'gte_3':
            return queryset.filter(score__gte=3.0)

def generate_feedback(modeladmin, request, queryset):
    logging.info("Iniciando generación de feedback para las evaluaciones seleccionadas")
    for evaluation in queryset:
        logging.debug(f"Procesando evaluación: {evaluation.name}")
        answers = Answer.objects.filter(evaluation=evaluation)
        
        for answer in answers:
            logging.debug(f"Procesando respuesta del estudiante: {answer.student.username}")
            user = answer.student
            
            questions_and_answers = []
            selected_options = answer.selected_options if answer.selected_options else []

            # Vamos a recorrer las preguntas y simplemente obtener la opción seleccionada
            for question in evaluation.questions.all():
                logging.debug(f"Procesando pregunta: {question.question_text}")
                try:
                    # Buscamos la opción seleccionada por el usuario
                    student_answer = next((option for option in selected_options if option), "No contestada")

                except (KeyError, ObjectDoesNotExist) as e:
                    logging.error(f"Error al procesar la pregunta {question.question_text}: {str(e)}")
                    student_answer = "No contestada"

                # Añadir los detalles de la pregunta y la respuesta al contexto
                questions_and_answers.append({
                    "question": question.question_text,
                    "correct_answer": question.correct_answer,
                    "student_answer": student_answer,
                    "is_correct": student_answer == question.correct_answer  # Esto se mantiene para completar el contexto
                })

            # Crear el contexto para la generación de feedback
            context = {
                "student_name": user.username,
                "course_name": evaluation.course.name,
                "evaluation_name": evaluation.name,
                "score": answer.score,
                "max_score": evaluation.max_score,
                "questions_and_answers": questions_and_answers
            }

            # Obtener el feedback del modelo LLM seleccionado
            feedback = get_llm_feedback(context, evaluation.llm_model)
            
            # Guardar el feedback en la base de datos
            answer.feedback = feedback
            answer.save()
            logging.info(f"Feedback generado para el estudiante {user.username}")

    # Notificar al usuario que la generación de feedback ha terminado
    modeladmin.message_user(request, "Feedback generation completed for selected evaluations")
    logging.info("Generación de feedback completada para las evaluaciones seleccionadas")

generate_feedback.short_description = "Generate feedback for selected evaluations"

@admin.register(Course, site=custom_admin_site)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Option, site=custom_admin_site)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_latex', 'image')

@admin.register(Question, site=custom_admin_site)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'subject', 'difficulty', 'image', 'latex_format', 'correct_answer')
    list_filter = ('subject', 'latex_format', 'difficulty')

@admin.register(Evaluation, site=custom_admin_site)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'date', 'period', 'llm_model', 'time_limit']
    list_filter = ['llm_model', 'course', 'period', 'time_limit']
    actions = [generate_feedback]

@admin.register(Answer, site=custom_admin_site)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['evaluation', 'student', 'selected_options', 'submission_date', 'score', 'attempts', 'feedback_check']
    search_fields = ['evaluation__name', 'student__username']
    list_filter = ['submission_date', 'evaluation__name', 'feedback_check', ScoreFilter]

# Register the User and Group models with the custom admin site
custom_admin_site.register(User, admin.ModelAdmin)
custom_admin_site.register(Group, admin.ModelAdmin)