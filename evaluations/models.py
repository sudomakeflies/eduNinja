from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.conf import settings
from datetime import timedelta
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    grado = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.grado}'

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Option(models.Model):
    text = models.TextField(null=True)
    is_latex = models.BooleanField(default=False)
    image = models.ImageField(upload_to='option_images/', null=True, blank=True)  # New field for option images

    def __str__(self):
        return str(self.pk)

# Dynamically generate SUBJECT_CHOICES from QTI_Bank subdirectories
import os
QTI_BANK_PATH = 'QTI_Bank'
subdirectories = [d for d in os.listdir(QTI_BANK_PATH) if os.path.isdir(os.path.join(QTI_BANK_PATH, d))]
SUBJECT_CHOICES = tuple((subdir, subdir.replace('_', ' ').title()) for subdir in subdirectories)

class Question(models.Model):
    
    DIFFICULTY_CHOICES = (
        ('Easy', 'Fácil'),
        ('Medium', 'Medio'),
        ('Hard', 'Difícil'),
    )

    subject = models.CharField(max_length=120, choices=SUBJECT_CHOICES, db_index=True)
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES, db_index=True)
    question_text = models.TextField()
    image = models.ImageField(upload_to='question_images/', null=True, blank=True)  # Opcional: imagen asociada a la pregunta
    latex_format = models.BooleanField(default=False)
    options = models.ManyToManyField('Option')    
    correct_answer = models.CharField(max_length=200)
    
    def __str__(self):
        return f'({self.pk}) {self.subject} - {self.question_text[:50]}'

def create_question_order(sender, instance, action, pk_set, **kwargs):
    """
    Signal para manejar la creación automática de QuestionOrder cuando se agregan preguntas
    a una evaluación a través de la relación many-to-many directamente.
    """
    if action == "post_add":
        evaluation = instance
        # Obtener el último orden o empezar desde 0
        last_order = QuestionOrder.objects.filter(evaluation=evaluation).aggregate(
            models.Max('order'))['order__max'] or -1
        
        # Para cada pregunta agregada
        for question_id in pk_set:
            # Si no existe un orden para esta pregunta, crear uno
            if not QuestionOrder.objects.filter(evaluation=evaluation, question_id=question_id).exists():
                last_order += 1
                QuestionOrder.objects.create(
                    evaluation=evaluation,
                    question_id=question_id,
                    order=last_order
                )

class Evaluation(models.Model):
    LLM_CHOICES = [
        ('ollama', 'Ollama'),
        ('anthropic', 'Anthropic Claude 3.5'),
        ('gemini', 'Gemini 2.0 flash'),
    ]
    name = models.CharField(max_length=100, default="Matemáticas")
    course = models.ForeignKey('Course', on_delete=models.CASCADE, default=1)
    period = models.CharField(max_length=10, default=1, db_index=True)  # Por ejemplo: I, II, III
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    value_per_question = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    date = models.DateField(default=datetime.now, db_index=True)
    questions = models.ManyToManyField(Question)
    llm_model = models.CharField(max_length=10, choices=LLM_CHOICES, default='gemini')
    time_limit = models.DurationField(
        null=True, 
        blank=True, 
        default=timedelta(hours=1.7), 
        help_text="Tiempo límite para la evaluación (HH:MM:SS)"
    )
    is_active = models.BooleanField(default=True, help_text="If enabled, students can take this evaluation")
    enable_logs = models.BooleanField(default=True, help_text="If enabled, student activity will be logged")
    
    def __str__(self):
        return f'{self.name} - {self.date} - ´{self.period}'
    
    def add_question(self, question):
        """
        Agrega una pregunta a la evaluación manteniendo el orden.
        """
        if not self.questions.filter(id=question.id).exists():
            self.questions.add(question)
            # El orden se creará automáticamente a través del signal

class Answer(models.Model):
    evaluation = models.ForeignKey('Evaluation', on_delete=models.CASCADE, related_name='answers', db_index=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    selected_options = models.JSONField(default=list, blank=True, null=True, verbose_name='Lista de respuestas')
    feedback = models.TextField(blank=True, null=True)
    feedback_check = models.BooleanField(default=False)
    submission_date = models.DateTimeField(auto_now_add=True, db_index=True)
    score = models.FloatField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ('evaluation', 'student')

class QuestionOrder(models.Model):
    evaluation = models.ForeignKey('Evaluation', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('evaluation', 'question')
        ordering = ['order']

    def __str__(self):
        return f'Evaluation {self.evaluation.id} - Question {self.question.id} - Order {self.order}'

class EvaluationLog(models.Model):
    evaluation = models.ForeignKey('Evaluation', on_delete=models.CASCADE, related_name='logs', db_index=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f'{self.student.username} - {self.evaluation.name} - {self.timestamp}'

# Conectar el signal con el modelo Evaluation
m2m_changed.connect(create_question_order, sender=Evaluation.questions.through)
