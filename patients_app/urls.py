from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_patient, name='add_patient'),

    path('patients/delete/<int:id>/', views.del_patient, name='delete_patient'),

    path('patients/update/<int:id>/', views.update_patient, name='update_patient'),

    path('patients/json/', views.patients_json, name='patients_json'),
]