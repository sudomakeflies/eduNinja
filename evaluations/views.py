import logging
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
from django.db import models
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
    
    # Get questions in consistent order
    questions = Evaluation.get_ordered_questions(evaluation)

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
            
            # Crear un registro de logging para depuración
            logging.debug(f"Evaluation {evaluation.id} - Student {student.id} - Score: {total_score}")
            logging.debug(f"Selected options: {selected_options}")

            answer, created = Answer.objects.get_or_create(
                evaluation=evaluation,
                student=student,
                defaults={
                    'selected_options': selected_options,
                    'feedback': '',
                    'score': float(total_score),
                    'attempts': 1
                }
            )

            if not created and answer.attempts < 1:
                logging.info(f"Actualizando respuesta existente para evaluación {evaluation.id} - estudiante {student.id}")
                answer.selected_options = selected_options
                answer.feedback = ''
                answer.score = float(total_score)
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

        # Get questions in correct order and render evaluation results
        ordered_questions = Evaluation.get_ordered_questions(evaluation)
        return render(request, 'evaluations/evaluation_result.html', {
            'evaluation': evaluation, 
            'answers': answers,
            'ordered_questions': ordered_questions
        })
        #result_text = f"\nTotal score: {total_score}\n"
        #return HttpResponse(result_text, content_type='text/plain')

    return render(request, 'evaluations/take_evaluation.html', context)

def process_student_answers(request, evaluation):
    if evaluation.value_per_question * evaluation.questions.count() > evaluation.max_score:
        logging.warning(f"Evaluation {evaluation.id}: value_per_question * number of questions exceeds max_score")
    
    total_score = 0
    value_per_question = evaluation.value_per_question
    selected_options = {}
    questions_order = {}

    # Get questions in consistent order and create order mapping
    ordered_questions = Evaluation.get_ordered_questions(evaluation)
    for order, question in enumerate(ordered_questions):
        questions_order[question.id] = order

    # Process each response using the same ordering
    for question in ordered_questions:
        selected_option = request.POST.get(f'question_{question.id}')
        
        if selected_option:
            # Normalizar el formato de la respuesta a ChoiceX
            if selected_option:
                # La respuesta viene como una letra (A, B, C, D)
                # Simplemente agregarle el prefijo 'Choice'
                selected_option = f'Choice{selected_option}'
                logging.debug(f"Respuesta normalizada: -> {selected_option}")
                
            # También normalizar la respuesta correcta
            correct_answer = question.correct_answer
            if correct_answer and not correct_answer.startswith('Choice'):
                if len(correct_answer) == 1 and correct_answer.isalpha():
                    correct_answer = f'Choice{correct_answer.upper()}'
                    # Actualizar la respuesta correcta en la base de datos
                    question.correct_answer = correct_answer
                    question.save()
            
            # Comparar con la respuesta correcta
            is_correct = selected_option == question.correct_answer
            logging.debug(f"Question {question.id}: selected={selected_option}, correct={question.correct_answer}, is_correct={is_correct}")
            score = value_per_question if is_correct else 0
            total_score += score

            # Guardar la respuesta con metadata (convirtiendo Decimal a float)
            selected_options[str(question.id)] = {
                'answer': selected_option,
                'is_correct': is_correct,
                'score': float(score),
                'order': questions_order[question.id]
            }

    # Asegurar que el puntaje total no exceda el máximo
    total_score = min(total_score, evaluation.max_score)

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
#@cache_page(60)
def evaluation_result(request, pk):
    evaluation = get_object_or_404(Evaluation.objects.select_related('course'), pk=pk)
    answers = Answer.objects.filter(evaluation=evaluation, student=request.user).exclude(score=None).select_related('evaluation')
    
    # Get questions in correct order
    ordered_questions = Evaluation.get_ordered_questions(evaluation)
    
    return render(request, 'evaluations/evaluation_result.html', {
        'evaluation': evaluation, 
        'answers': answers,
        'ordered_questions': ordered_questions
    })

@login_required
#@cache_page(60)
def view_answers(request):
    # Get user's answers
    user_answers = Answer.objects.filter(student=request.user).select_related('evaluation', 'evaluation__course')
    
    # For each answer, get the ordered questions for its evaluation
    answer_data = []
    for answer in user_answers:
        ordered_questions = Evaluation.get_ordered_questions(answer.evaluation)
        answer_data.append({
            'answer': answer,
            'ordered_questions': ordered_questions
        })
    
    return render(request, 'evaluations/view_answers.html', {
        'answer_data': answer_data,
        'student': request.user
    })

def error_view(request):
    return render(request, 'evaluations/error_template.html')

@login_required
@cache_page(60)
def view_question(request, pk):
    question = get_object_or_404(Question.objects.prefetch_related('options'), pk=pk)
    return render(request, 'evaluations/view_question.html', {
        'question': question
    })

#@login_required
@cache_page(60)
def preview_evaluation(request, pk):
    evaluation = get_object_or_404(Evaluation.objects.select_related('course').prefetch_related('questions'), pk=pk)
    
    # Check if evaluation is active
    if not evaluation.is_active:
        return render(request, 'evaluations/evaluation_inactive.html', {'evaluation': evaluation})
        
    # Get questions in consistent order
    questions = Evaluation.get_ordered_questions(evaluation)

    context = {
        'evaluation': evaluation,
        'questions': questions,
        'number_to_letter': number_to_letter,
    }

    return render(request, 'evaluations/preview_evaluation.html', context)

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
