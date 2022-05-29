from django.contrib import admin
from .models import Company
from users.models import CustomUser

class ManagersInline(admin.TabularInline):
    model = CustomUser
    extra = 0
    fields = ('last_name', 'first_name', 'department')
    readonly_fields = ('last_name', 'first_name')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    inlines = [ManagersInline]
    fieldsets = (
        (None, {
            'fields': (
                'name',
            )
        }),
        (None, {
            'fields': (
                'balance_minutes',
                'balance_seconds'
            )
        }),
        (None, {
            'fields': (
                'limit',
                'uploaded_amount'
            )
        }),
    )
