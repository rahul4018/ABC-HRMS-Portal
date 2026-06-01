from django.urls import path
from .views import (
    leave_list,
    apply_leave,
    leave_detail,
    approve_leave,
    reject_leave,
)

urlpatterns = [
    path('', leave_list, name='leave_list'),
    path('apply/', apply_leave, name='apply_leave'),
    path('<int:pk>/', leave_detail, name='leave_detail'),
    path('<int:pk>/approve/', approve_leave, name='approve_leave'),
    path('<int:pk>/reject/', reject_leave, name='reject_leave'),
]