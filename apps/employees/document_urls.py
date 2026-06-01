from django.urls import path
from apps.employees.views import (
    document_list,
    upload_document,
    delete_document,
    approve_document,
    reject_document,
    send_back_document,
)

urlpatterns = [
    path('', document_list, name='document_list'),
    path('upload/', upload_document, name='upload_document'),
    path('<int:pk>/delete/', delete_document, name='delete_document'),
    path('<int:pk>/approve/', approve_document, name='approve_document'),
    path('<int:pk>/reject/', reject_document, name='reject_document'),
    path('<int:pk>/send-back/', send_back_document, name='send_back_document'),
]