from django.urls import path

from .views import (
    promotion_list,
    create_promotion
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

]