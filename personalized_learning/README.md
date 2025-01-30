# Personalized Learning
Este sistema está diseñado para crear una experiencia de aprendizaje altamente personalizada que:

- Se adapta al estilo de aprendizaje del estudiante
- Realiza seguimiento detallado del progreso
- Proporciona contenido relevante y adaptativo
- Ofrece apoyo mediante tutoría inteligente
- Evalúa y retroalimenta el progreso de forma continua

## LearningStyle (Estilo de Aprendizaje)
Objetivo: Registrar y gestionar el perfil de aprendizaje de cada estudiante
Almacena puntuaciones para diferentes estilos: visual, auditivo, kinestésico y lectura
Permite determinar el estilo dominante del estudiante para personalizar el contenido

## Competency (Competencia)
Objetivo: Definir las habilidades o conocimientos que se pueden adquirir
Permite crear una estructura jerárquica de competencias (competencias padre-hijo)
Base para el seguimiento del progreso del estudiante

## StudentCompetency (Competencia del Estudiante)
Objetivo: Hacer seguimiento del nivel de dominio del estudiante en cada competencia
Registra el nivel actual (0-100) y la última fecha de evaluación
Permite medir el progreso individual

## LearningPath (Ruta de Aprendizaje)
Objetivo: Crear planes personalizados de aprendizaje
Define objetivos específicos para cada competencia
Incluye recomendaciones adaptativas basadas en el perfil del estudiante
Realiza seguimiento del progreso hacia los objetivos

## LearningResource (Recurso de Aprendizaje)
Objetivo: Proporcionar contenido educativo en diversos formatos
Soporta múltiples tipos: Markdown, Video, PDF, Quiz, Proyecto
Asociado a competencias específicas
Incluye metadatos como dificultad y duración estimada

## LearningActivity (Actividad de Aprendizaje)
Objetivo: Registrar la interacción del estudiante con los recursos
Hace seguimiento del progreso y finalización de actividades
Permite recopilar retroalimentación

## ChatSession y ChatMessage (Sesión y Mensajes de Chat)
Objetivo: Facilitar la interacción con un sistema de tutoría inteligente
Mantiene el contexto de las conversaciones
Almacena el historial de interacciones y metadatos relacionados con el LLM

## CompetencyAssessment (Evaluación de Competencia)
Objetivo: Evaluar el dominio de competencias específicas
Integra retroalimentación automatizada mediante LLM
Proporciona recomendaciones personalizadas basadas en los resultados