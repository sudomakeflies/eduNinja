# ![eduNinja logo](statics/logo.svg) eduNinja
eduNinja es el resultado de varios años de investigación autogestionada y autofinanciada, emergiendo como un sistema integral de apoyo al aprendizaje personalizado. Centrado en un enfoque "evaluación-prioritaria" y "offline-first", eduNinja pone un fuerte énfasis en STEAM (Ciencia, Tecnología, Ingeniería, Artes y Matemáticas). Ofrece evaluaciones de opción múltiple optimizadas específicamente para matemáticas y ciencias, e incorpora un sistema de retroalimentación y recomendaciones asistido por inteligencia artificial, proporcionando una experiencia de aprendizaje adaptativa y eficaz.


## eduNinja-Evals
eduNinja-Evals facilita la creación y administración de evaluaciones de opción múltiple en matemáticas y ciencias (STEAM). Permite a los usuarios tomar evaluaciones con retroalimentación instantánea y utiliza un modelo de lenguaje de aprendizaje automático local para una retroalimentación adicional.

### Características:
Creación y gestión de cursos, preguntas y evaluaciones.
Toma de evaluaciones con retroalimentación instantánea.
Integración de modelo de lenguaje para retroalimentación via ollama or anthropic api.
Funcionalidad de inicio de sesión y registro de cuentas.
Renderizado latex para mejor calidad de ecuaciones.
Incluye banco de preguntas.

#### TODO
Personalized Learning system, right now is only a dummy implementation!

## eduNinja-PL
Personalized learning es un sistema de apoyo al aprendizaje a partir de unas preferencias declaradas por el usuario y un set de pruebas diagnosticas de manera apropiada permite recibir recomendaciones y feedback de modelos LLM's. 

## Instalación y Uso:
Instala Docker
Clona este repositorio: git clone https://github.com/sudomakeflies/eduNinja.git
cd eduNinja
docker-compose up --build

Lets explot it in localhost!

## Contribución:
¡Las contribuciones son bienvenidas! Si tienes ideas para nuevas características, correcciones de errores o mejoras en el código, siéntete libre de abrir un problema o enviar una solicitud de extracción.

## Licencia:
Este proyecto está licenciado bajo la Licencia GPLv3.
