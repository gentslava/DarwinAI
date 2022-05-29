"""
Definition of urls for DarwinAI.
"""
import debug_toolbar
from django.conf.urls.static import static
from django.conf import settings

from datetime import datetime
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.routers import DefaultRouter
"""
Действие определяется http методом:
GET: list,
POST: create,
PUT: update,
DELETE: destroy
"""

urlpatterns = [
    path('', include('frontend.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('admin/', admin.site.urls),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static('export/', document_root=settings.EXPORT_ROOT)