# utils.py
import json
#from .models import LearningPath

def generate_adaptive_recommendations(student):
    """
    Generate adaptive recommendations for a student based on their learning paths and progress.
    """
    learning_paths = LearningPath.objects.filter(student=student)
    recommendations = []

    for path in learning_paths:
        if path.progress < 50:
            recommendations.append({
                "course": path.course.title,
                "recommendation": "Revisa los recursos recomendados y completa las tareas pendientes."
            })
        else:
            recommendations.append({
                "course": path.course.title,
                "recommendation": "Continúa con las tareas y prepárate para la evaluación final."
            })

    if student.learning_style:
        recommendations.append({
            "learning_style": student.learning_style,
            "recommendation": f"Para tu estilo de aprendizaje '{student.learning_style}', considera usar métodos de estudio específicos."
        })

    return json.dumps(recommendations)

import requests
import json

def llm_feedback(context):
    """
    Integrate feedback from LLMs for a given assessment by making a real API call to Ollama server.
    """
    url = "http://localhost:11434/api/generate"

    # Preparar el prompt con la información del contexto
    prompt = f"""
    Proporciona feedback detallado para el estudiante {context['student_name']} 
    en el curso {context['course_name']} para la evaluación {context['evaluation_name']}.
    
    Puntuación del estudiante: {context['score']} de {context['max_score']}
    
    Detalles de las preguntas y respuestas:
    """
    
    for qa in context['questions_and_answers']:
        prompt += f"""
        Pregunta: {qa['question']}
        Respuesta correcta: {qa['correct_answer']}
        Respuesta del estudiante: {qa['student_answer']}
        ¿Correcta?: {'Sí' if qa['is_correct'] else 'No'}
        """

    prompt += "\nPor favor, proporciona un feedback constructivo basado en este desempeño."

    data = {
        "model": "llama2",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()

        llm_response = response.json()
        feedback = llm_response.get('response', '').strip()

        return json.dumps({
            "student": context['student_name'],
            "course": context['course_name'],
            "evaluation": context['evaluation_name'],
            "score": context['score'],
            "feedback": feedback
        })

    except requests.RequestException as e:
        print(f"Error making request to Ollama: {e}")
        return json.dumps({
            "student": context['student_name'],
            "course": context['course_name'],
            "evaluation": context['evaluation_name'],
            "score": context['score'],
            "feedback": "Error fetching feedback from LLM."
        })