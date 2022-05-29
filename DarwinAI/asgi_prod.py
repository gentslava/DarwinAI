# DarwinAI/asgi.py
import os
import yaml
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DarwinAI.settings_prod')
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter, URLRouter

application = ProtocolTypeRouter({
  "http": AsgiHandler(),
#   "websocket":
})