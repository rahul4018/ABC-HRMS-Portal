from django.urls import path

from apps.employees.views import (
    payslip_list,
    payslip_detail,
)

urlpatterns = [

    path(
        '',
        payslip_list,
        name='payslip_list'
    ),

    path(
        '<int:pk>/',
        payslip_detail,
        name='payslip_detail'
    ),

]