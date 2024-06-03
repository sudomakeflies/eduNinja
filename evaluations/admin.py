from django.contrib import admin
from .models import Course, Question, Evaluation, Answer

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'subject', 'difficulty', 'image', 'latex_format', 'correct_answer')
    list_filter = ('subject', 'latex_format', 'difficulty')
    def question_text(self, obj):
        return obj.question_text

    question_text.short_description = 'Texto pregunta'  # Opcional: Cambiar el encabezado de la columna

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'date', 'period')
    list_filter = ('course', 'period',)
    def course_name(self, obj):
        return obj.course.name

    course_name.short_description = 'Curso'  # Opcional: Cambiar el encabezado de la columna

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['evaluation', 'student', 'selected_options', 'submission_date', 'score', 'attempts']
    search_fields = ['evaluation__name', 'student__username']
    list_filter = ['submission_date', 'evaluation__name']

    def evaluation_name(self, obj):
        return obj.evaluation.name

    evaluation_name.short_description = 'Evaluación'  # Opcional: Cambiar el encabezado de la columna
