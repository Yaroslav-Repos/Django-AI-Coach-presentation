import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django_AI_Coach_presentation.settings')

django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from analyzer.middleware import JWTAuthMiddleware
from analyzer.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})