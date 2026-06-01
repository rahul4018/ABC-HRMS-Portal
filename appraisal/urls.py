from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.pmr_list,
        name='pmr_list'
    ),

    path(
        'create/',
        views.pmr_create,
        name='pmr_create'
    ),

    path(
        '<int:pk>/',
        views.pmr_detail,
        name='pmr_detail'
    ),

]