from django.urls import path

from apps.employees.views import (
    document_list,
    upload_document,
    delete_document,
)

urlpatterns = [

    path(
        '',
        document_list,
        name='document_list'
    ),

    path(
        'upload/',
        upload_document,
        name='upload_document'
    ),

    path(
        '<int:pk>/delete/',
        delete_document,
        name='delete_document'
    ),

]