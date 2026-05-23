from django.urls import path

from .views import (
    leave_list,
    apply_leave,
    leave_detail,
)

urlpatterns = [

    path(
        '',
        leave_list,
        name='leave_list'
    ),

    path(
        'apply/',
        apply_leave,
        name='apply_leave'
    ),

    path(
        '<int:pk>/',
        leave_detail,
        name='leave_detail'
    ),
]