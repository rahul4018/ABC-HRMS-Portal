from django.urls import path

from apps.employees.views import (
    attendance_list,
    mark_attendance,
    attendance_detail,
)

urlpatterns = [

    path(
        '',
        attendance_list,
        name='attendance_list'
    ),

    path(
        'mark/',
        mark_attendance,
        name='mark_attendance'
    ),

    path(
        '<int:pk>/',
        attendance_detail,
        name='attendance_detail'
    ),

]