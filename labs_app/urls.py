from django.urls import path
from . import views

urlpatterns = [
    path('laboratory/list-labs/',views.list_lab, name = 'list_lab'),
   
    path('laboratory/add-labs/', views.add_lab, name = 'add_lab'),

    path('laboratory/delete-labs/<int:id>/',views.delete_lab, name = 'delete_lab'),

    path('laboratory/get-labs/<int:id>/',views.get_lab, name = 'get_lab'),

    path('laboratory/update-labs/<int:id>/',views.update_lab, name = 'update_lab'),

    path('laboratory/search-labs/',views.search_lab, name = 'search_lab'),

    path('labs/json/', views.labs_json, name='labs_json'),
]
