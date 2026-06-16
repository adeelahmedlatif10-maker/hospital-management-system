"""
URL configuration for hms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from patients_app import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    path('patients/', include('patients_app.urls')),
    path('roles/', include('roles_app.urls')),
    path('users/', include('users_app.urls')),
    path('doctors/', include('doctors_app.urls')),
    path('appointments/', include('appointments_app.urls')),
    path('payments/', include('payments_app.urls')),
    path('tests/', include('tests_app.urls')),
    path('labs/', include('labs_app.urls')),
    path('dashboard/',include('dashboard_app.urls')),
]