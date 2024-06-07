from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError
#import requests
#from django.http import JsonResponse
#from .utils import FeedbackService, FeedbackServiceError

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Option(models.Model):
    text = models.TextField()
    is_latex = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Question(models.Model):
    SUBJECT_CHOICES = (
    ('Math_Algebra', 'Matemáticas - Álgebra'),
    ('Math_Statistics', 'Matemáticas - Estadística'),
    ('Math_Geometry', 'Matemáticas - Geometría'),
    ('Math_Calculus', 'Matemáticas - Cálculo'),
    ('Math_Trigonometry', 'Matemáticas - Trigonometría'),
    ('Math_Probability', 'Matemáticas - Probabilidad'),
    ('Math_Number Theory', 'Matemáticas - Teoría de Números'),
    ('Math_Logic', 'Matemáticas - Lógica'),
    ('Math_Graphics', 'Matemáticas - Gráficos'),
    ('Math_Tables', 'Matemáticas - Tablas'),
    ('Physics_Kinematics', 'Física - Cinemática'),
    ('Physics_Waves', 'Física - Ondas'),
    ('Physics_Thermodynamics', 'Física - Termodinámica'),
    ('Physics_Electromagnetism', 'Física - Electromagnetismo'),
    ('Physics_Optics', 'Física - Óptica'),
    ('Physics_Mechanics', 'Física - Mecánica'),
    ('Physics_Acoustics', 'Física - Acústica'),
    ('Physics_Astronomy', 'Física - Astronomía'),
    ('Physics_Nuclear Physics', 'Física - Física Nuclear'),
    ('Physics_Relativity', 'Física - Relatividad'),
    ('Physics_Particle Physics', 'Física - Física de Partículas'),
    ('Physics_Dynamics', 'Física - Dinámica'),
    ('Physics_Energy', 'Física - Energía'),
    # Puedes agregar más subcategorías según sea necesario
)

    
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
    #options = models.JSONField(default=list, blank=True, null=True, verbose_name='Opciones de respuesta')
    correct_answer = models.CharField(max_length=200)
    
    def __str__(self):
        return f'{self.subject} - {self.question_text[:20]}'

class Evaluation(models.Model):
    name = models.CharField(max_length=100, default="Matemáticas")
    course = models.ForeignKey('Course', on_delete=models.CASCADE, default=1)
    period = models.CharField(max_length=10, default=1, db_index=True)  # Por ejemplo: I, II, III
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    value_per_question = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    date = models.DateField(default=datetime.now, db_index=True)
    questions = models.ManyToManyField(Question)
    
    def __str__(self):
        return f'{self.name} - {self.date} - ´{self.period}'


class Answer(models.Model):
    evaluation = models.ForeignKey('Evaluation', on_delete=models.CASCADE, related_name='answers', db_index=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    selected_options = models.JSONField(default=list, blank=True, null=True, verbose_name='Lista de respuestas')
    feedback = models.TextField(blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True, db_index=True)
    score = models.FloatField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=2)

    # def save(self, *args, **kwargs):
    #     if self.pk is None:  # Check if the instance is new
    #         try:
    #             super().save(*args, **kwargs)
    #             #self.generate_feedback()  # Call the method for generating feedback
    #         except IntegrityError as e:
    #             if "CHECK constraint failed" in str(e):
    #                 raise ValidationError("Integrity error models.py:106 asyncio feedback evaluations")
    #     else:  # If the instance already exists, just call super without forcing insert
    #         super().save(*args, **kwargs)

    # def generate_feedback(self):
    #     evaluation_data = {
    #         "name": self.evaluation.name,
    #         "course": str(self.evaluation.course),  # Convert course object to string
    #         "max_score": float(self.evaluation.max_score),
    #         "value_per_question": float(self.evaluation.value_per_question),
    #         "questions": [question.id for question in self.evaluation.questions.all()],
    #         "selected_options": self.selected_options,
    #     }

    #     data = {
    #         "type": "generate.feedback",
    #         "answer_id": self.id,
    #         "response": evaluation_data,
    #     }
    #     #response = requests.post("http://localhost:8000/ws/feedback/", json=data, headers={'Content-Type': 'application/json'})
    #     try:
    #         # Assuming 'data' is your JSON data
    #         feedback_response = FeedbackService.send_feedback(data)
    #         # Process the response if needed
    #     except FeedbackServiceError as e:
    #         # Handle the custom feedback service error
    #         error_message = str(e)
    #         return JsonResponse({'error': error_message}, status=500)  # Return an appropriate HTTP response with a JSON error message
        
    #     if feedback_response.status_code != 200:
    #         print("Error al enviar el mensaje WebSocket:", feedback_response.text)
    #     else:
    #         feedback_data = feedback_response.json()
    #         # Aquí asumimos que el feedback recibido del servidor se encuentra en el campo "feedback" del JSON
    #         feedback_text = feedback_data.get("feedback", "")
    #         self.feedback = feedback_text
    #         # Save the feedback without triggering generate_feedback again
    #         super(Answer, self).save(update_fields=['feedback'])

    class Meta:
        unique_together = ('evaluation', 'student')
