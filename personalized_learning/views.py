from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import json

from .models import (
    LearningPath, LearningResource, LearningActivity,
    ChatSession, ChatMessage, Competency, StudentCompetency, 
    CompetencyAssessment
)
from .utils import (
    analyze_evaluation_results, generate_adaptive_recommendations,
    update_learning_path, process_markdown_content,
    get_learning_recommendations
)
from evaluations.llm_utils import get_llm_feedback as get_llm_response

@login_required
def dashboard(request):
    """Student dashboard showing learning paths and progress"""
    learning_paths = LearningPath.objects.filter(
        student=request.user,
        is_active=True
    ).select_related('competency')
    
    # Get recent activities
    recent_activities = LearningActivity.objects.filter(
        student=request.user
    ).select_related('resource', 'learning_path')[:5]
    
    # Get recommendations
    recommendations = generate_adaptive_recommendations(request.user)
    
    context = {
        'learning_paths': learning_paths,
        'recent_activities': recent_activities,
        'recommendations': recommendations
    }
    
    return render(request, 'personalized_learning/dashboard.html', context)

@login_required
def learning_path_detail(request, path_id):
    """View a specific learning path and its resources"""
    path = get_object_or_404(LearningPath, id=path_id, student=request.user)
    
    activities = LearningActivity.objects.filter(
        learning_path=path
    ).select_related('resource')
    
    recommendations = get_learning_recommendations(
        request.user,
        path.competency_id
    )
    
    context = {
        'path': path,
        'activities': activities,
        'recommendations': recommendations
    }
    
    return render(request, 'personalized_learning/learning_path_detail.html', context)

@login_required
def resource_detail(request, resource_id):
    """View a specific learning resource"""
    resource = get_object_or_404(LearningResource, id=resource_id)
    
    # Process markdown content if needed
    if resource.content_type == 'MD':
        processed_content = process_markdown_content(
            resource.content,
            resource.metadata
        )
    else:
        processed_content = {'html': resource.content, 'metadata': resource.metadata}
    
    # Get or create learning activity
    activity, created = LearningActivity.objects.get_or_create(
        student=request.user,
        resource=resource,
        learning_path_id=request.GET.get('path_id')
    )
    
    context = {
        'resource': resource,
        'content': processed_content,
        'activity': activity
    }
    
    return render(request, 'personalized_learning/resource_detail.html', context)

@login_required
@require_http_methods(["POST"])
def complete_activity(request, activity_id):
    """Mark a learning activity as completed"""
    activity = get_object_or_404(
        LearningActivity,
        id=activity_id,
        student=request.user
    )
    
    activity.complete()
    
    # Update learning path progress
    update_result = update_learning_path(
        request.user,
        activity.learning_path.competency_id
    )
    
    return JsonResponse(update_result)

@login_required
def chat_interface(request):
    """Main chat interface view"""
    # Get or create active chat session
    session, created = ChatSession.objects.get_or_create(
        student=request.user,
        defaults={'context': {
            'learning_paths': list(request.user.learning_paths.values_list('competency__name', flat=True)),
            'student_level': 'beginner'  # You might want to determine this dynamically
        }}
    )
    
    # Get chat history
    messages = ChatMessage.objects.filter(session=session)
    paginator = Paginator(messages, 50)
    page = request.GET.get('page', 1)
    
    context = {
        'session': session,
        'messages': paginator.get_page(page)
    }
    
    return render(request, 'personalized_learning/chat.html', context)

