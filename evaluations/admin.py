from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Course, Question, Evaluation, Answer, Option
from .llm_utils import get_llm_feedback
from django.contrib.admin import AdminSite
from django.core.exceptions import ObjectDoesNotExist
import logging
from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import path
import csv
from .forms import EvaluationForm, UserAdminForm, QuestionAdminForm

# Configuración básica del logging
logging.basicConfig(
    level=logging.DEBUG,  # Nivel de logging
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato del mensaje
    handlers=[
        logging.FileHandler("evaluation_debug.log"),  # Guardar logs en un archivo
        logging.StreamHandler()  # Mostrar logs en la consola
    ]
)

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

def import_users_from_csv(request):
    if request.method == "POST":
        form = CsvImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
            for row in reader:
                try:
                    username = row.get('username')
                    password = row.get('password')
                    if username and password:
                        try:
                            user = User.objects.get(username=username)
                            user.set_password(password)
                            user.save()
                            logging.info(f"Updated password for existing user: {username}")
                        except ObjectDoesNotExist:
                            user = User.objects.create_user(username=username, password=password)
                            logging.info(f"Created new user: {username}")
                        
                        grado = row.get('grado')
                        if grado:
                            from .models import UserProfile
                            profile, created = UserProfile.objects.get_or_create(user=user)
                            profile.grado = grado
                            profile.save()
                            logging.info(f"Updated or created profile for user: {username} with grado: {grado}")
                        else:
                            logging.warning(f"No grado provided for user: {username}")
                    else:
                        logging.warning(f"Skipping row due to missing required fields: {row}")
                except Exception as e:
                    logging.error(f"Error processing user from row: {row}. Error: {e}")
            CourseAdmin(Course, custom_admin_site).message_user(request, "Users imported successfully")
            return HttpResponseRedirect(request.path_info)
    else:
        form = CsvImportForm()
    return render(request, 'admin/csv_form.html', {'form': form})

class CustomAdminSite(AdminSite):
    site_header = 'eduNinja Admin'
    site_title = 'eduNinja Admin'
    index_title = 'Welcome to eduNinja Admin'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import_users_csv/', self.admin_view(import_users_from_csv), name='import_users_csv'),
        ]
        return custom_urls + urls

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
    logging.info("Iniciando generación de feedback para los objetos seleccionados")
    for obj in queryset:
        if isinstance(obj, Evaluation):
            evaluation = obj
            logging.debug(f"Procesando evaluación: {evaluation.name}")
            answers = Answer.objects.filter(evaluation=evaluation)
        elif isinstance(obj, Answer):
            answer = obj
            evaluation = answer.evaluation
            logging.debug(f"Procesando respuesta del estudiante: {answer.student.username} para la evaluación: {evaluation.name}")
            answers = [answer]
        else:
            logging.warning(f"Objeto desconocido en el queryset: {obj}")
            continue
        
        for answer in answers:
            logging.debug(f"Procesando respuesta del estudiante: {answer.student.username}")
            user = answer.student
            
            questions_and_answers = []
            selected_options = answer.selected_options if answer.selected_options else []

            # Vamos a recorrer las preguntas y obtener la opción seleccionada para cada una
            for i, question in enumerate(evaluation.questions.all()):
                logging.debug(f"Procesando pregunta: {question.question_text}")
                student_answer = "No contestada"
                if i < len(selected_options):
                    student_answer = selected_options[i]

                # Añadir los detalles de la pregunta y la respuesta al contexto
                questions_and_answers.append({
                    "question": question.question_text,
                    "correct_answer": question.correct_answer,
                    "student_answer": student_answer.text if hasattr(student_answer, 'text') else student_answer,
                    "is_correct": student_answer.text == question.correct_answer if hasattr(student_answer, 'text') else student_answer == question.correct_answer
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
            answer.feedback_check = True
            answer.save()
            logging.info(f"Feedback generado para el estudiante {user.username}")

    # Notificar al usuario que la generación de feedback ha terminado
    modeladmin.message_user(request, "Feedback generation completed for selected objects")
    logging.info("Generación de feedback completada para los objetos seleccionados")

generate_feedback.short_description = "Generate feedback for selected evaluations"

@admin.register(Course, site=custom_admin_site)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Option, site=custom_admin_site)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_latex', 'image')

@admin.register(Question, site=custom_admin_site)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'subject', 'difficulty', 'image', 'latex_format', 'correct_answer', 'display_options')
    list_filter = ('subject', 'latex_format', 'difficulty')
    form = QuestionAdminForm

    def display_options(self, obj):
        return ", ".join([option.text for option in obj.options.all()])
    display_options.short_description = 'Options'

@admin.register(Evaluation, site=custom_admin_site)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'date', 'period', 'llm_model', 'time_limit']
    list_filter = ['llm_model', 'course', 'period', 'time_limit']
    actions = [generate_feedback]
    form = EvaluationForm

@admin.register(Answer, site=custom_admin_site)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['evaluation', 'student', 'selected_options', 'submission_date', 'score', 'attempts', 'feedback_check']
    search_fields = ['evaluation__name', 'student__username']
    list_filter = ['submission_date', 'evaluation__name', 'feedback_check', ScoreFilter]
    actions = [generate_feedback]

from django.utils.html import format_html
from .utils import generate_qr_code

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'qr_code_image', 'grado')
    list_filter = ('profile__grado',)
    form = UserAdminForm

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Grado', {'fields': ('grado',)}),
    )


    def get_queryset(self, request):
        # Almacena el objeto request en una variable de instancia
        self.request = request
        return super().get_queryset(request)

    def grado(self, obj):
        try:
            return obj.profile.grado
        except ObjectDoesNotExist:
            return None
    grado.short_description = 'Grado'

    def qr_code_image(self, obj):
        if obj.password:
            qr_code_url = generate_qr_code(obj, self.request)
            return format_html('<img src="{}" width="400" height="400" />', qr_code_url)
        return "No password set"

    qr_code_image.short_description = "QR Code"

# Register the User and Group models with the custom admin site
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, admin.ModelAdmin)
