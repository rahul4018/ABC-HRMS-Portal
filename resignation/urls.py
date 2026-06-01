from django.urls import path

from .views import (
    resignation_list,
    apply_resignation,
    approve_resignation,
    reject_resignation,
)

urlpatterns = [

    path(
        '',
        resignation_list,
        name='resignation_list'
    ),

    path(
        'apply/',
        apply_resignation,
        name='apply_resignation'
    ),

    path(
        '<int:pk>/approve/',
        approve_resignation,
        name='approve_resignation'
    ),

    path(
        '<int:pk>/reject/',
        reject_resignation,
        name='reject_resignation'
    ),

]