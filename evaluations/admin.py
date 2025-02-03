from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Course, Question, Evaluation, Answer, Option, QuestionOrder
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
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model

User = get_user_model()

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

    def each_context(self, request):
        context = super().each_context(request)
        context['host_ip'] = settings.HOST_IP  # Agrega la IP al contexto
        return context

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
            selected_options = answer.selected_options if answer.selected_options else {}

            # Get questions using consistent ordering method
            for question in Evaluation.get_ordered_questions(evaluation):
                question_id = str(question.id)
                logging.debug(f"Procesando pregunta {question_id}: {question.question_text}")
                
                student_response = selected_options.get(question_id, {})
                student_answer = student_response.get('answer', 'No contestada')

                # Añadir los detalles de la pregunta y la respuesta al contexto
                questions_and_answers.append({
                    "question_id": question_id,
                    "question": question.question_text,
                    "correct_answer": question.correct_answer,
                    "student_answer": student_answer,
                    "is_correct": student_response.get('is_correct', False),
                    "score": student_response.get('score', 0)
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

            # Analizar el feedback para actualizar las competencias
            from personalized_learning.utils import analyze_feedback_for_competencies
            try:
                competency_results = analyze_feedback_for_competencies(feedback, user)
                if not competency_results['success']:
                    logging.error(f"Error al analizar competencias: {competency_results['error']}")
                else:
                    logging.info(f"Competencias actualizadas: {competency_results['competency_updates']}")
            except Exception as e:
                logging.error(f"Error al procesar competencias: {str(e)}")

    # Notificar al usuario que la generación de feedback ha terminado
    modeladmin.message_user(request, "Feedback generation and competency analysis completed")
    logging.info("Generación de feedback y análisis de competencias completados")

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

class QuestionOrderInline(admin.TabularInline):
    model = QuestionOrder
    extra = 1
    ordering = ['order']
    raw_id_fields = ['question']

@admin.register(Evaluation, site=custom_admin_site)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'date', 'period', 'llm_model', 'time_limit']
    list_filter = ['llm_model', 'course', 'period', 'time_limit']
    actions = [generate_feedback]
    form = EvaluationForm
    inlines = [QuestionOrderInline]
    
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Si hay nuevas preguntas agregadas a través del admin, usar add_question
        if 'questions' in form.cleaned_data:
            current_questions = set(form.instance.questions.all())
            new_questions = set(form.cleaned_data['questions'])
            # Para cada pregunta nueva que no estaba antes
            for question in new_questions - current_questions:
                form.instance.add_question(question)

@admin.register(QuestionOrder, site=custom_admin_site)
class QuestionOrderAdmin(admin.ModelAdmin):
    list_display = ['evaluation', 'question', 'order']
    list_filter = ['evaluation']
    ordering = ['evaluation', 'order']
    search_fields = ['evaluation__name', 'question__question_text']
    raw_id_fields = ['evaluation', 'question']

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


class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'get_user_id', 'expire_date')
    readonly_fields = ('session_data', 'expire_date')

    def get_user_id(self, obj):
        try:
            session_data = obj.get_decoded()
            user_id = session_data.get('_auth_user_id')
            if user_id:
                user = User.objects.get(pk=user_id)
                return user.username # o user.id si prefieres el ID numérico
            else:
                return "Ningún usuario logueado"
        except (KeyError, User.DoesNotExist):
            return "Error al obtener el usuario"

    get_user_id.short_description = 'Usuario'

# Register the User and Group models with the custom admin site
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, admin.ModelAdmin)
custom_admin_site.register(Session, SessionAdmin)

from .models import EvaluationLog
@admin.register(EvaluationLog, site=custom_admin_site)
class EvaluationLogAdmin(admin.ModelAdmin):
    list_display = ['evaluation', 'student', 'timestamp', 'event_type']
    list_filter = ['evaluation', 'student', 'event_type']
