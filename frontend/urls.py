from django.urls import path, include
from django.conf.urls import url
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', views.index, name = 'dashboard'),
    path('critical-calls/', views.index),
    
    path('managers/', views.analytics, name = 'managers'),
    
    path('manager-<manager_id>/calls/', views.calls),
    path('manager-<manager_id>/upload/', views.calls),
    path('manager-<manager_id>/remove/', views.calls),
    
    path('manager-<manager_id>/post_analyze/<salt>/', views.post_analyze),
    
    path('manager-<manager_id>/real_time/<salt>/', views.real_time),
    
    path('dictionaries/', views.dictionaries, name = 'dictionaries'),
    path('dictionaries/words-list/', views.dictionaries),
    
    path('scripts/', views.scripts, name = 'scripts'),
    path('scripts/words-list/', views.scripts),
    path('scripts/add/', views.scripts),
    path('scripts/delete/<script_id>/', views.scripts),
    
    path('settings/', views.settings, name = 'settings'),
    
    path('team/', views.team, name="team"),
    path('managers-list/', views.team),
    path('team/add/', views.team),
    path('team/delete/<type>/<data>/', views.team),
    
    path('login/', views.login_view, name = 'login'),
    path('logout/', views.logout_view, name = 'logout'),
    
    path('registr/', views.registration_view),
    path('recalc/', views.recalc_view),
    path('migrate/', views.migrate_view),
#     path('accounts/', views.registration_view),
    
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico'), name = 'favicon'),
]