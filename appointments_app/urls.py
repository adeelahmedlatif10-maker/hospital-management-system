from django.urls import path
from . import views

urlpatterns = [
    path('appointments/book-appointment/',views.book_appointment, name = 'book_appointment'),

    path('appointments/delete-appointment/<int:id>/',views.delete_appointment, name = 'delete_appointment'),

    path('appointments/get-appointment/<int:id>/',views.get_appointment, name = 'get_appointment'),

    path('appointments/update-appointment/<int:id>/',views.update_appoitnment, name = 'update_appointment'),

    path('appointments/json/', views.appointments_json, name='appointments_json'),
    
    path('appointments/today/json/', views.appointments_today_json, name='appointments_today_json'),
]