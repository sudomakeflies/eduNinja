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


class HomeView(ListView):
    model = Course
    template_name = 'evaluations/home.html'
    context_object_name = 'courses'

class CourseListView(ListView):
    model = Course
    template_name = 'evaluations/course_list.html'
    context_object_name = 'courses'

class CourseDetailView(DetailView):
    model = Course
    template_name = 'evaluations/course_detail.html'
    context_object_name = 'course'

class QuestionListView(ListView):
    model = Question
    template_name = 'evaluations/question_list.html'
    context_object_name = 'questions'

class EvaluationListView(ListView):
    model = Evaluation
    template_name = 'evaluations/evaluation_list.html'
    context_object_name = 'evaluations'


@login_required
def take_evaluation(request, pk):
    evaluation = get_object_or_404(Evaluation, pk=pk)
    student = request.user
    context = {
        'evaluation': evaluation,
        'number_to_letter': number_to_letter,  # Agrega la función al contexto
    }

    # Verificar si ya existe un registro de Answer para esta evaluación y este estudiante
    answer_exists = Answer.objects.filter(evaluation=evaluation, student=student).exists()

    if request.method == 'POST':
        try:

            # Procesar las respuestas del estudiante
            # Calcular la calificación
            total_score = 0
            value_per_question = evaluation.value_per_question
            selected_options = {}

            for question in evaluation.questions.all():
                selected_option = request.POST.get(f'question_{question.id}')
                correct_answer = question.correct_answer
                is_correct = selected_option == correct_answer
                print(selected_option) 
                print(correct_answer)

                # Calcular el puntaje
                score = value_per_question if is_correct else 0
                total_score += score
                selected_options[str(question.id)] = selected_option  # Store the selected option

            if not answer_exists:
                # Crear un nuevo registro de Answer si no existe uno previo
                answer = Answer.objects.create(
                    evaluation=evaluation,
                    student=student,
                    selected_options=selected_options,
                    feedback = '',
                    score= total_score,
                    attempts=3  # Comienza con 3 intentos
                )
                #answer.question.set(evaluation.questions.all())
            else:
                # Actualizar el registro existente y reducir el contador de intentos
                answer = Answer.objects.get(evaluation=evaluation, student=student)
                # Actualizar los campos con los datos del POST
                #answer.question = question
                #answer.question.set(evaluation.questions.all())
                answer.selected_options = selected_options
                answer.feedback = ''  # O puedes actualizar con el valor deseado
                answer.score = total_score
                answer.attempts = F('attempts') - 1  # Reducir el contador de intentos en 1
                # Guardar los cambios en la base de datos
                answer.save()
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

@login_required
def evaluation_result(request, pk):
    evaluation = get_object_or_404(Evaluation, pk=pk)
    answers = Answer.objects.filter(evaluation=evaluation, student=request.user).exclude(score=None)
    #total_score = sum(answer.score for answer in answers if answer.score is not None)
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
def view_answers(request):
    # Obtener las respuestas del usuario autenticado
    user_answers = Answer.objects.filter(student=request.user)
    return render(request, 'evaluations/view_answers.html', {'user_answers': user_answers, 'student': request.user})

def error_view(request):
    return render(request, 'evaluations/error_template.html')