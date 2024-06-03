from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import F

from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

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

    subject = models.CharField(max_length=120, choices=SUBJECT_CHOICES)
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES)
    question_text = models.TextField()
    image = models.ImageField(upload_to='question_images/', null=True, blank=True)  # Opcional: imagen asociada a la pregunta
    latex_format = models.BooleanField(default=True)
    #options = models.JSONField()
    #options = models.ManyToManyField('Option')
    options = models.JSONField(default=list, blank=True, null=True, verbose_name='Opciones de respuesta')
    correct_answer = models.CharField(max_length=200)
    
    def __str__(self):
        return f'{self.subject} - {self.question_text[:50]}'

class Evaluation(models.Model):
    name = models.CharField(max_length=100, default="Matemáticas")
    course = models.ForeignKey('Course', on_delete=models.CASCADE, default=1)
    period = models.CharField(max_length=10, default=1)  # Por ejemplo: I, II, III
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    value_per_question = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    date = models.DateField(default=datetime.now)
    questions = models.ManyToManyField(Question)
    
    def __str__(self):
        return f'{self.name} - {self.date} - ´{self.period}'

class Answer(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='answers')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    selected_options = models.JSONField(default=list, blank=True, null=True, verbose_name='Lista de respuestas')  # To store selected options as a JSON object
    feedback = models.TextField(blank=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=2)  # Contador de intentos del estudiante
    
    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except IntegrityError as e:
            if "CHECK constraint failed" in str(e):
                raise ValidationError("Ya has alcanzado el límite de intentos para esta evaluación")
                
    class Meta:
        unique_together = ('evaluation', 'student')  # Garantizar que solo haya una respuesta por estudiante por evaluación
