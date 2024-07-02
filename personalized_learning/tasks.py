from celery import shared_task
from django.contrib.auth import get_user_model
from evaluations.models import Evaluation, Answer
from .utils import llm_feedback
import json

@shared_task
def generate_feedback():
    User = get_user_model()
    for user in User.objects.all():
        for course in Course.objects.filter(evaluation__answers__student=user).distinct():
            evaluations = Evaluation.objects.filter(course=course, answers__student=user)
            
            for evaluation in evaluations:
                answer = Answer.objects.get(evaluation=evaluation, student=user)
                
                # Recopilamos información detallada sobre las preguntas y respuestas
                questions_and_answers = []
                for question in evaluation.questions.all():
                    student_answer = answer.selected_options.get(str(question.id), "No contestada")
                    questions_and_answers.append({
                        "question": question.question_text,
                        "correct_answer": question.correct_answer,
                        "student_answer": student_answer,
                        "is_correct": student_answer == question.correct_answer
                    })

                # Preparamos el contexto para el LLM
                context = {
                    "student_name": user.username,
                    "course_name": course.name,
                    "evaluation_name": evaluation.name,
                    "score": answer.score,
                    "max_score": evaluation.max_score,
                    "questions_and_answers": questions_and_answers
                }

                # Llamamos a la función llm_feedback con el contexto
                feedback_json = llm_feedback(context)
                feedback_data = json.loads(feedback_json)

                # Actualizamos el feedback en la respuesta del estudiante
                answer.feedback = feedback_data['feedback']
                answer.save()

                # Aquí podrías añadir lógica para notificar al estudiante si lo deseas

    return "Feedback generation completed for all students and their evaluations"