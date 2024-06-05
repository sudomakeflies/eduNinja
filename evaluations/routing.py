# routing.py

from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from evaluations.consumers import FeedbackConsumer

websocket_urlpatterns = [
    path('ws/feedback/', FeedbackConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
    'channel': ChannelNameRouter({
        'feedback_channel': FeedbackConsumer,
    }),
})
