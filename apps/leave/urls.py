from django.urls import path

from .views import (
    leave_list,
    apply_leave,
    leave_detail,
    approve_leave,
    reject_leave,
    request_leave_changes,
    cancel_leave,
    leave_balance,
    leave_calendar,
    holiday_list,
    holiday_add,
    leave_policy_list,
    leave_policy_update,
)

urlpatterns = [
    path('', leave_list, name='leave_list'),
    path('apply/', apply_leave, name='apply_leave'),
    path('<int:pk>/', leave_detail, name='leave_detail'),
    path('<int:pk>/approve/', approve_leave, name='approve_leave'),
    path('<int:pk>/reject/', reject_leave, name='reject_leave'),
    path('<int:pk>/request-changes/', request_leave_changes, name='request_leave_changes'),
    path('<int:pk>/cancel/', cancel_leave, name='cancel_leave'),

    path('balance/', leave_balance, name='leave_balance'),
    path('balance/<int:employee_id>/', leave_balance, name='employee_leave_balance'),
    path('calendar/', leave_calendar, name='leave_calendar'),

    path('holidays/', holiday_list, name='holiday_list'),
    path('holidays/add/', holiday_add, name='holiday_add'),

    path('policies/', leave_policy_list, name='leave_policy_list'),
    path('policies/<int:pk>/update/', leave_policy_update, name='leave_policy_update'),
]
