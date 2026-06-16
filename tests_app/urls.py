from django.urls import path
from . import views

urlpatterns = [
    path('test/add-tests/',views.add_test, name = 'add_test'),

    path('test/delete-test/<int:id>/',views.delete_test, name = 'delete_test'),

    path('test/get-tests/<int:id>/',views.get_test, name = 'get_test'),

    path('test/update-tests/<int:id>/',views.update_test, name = 'update_test'),

    path('test/json/', views.tests_json, name='tests_json'),

    path('records/add-records/',views.add_test_record, name = 'add_test_record'),

    path('records/delete-records/<int:id>/',views.delete_record, name = 'delete_record'),

    path('records/get-records/<int:id>/',views.get_record, name = 'get_record'),

    path('records/update-records/<int:id>/',views.update_record, name = 'update_record'),

    path('records/json/', views.records_json, name='records_json'),
]