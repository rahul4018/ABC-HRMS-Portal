from django.urls import path

from apps.employees.views import (
    announcement_list,
    announcement_add,
    announcement_detail,
)

urlpatterns = [

    path(
        '',
        announcement_list,
        name='announcement_list'
    ),

    path(
        'add/',
        announcement_add,
        name='announcement_add'
    ),

    path(
        '<int:pk>/',
        announcement_detail,
        name='announcement_detail'
    ),

]