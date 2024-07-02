# models.py
from django.db import models
# from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from .utils import generate_adaptive_recommendations
from evaluations.models import Evaluation

# class NinjaUser(AbstractUser):
#     bio = models.TextField(blank=True)
#     learning_style = models.CharField(max_length=100, blank=True)

# class Course(models.Model):
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     teacher = models.ForeignKey(NinjaUser, on_delete=models.CASCADE, related_name='courses')

#     def __str__(self):
#         return self.title

class LearningPath(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_paths')
    #course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)
    adaptive_recommendations = models.JSONField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.adaptive_recommendations:
            self.adaptive_recommendations = generate_adaptive_recommendations(self.student)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.progress}"

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    ninjauser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    due_date = models.DateTimeField()
    resources = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.title

class Assessment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assessments')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')
    score = models.IntegerField()
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='assessments')

    def save(self, *args, **kwargs):
        if not self.llm_feedback:
            self.llm_feedback = integrate_llm_feedback(self)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.task.title} - Score: {self.score}"