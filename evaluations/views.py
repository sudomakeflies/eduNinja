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
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async

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

# Función para enviar un mensaje WebSocket
async def send_websocket_message(answer_id, response):
    channel_layer = get_channel_layer()
    await sync_to_async(channel_layer.group_send)(
        "feedback_channel",
        {
            "type": "generate.feedback",
            "answer_id": answer_id,
            "response": response,
        }
    )

@login_required
#@cache_page(60)
def take_evaluation(request, pk):
    #evaluation = get_object_or_404(Evaluation, pk=pk)
    evaluation = get_object_or_404(Evaluation.objects.select_related('course').prefetch_related('questions'), pk=pk)
    student = request.user
    context = {
        'evaluation': evaluation,
        'number_to_letter': number_to_letter,  # Agrega la función al contexto
    }

    # Verificar si ya existe un registro de Answer para esta evaluación y este estudiante
    answer_exists = Answer.objects.filter(evaluation=evaluation, student=student).exists()

    if request.method == 'POST':
        try:
            total_score, selected_options = process_student_answers(request, evaluation)

            answer, created = Answer.objects.update_or_create(
                evaluation=evaluation,
                student=student,
                defaults={
                    'selected_options': selected_options,
                    'feedback': '',
                    'score': total_score,
                    'attempts': F('attempts') - 1 if not created else 3
                }
            )
            
            # Iniciar un proceso asíncrono para manejar la respuesta del LLM
            #asyncio.create_task(handle_llm_response(answer))
            # Enviar un mensaje WebSocket para manejar la respuesta del LLM
            #asyncio.run(send_websocket_message(answer.id, evaluation.questions.all()))  
            # O usa await send_websocket_message(answer.id, response) si el método es async


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
    selected_options = {}

    for question in evaluation.questions.all():
        selected_option = request.POST.get(f'question_{question.id}')
        correct_answer = question.correct_answer
        is_correct = selected_option == correct_answer

        score = value_per_question if is_correct else 0
        total_score += score
        selected_options[str(question.id)] = selected_option

    return total_score, selected_options

@login_required
@cache_page(60)
def evaluation_result(request, pk):
    #evaluation = get_object_or_404(Evaluation, pk=pk)
    #answers = Answer.objects.filter(evaluation=evaluation, student=request.user).exclude(score=None)
    #total_score = sum(answer.score for answer in answers if answer.score is not None)
    evaluation = get_object_or_404(Evaluation.objects.select_related('course'), pk=pk)
    answers = Answer.objects.filter(evaluation=evaluation, student=request.user).exclude(score=None).select_related('evaluation')
    return render(request, 'evaluations/evaluation_result.html', {'evaluation': evaluation, 'answers': answers})

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
def view_answers(request):
    # Obtener las respuestas del usuario autenticado
    #user_answers = Answer.objects.filter(student=request.user)
    user_answers = Answer.objects.filter(student=request.user).select_related('evaluation', 'evaluation__course')
    return render(request, 'evaluations/view_answers.html', {'user_answers': user_answers, 'student': request.user})

def error_view(request):
    return render(request, 'evaluations/error_template.html')