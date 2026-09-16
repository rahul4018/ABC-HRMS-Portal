from django.urls import path
from . import views

app_name = 'workforce'

urlpatterns = [
    path('', views.workforce_home, name='home'),
    path('organization/', views.organization, name='organization'),
    path('employee/<int:pk>/360/', views.employee_360, name='employee_360'),
    path('exit/', views.exit_list, name='exit_list'),
    path('exit/new/', views.exit_create, name='exit_create'),
    path('exit/<int:pk>/', views.exit_detail, name='exit_detail'),
    path('exit/<int:pk>/<str:action>/', views.exit_action, name='exit_action'),
    path('clearance/<int:pk>/', views.clearance_update, name='clearance_update'),
    path('exit-interview/<int:pk>/', views.interview_update, name='interview_update'),
    path('settlement/<int:pk>/', views.settlement_update, name='settlement_update'),
    path('exit/<int:pk>/document/<str:document_type>/', views.exit_document, name='exit_document'),
    path('requests/', views.request_list, name='request_list'),
    path('requests/new/', views.request_create, name='request_create'),
]
