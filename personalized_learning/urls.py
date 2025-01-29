from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'personalized_learning'

# Create router for API views
router = DefaultRouter()
router.register(r'api/learning-paths', views.LearningPathViewSet, basename='api-learning-path')
router.register(r'api/resources', views.LearningResourceViewSet, basename='api-resource')
router.register(r'api/chat-sessions', views.ChatSessionViewSet, basename='api-chat-session')

urlpatterns = [
    # Dashboard and Overview
    path('', views.dashboard, name='dashboard'),
    
    # Learning Paths
    path('path/<int:path_id>/', 
         views.learning_path_detail, 
         name='learning_path_detail'),
    
    # Learning Resources
    path('resource/<int:resource_id>/',
         views.resource_detail,
         name='resource_detail'),
    
    # Learning Activities
    path('activity/<int:activity_id>/complete/',
         views.complete_activity,
         name='complete_activity'),
    
    # Chat Interface
    path('chat/',
         views.chat_interface,
         name='chat_interface'),
    path('chat/<int:session_id>/message/',
         views.send_message,
         name='send_message'),
    path('chat/resource-help/',
         views.get_resource_help,
         name='resource_help'),
]

# Add API URLs
urlpatterns += router.urls
