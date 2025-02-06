import requests
from django.conf import settings
from anthropic import Anthropic
import traceback
import logging
from google import genai
import json

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

def get_llm_feedback(context, llm_model):
    logging.debug("Generando prompt para el feedback")
    prompt = f"""
    Como un experto en educación, proporciona un análisis detallado del desempeño del estudiante {context['student_name']} 
    en el curso {context['course_name']} para la evaluación {context['evaluation_name']}.
    
    Puntuación general: {context['score']} de {context['max_score']}
    
    Para cada pregunta, analiza:
    1. La competencia específica evaluada
    2. El nivel de dominio demostrado (0-100)
    3. Fortalezas y áreas de mejora
    4. Recomendaciones específicas para mejorar
    
    Análisis por pregunta:
    """
    
    # Las preguntas ya vienen ordenadas desde el admin.py
    for qa in context['questions_and_answers']:
        question_id = str(qa['question_id'])
        prompt += f"""
        Pregunta ID: {question_id}
        Pregunta: {qa['question']}
        Respuesta correcta: {qa['correct_answer']}
        Respuesta del estudiante: {qa['student_answer']}
        Estado: {'Correcta' if qa['is_correct'] else 'Incorrecta'}
        Puntaje obtenido: {qa['score']} de {context['max_score']/len(context['questions_and_answers'])}
        
        Por favor analiza:
        - Competencia(s) evaluada(s)
        - Nivel de dominio demostrado
        - Análisis específico
        - Recomendaciones de mejora
        
        ---
        """

    prompt += """
    Proporciona tu análisis en el siguiente formato JSON:
    {
        "overall_analysis": {
            "summary": "Resumen general del desempeño",
            "score": "Puntuación numérica",
            "primary_strengths": ["fortaleza1", "fortaleza2"],
            "primary_areas_for_improvement": ["área1", "área2"]
        },
        "competency_analysis": [
            {
                "competency_name": "nombre de la competencia",
                "demonstrated_level": "nivel numérico (0-100)",
                "strengths": ["fortaleza1", "fortaleza2"],
                "areas_for_improvement": ["área1", "área2"],
                "recommendations": ["recomendación1", "recomendación2"],
                "related_questions": [1, 2, 3]
            }
        ],
        "question_analysis": [
            {
                "question_number": 1,
                "competencies": ["competencia1", "competencia2"],
                "demonstrated_level": "nivel numérico (0-100)",
                "analysis": "análisis detallado",
                "recommendations": ["recomendación1", "recomendación2"]
            }
        ]
    }
    
    Asegúrate de que el feedback sea constructivo, específico y orientado a la mejora del aprendizaje.
    """

    # Logging del prompt para depuración
    logging.debug(f"Prompt generado: {prompt}")
    
    # Selección del modelo de LLM para obtener el feedback
    if llm_model == 'ollama':
        logging.debug("Feedback generado usando el modelo 'ollama'")
        return get_ollama_feedback(prompt)
    elif llm_model == 'anthropic':
        logging.debug("Feedback generado usando el modelo 'anthropic'")
        return get_anthropic_feedback(prompt)
    elif llm_model == 'gemini':
        logging.debug("Feedback generado usando el modelo 'gemini'")
        return get_gemini_feedback(prompt)
    else:
        logging.error(f"Modelo LLM no soportado: {llm_model}")
        return "Modelo LLM no soportado."

def get_technical_pedagogical_report(context, llm_model):
    logging.debug("Generando prompt para el informe técnico-pedagógico")
    prompt = f"""
    Como experto en pedagogía y evaluación educativa, genera un informe técnico-pedagógico detallado para la evaluación
    "{context['evaluation_name']}" en el curso {context['course_name']}.
    
    Datos generales:
    - Total de estudiantes: {len(context['student_results'])}
    - Promedio general: {context['average_score']} de {context['max_score']}
    - Rango de calificaciones: {context['score_range']}
    
    Análisis estadístico por pregunta:
    """
    
    for question in context['question_stats']:
        prompt += f"""
        Pregunta ID: {question['id']}
        Pregunta: {question['text']}
        - Porcentaje de aciertos: {question['success_rate']}%
        - Respuestas más comunes: {question['common_answers']}
        - Dificultad observada: {question['difficulty_level']}
        
        ---
        """

    prompt += """
    Basándote en el marco de competencias del Ministerio de Educación Nacional (MEN) de Colombia, realiza un análisis 
    exhaustivo que incluya:

    1. Análisis general del grupo
    2. Competencias evaluadas según el MEN
    3. Nivel de logro por competencia (0-100)
    4. Plan de mejoramiento grupal

    Proporciona tu análisis en el siguiente formato JSON:
    {
        "group_analysis": {
            "summary": "Análisis general del desempeño del grupo",
            "average_score": "Promedio numérico",
            "key_findings": ["hallazgo1", "hallazgo2"],
            "general_recommendations": ["recomendación1", "recomendación2"]
        },
        "competency_analysis": [
            {
                "competency_name": "nombre de la competencia según MEN",
                "competency_description": "descripción de la competencia",
                "achievement_level": "nivel numérico (0-100)",
                "group_strengths": ["fortaleza1", "fortaleza2"],
                "group_challenges": ["desafío1", "desafío2"],
                "related_questions": [1, 2, 3],
                "improvement_strategies": ["estrategia1", "estrategia2"]
            }
        ],
        "question_analysis": [
            {
                "question_number": 1,
                "men_competencies": ["competencia1", "competencia2"],
                "success_rate": "porcentaje",
                "difficulty_analysis": "análisis de dificultad",
                "misconception_patterns": ["patrón1", "patrón2"],
                "teaching_recommendations": ["recomendación1", "recomendación2"]
            }
        ],
        "improvement_plan": {
            "priority_areas": ["área1", "área2"],
            "group_level_strategies": ["estrategia1", "estrategia2"],
            "recommended_resources": ["recurso1", "recurso2"],
            "success_indicators": ["indicador1", "indicador2"]
        }
    }
    
    El análisis debe ser riguroso, basado en evidencia y orientado a la mejora del proceso de enseñanza-aprendizaje grupal.
    """

    # Logging del prompt para depuración
    logging.debug(f"Prompt generado para informe técnico-pedagógico: {prompt}")
    
    # Selección del modelo de LLM
    if llm_model == 'ollama':
        logging.debug("Informe generado usando el modelo 'ollama'")
        return get_ollama_feedback(prompt)
    elif llm_model == 'anthropic':
        logging.debug("Informe generado usando el modelo 'anthropic'")
        return get_anthropic_feedback(prompt)
    elif llm_model == 'gemini':
        logging.debug("Informe generado usando el modelo 'gemini'")
        return get_gemini_feedback(prompt)
    else:
        logging.error(f"Modelo LLM no soportado: {llm_model}")
        return "Modelo LLM no soportado."

