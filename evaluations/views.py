#import asyncio
#from openai import OpenAI
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import Course, Question, Evaluation, Answer
from django.contrib.auth.decorators import login_required
from .utils import number_to_letter  # Importa la función desde archivo de utilidades
from django.db.models import F
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

@method_decorator(cache_page(60), name='dispatch')
class HomeView(ListView):
    model = Course
    template_name = 'evaluations/home.html'
    context_object_name = 'courses'

@method_decorator(cache_page(60), name='dispatch')
class CourseListView(ListView):
    model = Course
    template_name = 'evaluations/course_list.html'
    context_object_name = 'courses'

@method_decorator(cache_page(60), name='dispatch')
class CourseDetailView(DetailView):
    model = Course
    template_name = 'evaluations/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['evaluations'] = Evaluation.objects.filter(course=self.object).select_related('course')
        return context

@method_decorator(cache_page(60), name='dispatch')
class QuestionListView(ListView):
    model = Question
    template_name = 'evaluations/question_list.html'
    context_object_name = 'questions'

@method_decorator(cache_page(60), name='dispatch')
class EvaluationListView(ListView):
    model = Evaluation
    template_name = 'evaluations/evaluation_list.html'
    context_object_name = 'evaluations'

@login_required
#@cache_page(60)
def take_evaluation(request, pk):
    #evaluation = get_object_or_404(Evaluation, pk=pk)
    evaluation = get_object_or_404(Evaluation.objects.select_related('course').prefetch_related('questions'), pk=pk)
    
    # Check if evaluation is active
    if not evaluation.is_active:
        return render(request, 'evaluations/evaluation_inactive.html', {'evaluation': evaluation})
        
    student = request.user
    request.session['evaluation_start_time'] = str(datetime.now())
    request.session['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
    # Obtener preguntas en orden, con fallback al ID si no existe orden específico
    questions = evaluation.questions.all().order_by(
        'questionorder__order',
        'id'
    )

    context = {
        'evaluation': evaluation,
        'questions': questions,
        'number_to_letter': number_to_letter,
    }

    # Verificar si ya existe un registro de Answer y si ha excedido el límite de intentos
    existing_answer = Answer.objects.filter(evaluation=evaluation, student=student).first()
    if existing_answer and existing_answer.attempts >= 1:
        return render(request, 'evaluations/evaluation_inactive.html', 
                     {'evaluation': evaluation, 
                      'message': 'Ya has alcanzado el límite de intentos para esta evaluación.'})

    if request.method == 'POST':
        try:
            total_score, selected_options = process_student_answers(request, evaluation)

            answer, created = Answer.objects.get_or_create(
                evaluation=evaluation,
                student=student,
                defaults={
                    'selected_options': selected_options,
                    'feedback': '',
                    'score': total_score,
                    'attempts': 1
                }
            )

            if not created and answer.attempts < 1:
                print("Print actualizando answer evaluation model")
                answer.selected_options = selected_options
                answer.feedback = ''
                answer.score = total_score
                answer.attempts = F('attempts') + 1
                answer.save()
            elif not created:
                # Si ya alcanzó el límite de intentos, redirigir con mensaje
                return render(request, 'evaluations/evaluation_inactive.html', 
                            {'evaluation': evaluation, 
                             'message': 'Ya has alcanzado el límite de intentos para esta evaluación.'})
            

        except ValidationError as e:
            # Si se produce un error de validación, redirigir a la vista de error
            return redirect(reverse('error_view'))

        # Obtener todas las respuestas para la evaluación y el estudiante
        answers = Answer.objects.filter(evaluation=evaluation, student=student)

        # Redirigir a la página de resultados con el puntaje total
        #return redirect('evaluation_result', {'total_score': total_score, 'pk':evaluation.pk})
        return render(request, 'evaluations/evaluation_result.html', {'evaluation': evaluation, 'answers':answers })
        #result_text = f"\nTotal score: {total_score}\n"
        #return HttpResponse(result_text, content_type='text/plain')

    return render(request, 'evaluations/take_evaluation.html', context)

def process_student_answers(request, evaluation):
    total_score = 0
    value_per_question = evaluation.value_per_question
    selected_options = []

    # Obtener preguntas en el mismo orden que en la vista
    for question in evaluation.questions.all().order_by('questionorder__order', 'id'):
        selected_option = request.POST.get(f'question_{question.id}')
        
        if selected_option:
            correct_answer = question.correct_answer
            num_to_letter = lambda selected_option: 'Choice' + chr(64 + int(selected_option)) if selected_option.isdigit() and 1 <= int(selected_option) <= 10 else selected_option
            selected_option = num_to_letter(selected_option)
            is_correct = selected_option == correct_answer
            score = value_per_question if is_correct else 0
            total_score += score
        else:
            selected_option = None
            score = 0

        selected_options.append(selected_option)

    # Si todas las respuestas son None, devolvemos una lista vacía
    if all(option is None for option in selected_options):
        selected_options = {}

    return total_score, selected_options

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
@cache_page(60)
def evaluation_result(request, pk):
    #evaluation = get_object_or_404(Evaluation, pk=pk)
    #answers = Answer.objects.filter(evaluation=evaluation, student=request.user).exclude(score=None)
    #total_score = sum(answer.score for answer in answers if answer.score is not None)
    evaluation = get_object_or_404(Evaluation.objects.select_related('course'), pk=pk)
    answers = Answer.objects.filter(evaluation=evaluation, student=request.user).exclude(score=None).select_related('evaluation')
    return render(request, 'evaluations/evaluation_result.html', {'evaluation': evaluation, 'answers': answers})

@login_required
@cache_page(60)
def view_answers(request):
    # Obtener las respuestas del usuario autenticado
    #user_answers = Answer.objects.filter(student=request.user)
    user_answers = Answer.objects.filter(student=request.user).select_related('evaluation', 'evaluation__course')
    return render(request, 'evaluations/view_answers.html', {'user_answers': user_answers, 'student': request.user})

def error_view(request):
    return render(request, 'evaluations/error_template.html')

@csrf_exempt
def log_evaluation_event(request):
    from .models import EvaluationLog
    import json
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            evaluation_id = data.get('evaluation_id')
            event_type = data.get('event_type')
             # Validate required fields
            if not evaluation_id or not event_type:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

            evaluation = get_object_or_404(Evaluation, pk=evaluation_id)
            
            # Only log if logging is enabled for this evaluation
            if evaluation.enable_logs:
                student = request.user
                start_time = request.session.get('evaluation_start_time')
                user_agent = request.session.get('user_agent')
                end_time = datetime.now()
                start_time_dt = datetime.fromisoformat(start_time) if start_time else None
                duration = end_time - start_time_dt if start_time_dt else None

                EvaluationLog.objects.create(
                    evaluation=evaluation,
                    student=student,
                    start_time=start_time_dt,
                    end_time=end_time,
                    duration=duration,
                    user_agent=user_agent,
                    event_type=event_type
                )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@csrf_exempt
def qr_login(request):
    from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
    from django.core.cache import cache
    from urllib.parse import unquote
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if request.method == 'GET':
        token = request.GET.get('token')
        if not token:
            return JsonResponse({'status': 'error', 'message': 'Token no proporcionado'}, status=400)

        token_decodificado = unquote(token)
        signer = TimestampSigner()
        
        try:
            # Extrae el user_id y session_id del token
            token_data = signer.unsign(token_decodificado, max_age=300)  # 5 minutos de validez
            user_id = token_data.split(':')[0] if ':' in token_data else token_data
            
            # Verifica si hay una sesión activa para este usuario
            cache_key = f'qr_login_session_{user_id}'
            stored_token = cache.get(cache_key)
            
            if stored_token and stored_token != token:
                # Si hay un token diferente almacenado, significa que se generó un nuevo QR
                return JsonResponse({
                    'status': 'error', 
                    'message': 'Se ha generado un nuevo código QR. Por favor, escanee el nuevo código.'
                }, status=401)
            
            # Busca el usuario en la base de datos
            user = User.objects.get(id=user_id)
            
            # Almacena el token actual en la caché
            cache.set(cache_key, token, timeout=300)  # 5 minutos de timeout
            
            # Autentica al usuario
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            return redirect('/')

        except SignatureExpired:
            return JsonResponse({
                'status': 'error', 
                'message': 'El código QR ha expirado. Por favor, solicite uno nuevo.'
            }, status=401)
        except BadSignature:
            return JsonResponse({
                'status': 'error', 
                'message': 'Código QR inválido.'
            }, status=401)
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error', 
                'message': 'Usuario no encontrado.'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': 'Error durante el inicio de sesión. Por favor, intente nuevamente.'
            }, status=500)
