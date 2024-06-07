# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from openai import OpenAI
# #from evaluations.models import Answer
# from django.contrib.auth import get_user_model
# from channels.layers import get_channel_layer
# from asgiref.sync import sync_to_async


# class FeedbackConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_group_name = "feedback_channel"  # Nombre del canal al que se suscribirá este consumidor
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         await self.generate_feedback(data)

#     async def generate_feedback(self, data):
#         User = get_user_model()
#         channel_layer = get_channel_layer()
#         client = OpenAI(base_url="http://localhost:1234/v1", api_key="your_api_key")
#         completion = client.chat.completions.create(
#             model="QuantFactory/Meta-Llama-3-8B-Instruct-GGUF",
#             messages=[
#                 {"role": "system", "content": "Responde con un texto corto conciso de nivel de un profesor Ph.D. en ciencias de la educación proporcionando retroalimentación detallada sobre los exámenes de mis estudiantes. Incluye sugerencias específicas para mejorar, refuerza los conceptos clave y aborda cualquier malentendido común. Además, proporciona ejemplos prácticos y estrategias de estudio personalizadas. Asegúrate de mantener un tono alentador y motivador para apoyar el crecimiento académico de los estudiantes."},
#                 {"role": "user", "content": data["response"]}
#             ],
#             temperature=0.7,
#         )
#         feedback = completion.choices[0].message
#         answer_id = data['answer_id']
#         await self.update_answer_feedback(answer_id, feedback)

#     @sync_to_async
#     def update_answer_feedback(self, answer_id, feedback):
#         from .models import Answer  # Esto aún se necesita para la llamada sync_to_async
#         answer = Answer.objects.get(id=answer_id)
#         answer.feedback = feedback
#         answer.save()