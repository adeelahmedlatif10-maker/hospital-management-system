from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.stats_json, name='dashboard_stats'),
    
    path('logs/', views.logs_json, name='dashboard_logs'),
]
