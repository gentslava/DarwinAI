from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html
from .models import CustomUser
from calls.models import Call

class CallsInline(admin.TabularInline):
    model = Call
    extra = 0
    readonly_fields = ('record', 'name', 'time', 'status', 'freq_hints', 'speed_podstr', 'loud_podstr', 'crit_words_count', 'neg_words_count', 'pos_operator', 'neg_operator', 'pos_client', 'neg_client', 'purity', 'interceptions', 'volume')
    
class UsersInline(admin.TabularInline):
    model = CustomUser
    extra = 0
    fields = ('last_name', 'first_name', 'department', 'product', 'critical', 'purity', 'script_following', 'speed_podstr', 'loud_podstr', 'crit_words_count', 'neg_words_count', 'pos_operator', 'neg_operator', 'pos_client', 'neg_client', 'limit', 'uploaded_amount')
    readonly_fields = ('last_name', 'first_name', 'department', 'product', 'critical', 'purity', 'script_following', 'speed_podstr', 'loud_podstr', 'crit_words_count', 'neg_words_count', 'pos_operator', 'neg_operator', 'pos_client', 'neg_client', 'limit', 'uploaded_amount')

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'company_link', 'last_name', 'first_name', 'supermanager_link', 'is_staff')
    list_display_links = ('id', 'last_name', 'first_name')
    inlines = [UsersInline, CallsInline]
    save_on_top = True
    save_as = True
    ordering = ('-company', 'id')
    fieldsets = (
        (None, {
            'fields': (
                'username',
                'email',
                'password'
            )
        }),
        (None, {
            'fields': (
                ('last_name', 'first_name'),
                'avatar'
            )
        }),
        ('Руководство', {
            'fields': (
                'company',
                'department',
                'product',
                'supermanager',
            )
        }),
        ('Словари', {
            'fields': (
                'scripts',
                'pos_words',
                'crit_words',
                'neg_words',
                'par_words',
                'client_pos_words',
                'client_neg_words'
            )
        }),
        ('Статистика', {
            'fields': (
                'critical',
                'purity',
                'speed_podstr',
                'loud_podstr',
                'crit_words_count',
                'neg_words_count',
                'pos_operator',
                'neg_operator',
                'pos_client',
                'neg_client',
            )
        }),
        ('Лимиты', {
            'fields': (
                'limit',
                'uploaded_amount'
            )
        }),
        ('Отображение общих параметров', {
            'fields': (
                'hide_speech_volume',
                'hide_script_following',
                'hide_loud_podstr',
                'hide_speed_podstr',
                'hide_speech_purity',
                'hide_interception',
                'hide_negative_words',
                'hide_positive_count',
                'hide_negative_count'
            )
        }),
        ('Параметры критического звонка', {
            'fields': (
                'critical_negative_emotions_client',
                'critical_negative_emotions_operator',
                'critical_speech_volume',
                'critical_script_following',
                'critical_loud_podstr',
                'critical_speed_podstr',
                'critical_speech_purity',
                'critical_interception_all',
                'critical_interception_avg',
                'critical_critical_words_all',
                'critical_critical_words_avg',
                'critical_negative_words_all',
                'critical_negative_words_avg',
                'critical_hints_count_all',
                'critical_hints_count_avg'
            )
        }),
        (None, {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser'
            )
        }),
        (None, {
            'fields': (
                'date_joined',
                'last_login'
            )
        }),
        (None, {
            'fields': (
                'user_permissions',
                'groups'
            )
        }),
    )
    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        try:
            if not request.user.id is 1:
                huser = qs.get(id = 30)
                return qs.exclude(id = huser.id).exclude(supermanager=huser)
        except CustomUser.DoesNotExist:
            None
        return qs
    
    def supermanager_link(self, obj):
        supermanager = obj.supermanager
        if supermanager:
            return format_html('<a href="{}/change/">{} {}</a>', supermanager.id, supermanager.last_name, supermanager.first_name)
        else:
            return format_html('<div>-</div>')
    supermanager_link.short_description = 'supermanager'
    supermanager_link.admin_order_field = 'supermanager'
    
    def company_link(self, obj):
        company = obj.company
        if company:
            return format_html('<a href="/admin/companies/company/{}/change/">{}</a>', company.id, company.name)
        else:
            return format_html('<div>-</div>')
    company_link.short_description = 'company'
    company_link.admin_order_field = 'company'
    