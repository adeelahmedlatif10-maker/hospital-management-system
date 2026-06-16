from django.urls import path
from . import views

urlpatterns = [
    path('bills/', views.bills_json, name='bills_json'),

    path('bills/stats/', views.bills_stats, name='bills_stats'),

    path('bills/add/', views.add_bill, name='add_bill'),

    path('bills/<int:bill_id>/paid/', views.mark_bill_paid, name='mark_bill_paid'),
    
    path('bills/delete/<int:bill_id>/', views.delete_bill, name='delete_bill'),
]