def get_gemini_feedback(prompt):
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(model='gemini-2.0-flash-exp', contents=prompt)
        
        # Get the raw text
        text = response.text
        
        # Remove any potential markdown code block formatting
        text = text.replace('```json\n', '').replace('\n```', '').strip()
        
        # Validate it's proper JSON
        try:
            json.loads(text)  # Test if it's valid JSON
            return text
        except json.JSONDecodeError:
            print(f"Invalid JSON from Gemini: {text}")
            return json.dumps({
                "overall_analysis": {
                    "summary": "Error: El feedback no se pudo generar correctamente.",
                    "score": "N/A",
                    "primary_strengths": [],
                    "primary_areas_for_improvement": []
                },
                "competency_analysis": [],
                "question_analysis": []
            })
            
    except Exception as e:
        print(f"Error making request to Gemini API: {e}")
        return json.dumps({
            "overall_analysis": {
                "summary": f"Error al conectar con el servicio de feedback: {str(e)}",
                "score": "N/A",
                "primary_strengths": [],
                "primary_areas_for_improvement": []
            },
            "competency_analysis": [],
            "question_analysis": []
        })

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
        
        # Get the raw text
        text = llm_response.get('response', '').strip()
        
        # Remove any potential markdown code block formatting
        text = text.replace('```json\n', '').replace('\n```', '').strip()
        
        # Validate it's proper JSON
        try:
            json.loads(text)  # Test if it's valid JSON
            return text
        except json.JSONDecodeError:
            print(f"Invalid JSON from Ollama: {text}")
            return json.dumps({
                "overall_analysis": {
                    "summary": "Error: El feedback no se pudo generar correctamente.",
                    "score": "N/A",
                    "primary_strengths": [],
                    "primary_areas_for_improvement": []
                },
                "competency_analysis": [],
                "question_analysis": []
            })
            
    except requests.RequestException as e:
        print(f"Error making request to Ollama: {e}")
        print(f"Exception details: {traceback.format_exc()}")
        return json.dumps({
            "overall_analysis": {
                "summary": f"Error al conectar con el servicio de feedback: {str(e)}",
                "score": "N/A",
                "primary_strengths": [],
                "primary_areas_for_improvement": []
            },
            "competency_analysis": [],
            "question_analysis": []
        })

def get_anthropic_feedback(prompt):
    try:
        response = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0,
            system="You are a Ph.D. in mathematics and science education with extensive experience in providing constructive feedback to K-12 students. Your goal is to offer responses that are both encouraging and informative, helping students to develop a deep understanding of mathematical and scientific concepts. When responding, consider the student's current level of knowledge, their potential misconceptions, and offer guidance that promotes critical thinking and problem-solving skills. Use language that is accessible to the student's grade level while ensuring that the feedback is rigorous and thought-provoking.",
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
        
        # Get the raw text
        text = response.content
        
        # Remove any potential markdown code block formatting
        text = text.replace('```json\n', '').replace('\n```', '').strip()
        
        # Validate it's proper JSON
        try:
            json.loads(text)  # Test if it's valid JSON
            return text
        except json.JSONDecodeError:
            print(f"Invalid JSON from Anthropic: {text}")
            return json.dumps({
                "overall_analysis": {
                    "summary": "Error: El feedback no se pudo generar correctamente.",
                    "score": "N/A",
                    "primary_strengths": [],
                    "primary_areas_for_improvement": []
                },
                "competency_analysis": [],
                "question_analysis": []
            })
            
    except Exception as e:
        print(f"Error making request to Anthropic API: {e}")
        return json.dumps({
            "overall_analysis": {
                "summary": f"Error al conectar con el servicio de feedback: {str(e)}",
                "score": "N/A",
                "primary_strengths": [],
                "primary_areas_for_improvement": []
            },
            "competency_analysis": [],
            "question_analysis": []
        })
