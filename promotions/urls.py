from django.urls import path

from .views import promotion_list

urlpatterns = [

    path(
        '',
        promotion_list,
        name='promotion_list'
    ),

]