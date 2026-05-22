from django.contrib import admin
from django.urls import path
from django.shortcuts import render


def dashboard(request):
    return render(request, 'dashboard/index.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
]