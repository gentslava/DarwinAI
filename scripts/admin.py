from django.contrib import admin
from .models import Script

@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
