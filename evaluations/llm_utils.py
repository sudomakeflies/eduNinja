import requests
from django.conf import settings
from anthropic import Anthropic
import traceback
import logging


anthropic = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

# Configuración básica del logging
logging.basicConfig(
    level=logging.DEBUG,  # Nivel de logging
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato del mensaje
    handlers=[
        logging.FileHandler("evaluation_debug.log"),  # Guardar logs en un archivo
        logging.StreamHandler()  # Mostrar logs en la consola
    ]
)


# Definiciones de los modelos se asumen aquí...
def get_llm_feedback(context, llm_model):
    logging.debug("Generando prompt para el feedback")
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

    
     # Logging del prompt para depuración
    logging.debug(f"Prompt generado: {prompt}")
    
    # Selección del modelo de LLM para obtener el feedback
    if llm_model == 'ollama':
        logging.debug("Feedback generado usando el modelo 'ollama'")
        return get_ollama_feedback(prompt)
    elif llm_model == 'anthropic':
        logging.debug("Feedback generado usando el modelo 'anthropic'")
        return get_anthropic_feedback(prompt)
    else:
        logging.error(f"Modelo LLM no soportado: {llm_model}")
        return "Modelo LLM no soportado."

    

def get_ollama_feedback(prompt):
    #url = "http://host.docker.internal:11434/api/generate"
    url = "http://192.168.0.105:11434/api/generate"
    data = {
        "model": "phi3",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=data, timeout=300)
        response.raise_for_status()
        llm_response = response.json()
        return llm_response.get('response', '').strip()
    except requests.RequestException as e:
        print(f"Error making request to Ollama: {e}")
        print(f"Exception details: {traceback.format_exc()}")
        return f"Exception details: {traceback.format_exc()}"

def get_anthropic_feedback(prompt):
    try:
        response = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
	    temperature=0,
	    system="You are a Ph.D. in mathematics and science education with extensive experience in providing constructive feedback to K-12 students. Your goal is to offer responses that are both encouraging and informative, helping students to develop a deep understanding of mathematical and scientific concepts. When responding, consider the student’s current level of knowledge, their potential misconceptions, and offer guidance that promotes critical thinking and problem-solving skills. Use language that is accessible to the student’s grade level while ensuring that the feedback is rigorous and thought-provoking.",
	    messages=[
	        {
	            "role": "user",
	            "content": [
	                {
	                    "type": "text",
	                    "text": prompt
	                }
	            ]
	        }
	    ]
        )
        return response.content
    except Exception as e:
        print(f"Error making request to Anthropic API: {e}")
        return "Error fetching feedback from Anthropic."
