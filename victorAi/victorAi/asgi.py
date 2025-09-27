import os
from django.core.asgi import get_asgi_application

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'victorAi.settings')

# Get Django ASGI application early to ensure Django is setup
django_asgi_app = get_asgi_application()

# Now import channels components
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from victorAiApp.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})