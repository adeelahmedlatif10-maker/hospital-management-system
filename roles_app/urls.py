from django.urls import path
from . import views

urlpatterns = [
    path('roles/add/',views.add_role, name = 'add_role'),

    path('roles/update-role/<int:id>/',views.update_role, name = 'update_role'),

    path('roles/delete-role/<int:id>/', views.delete_role,name = 'delete_role'),

    path('roles/json/', views.roles_json, name='roles_json'),

    path('roles/get-role/<int:id>/', views.get_role, name='get_role'),
]
