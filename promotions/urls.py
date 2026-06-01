from django.urls import path

from .views import (
    promotion_list,
    create_promotion,
    approve_promotion,
    reject_promotion,
)

urlpatterns = [

    path(
        '',
        promotion_list,
        name='promotion_list'
    ),

    path(
        'create/',
        create_promotion,
        name='create_promotion'
    ),

    path(
        '<int:pk>/approve/',
        approve_promotion,
        name='approve_promotion'
    ),

    path(
        '<int:pk>/reject/',
        reject_promotion,
        name='reject_promotion'
    ),

]