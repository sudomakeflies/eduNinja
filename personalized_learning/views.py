# personalized_learning/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import LearningPath, UserNotification

@login_required
def dashboard(request):
    learning_paths = LearningPath.objects.filter(student=request.user)
    notifications = UserNotification.objects.filter(user=request.user, read=False)
    return render(request, 'personalized_learning/dashboard.html', {
        'learning_paths': learning_paths,
        'notifications': notifications
    })