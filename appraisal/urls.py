from django.urls import path

from .views import (
    pmr_list,
    pmr_create,
    pmr_detail,
    pmr_approve,
    pmr_reject,
    pmr_send_back,
)

urlpatterns = [

    path(
        "",
        pmr_list,
        name="pmr_list"
    ),

    path(
        "create/",
        pmr_create,
        name="pmr_create"
    ),

    path(
        "<int:pk>/",
        pmr_detail,
        name="pmr_detail"
    ),

    path(
        "<int:pk>/approve/",
        pmr_approve,
        name="pmr_approve"
    ),

    path(
        "<int:pk>/reject/",
        pmr_reject,
        name="pmr_reject"
    ),

    path(
        "<int:pk>/send-back/",
        pmr_send_back,
        name="pmr_send_back"
    ),

]