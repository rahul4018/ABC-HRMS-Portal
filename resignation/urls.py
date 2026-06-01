from django.urls import path
from .views import (
    resignation_list,
    apply_resignation,
    resignation_detail,
    approve_resignation,
    reject_resignation,
    send_back_resignation,
)

urlpatterns = [
    path('', resignation_list, name='resignation_list'),
    path('apply/', apply_resignation, name='apply_resignation'),
    path('<int:pk>/', resignation_detail, name='resignation_detail'),
    path('<int:pk>/approve/', approve_resignation, name='approve_resignation'),
    path('<int:pk>/reject/', reject_resignation, name='reject_resignation'),
    path('<int:pk>/send-back/', send_back_resignation, name='send_back_resignation'),
]