@login_required
@require_http_methods(["POST"])
def send_message(request, session_id):
    """Handle sending a chat message"""
    session = get_object_or_404(ChatSession, id=session_id, student=request.user)
    
    # Create user message
    user_message = ChatMessage.objects.create(
        session=session,
        is_student=True,
        content=request.POST.get('message', '')
    )
    
    # Generate AI response
    try:
        # Prepare context for LLM
        context = {
            'chat_history': list(session.messages.values('is_student', 'content')),
            'learning_paths': list(request.user.learning_paths.values_list('competency__name', flat=True)),
            'student_info': {
                'name': request.user.username,
                'learning_style': request.user.learning_style.get_dominant_style()
            }
        }
        
        # Generate response
        prompt = f"""
        As LearnLM, provide a helpful response to assist with learning:
        
        User Message: {user_message.content}
        
        Context:
        - Learning Paths: {', '.join(context['learning_paths'])}
        - Learning Style: {context['student_info']['learning_style']}
        
        Previous messages: {context['chat_history'][-5:] if len(context['chat_history']) > 0 else 'None'}
        
        Provide a clear, constructive response that helps guide the learning process.
        """
        
        ai_response = get_llm_response(prompt)
        
        # Save AI response
        ChatMessage.objects.create(
            session=session,
            is_student=False,
            content=ai_response
        )
        
        return JsonResponse({
            'success': True,
            'response': ai_response
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# API Views
class LearningPathViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LearningPath.objects.filter(student=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        path = self.get_object()
        result = update_learning_path(request.user, path.competency_id)
        return Response(result)

class LearningResourceViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LearningResource.objects.filter(
            competency__in=self.request.user.learning_paths.values('competency')
        )
    
    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        resource = self.get_object()
        activity, created = LearningActivity.objects.get_or_create(
            student=request.user,
            resource=resource,
            learning_path_id=request.data.get('path_id')
        )
        activity.complete()
        return Response({'status': 'completed'})

class ChatSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(student=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        session = self.get_object()
        message_content = request.data.get('message')
        
        if not message_content:
            return Response(
                {'error': 'Message content is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Create user message
        user_message = ChatMessage.objects.create(
            session=session,
            is_student=True,
            content=message_content
        )
        
        try:
            # Generate and save AI response using same logic as web view
            context = {
                'chat_history': list(session.messages.values('is_student', 'content')),
                'learning_paths': list(request.user.learning_paths.values_list('competency__name', flat=True)),
                'student_info': {
                    'name': request.user.username,
                    'learning_style': request.user.learning_style.get_dominant_style()
                }
            }
            
            prompt = f"""
            As LearnLM, provide a helpful response to assist with learning:
            
            User Message: {message_content}
            
            Context:
            - Learning Paths: {', '.join(context['learning_paths'])}
            - Learning Style: {context['student_info']['learning_style']}
            
            Previous messages: {context['chat_history'][-5:] if len(context['chat_history']) > 0 else 'None'}
            
            Provide a clear, constructive response that helps guide the learning process.
            """
            
            ai_response = get_llm_response(prompt)
            
            ai_message = ChatMessage.objects.create(
                session=session,
                is_student=False,
                content=ai_response
            )
            
            return Response({
                'user_message': user_message.content,
                'ai_response': ai_message.content
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@login_required
@require_http_methods(["POST"])
def get_resource_help(request):
    """Handle AI assistance requests for specific learning resources"""
    try:
        data = json.loads(request.body)
        resource = get_object_or_404(LearningResource, id=data.get('resource_id'))
        question = data.get('question')

        if not question:
            return JsonResponse({
                'success': False,
                'error': 'Question is required'
            }, status=400)

        # Get resource content and metadata
        content = process_markdown_content(resource.content, resource.metadata) if resource.content_type == 'MD' else {
            'html': resource.content,
            'metadata': resource.metadata
        }

        # Prepare context for LLM
        context = {
            'resource_title': resource.title,
            'resource_type': resource.get_content_type_display(),
            'competency': resource.competency.name,
            'difficulty_level': resource.difficulty_level,
            'content': content.get('html', '')[:1000]  # First 1000 chars for context
        }

        # Generate response prompt
        prompt = f"""
        As an AI Learning Assistant, help explain this content:

        Resource: {context['resource_title']} ({context['resource_type']})
        Topic: {context['competency']}
        Difficulty: Level {context['difficulty_level']}

        Student Question: {question}

        Content Context:
        {context['content']}

        Please provide a helpful explanation that:
        1. Directly addresses the student's question
        2. Uses clear, accessible language
        3. Provides examples if relevant
        4. Encourages deeper understanding
        """

        response = get_llm_response(prompt)

        return JsonResponse({
            'success': True,
            'response': response
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
