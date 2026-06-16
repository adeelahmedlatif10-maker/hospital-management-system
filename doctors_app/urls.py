from django.urls import path
from . import views

urlpatterns = [
    path('doctors/add-doctor/',views.add_doctor, name = 'add_doctor'),

    path('doctors/delete-doctor/<int:id>/',views.delete_doctor, name = 'delete_doctor'),

    path('doctors/update-doctors/<int:id>/',views.update_doctor, name = 'update_doctor'),

    path('doctors/json/', views.doctors_json, name='doctors_json'),
]
