from django.urls import path

from .views import (
    resignation_list,
    apply_resignation,
)

urlpatterns = [

    path(
        "",
        resignation_list,
        name="resignation_list"
    ),

    path(
        "apply/",
        apply_resignation,
        name="apply_resignation"
    ),

]