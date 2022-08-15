"""
ASGI config for musma project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack

from users.routing import ws_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'musma.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app, #http://
    'websocket': AuthMiddlewareStack(URLRouter(ws_urlpatterns)) #ws://
})

