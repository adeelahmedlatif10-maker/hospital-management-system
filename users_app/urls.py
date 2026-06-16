from django.urls import path
from . import views

urlpatterns = [
    path('users/add-user/',views.add_user, name = 'add_user'),

    path('users/delete-user/<int:id>/',views.delete_user, name = 'delete_user'),

    path('users/get-user/<int:id>/',views.get_user, name = 'get_user'),

    path('users/update-user/<int:id>/',views.update_user, name = 'update_user'),

    path('users/json/', views.users_json, name='users_json'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),
]
