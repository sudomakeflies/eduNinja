from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from evaluations.models import Evaluation
from .utils import generate_adaptive_recommendations, integrate_llm_feedback

class LearningStyle(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learning_style')
    visual_score = models.IntegerField(default=0)
    auditory_score = models.IntegerField(default=0)
    kinesthetic_score = models.IntegerField(default=0)
    reading_score = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def get_dominant_style(self):
        scores = {
            'visual': self.visual_score,
            'auditory': self.auditory_score,
            'kinesthetic': self.kinesthetic_score,
            'reading': self.reading_score
        }
        return max(scores, key=scores.get)

class Competency(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='sub_competencies')
    
    class Meta:
        verbose_name_plural = "competencies"

    def __str__(self):
        return self.name

class StudentCompetency(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='competencies')
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE)
    level = models.IntegerField(default=0)  # 0-100
    last_assessed = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "student competencies"

class LearningPath(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_paths')
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE)
    target_level = models.IntegerField(default=100)
    current_level = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    adaptive_recommendations = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.adaptive_recommendations:
            self.adaptive_recommendations = generate_adaptive_recommendations(self.student)
        super().save(*args, **kwargs)

    def get_progress(self):
        return (self.current_level / self.target_level) * 100 if self.target_level > 0 else 0

    def __str__(self):
        return f"{self.student.username} - {self.competency.name} ({self.current_level}/{self.target_level})"

class LearningResource(models.Model):
    RESOURCE_TYPES = [
        ('MD', 'Markdown'),
        ('VID', 'Video'),
        ('PDF', 'PDF'),
        ('QUIZ', 'Quiz'),
        ('PROJ', 'Project')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    content_type = models.CharField(max_length=4, choices=RESOURCE_TYPES)
    content = models.TextField()  # For markdown content or URLs
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE, related_name='resources')
    difficulty_level = models.IntegerField(default=1)  # 1-5
    estimated_duration = models.IntegerField(help_text="Duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)  # For additional resource-specific data

    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"

class LearningActivity(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE)
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress = models.IntegerField(default=0)  # 0-100
    feedback = models.TextField(blank=True)

    def complete(self):
        self.completed_at = timezone.now()
        self.progress = 100
        self.save()

    class Meta:
        verbose_name_plural = "learning activities"

class ChatSession(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_interaction = models.DateTimeField(auto_now=True)
    context = models.JSONField(blank=True, null=True)  # Store session context for LLM

    def __str__(self):
        return f"{self.student.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    is_student = models.BooleanField(default=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)  # Store LLM-related metadata

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{'Student' if self.is_student else 'LearnLM'}: {self.content[:50]}..."

class CompetencyAssessment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='competency_assessments')
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    llm_feedback = models.TextField(blank=True)
    recommendations = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = 'Competency Assessment'
        verbose_name_plural = 'Competency Assessments'

    def save(self, *args, **kwargs):
        if not self.llm_feedback:
            self.llm_feedback = integrate_llm_feedback(self)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.competency.name} - Score: {self.score}"

class CompetencyMismatchLog(models.Model):
    original_name = models.CharField(max_length=200)
    matched_competency = models.ForeignKey(Competency, on_delete=models.CASCADE)
    match_type = models.CharField(max_length=10, choices=[
        ('exact', 'Exact Match'),
        ('fuzzy', 'Fuzzy Match'),
        ('wildcard', 'Wildcard')
    ])
    similarity_score = models.FloatField(null=True, blank=True)
    frequency = models.IntegerField(default=1)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['original_name', 'matched_competency']

    def __str__(self):
        return f"{self.original_name} -> {self.matched_competency.name} ({self.match_type})"
