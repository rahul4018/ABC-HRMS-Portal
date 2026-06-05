from django.urls import path

from apps.employees.views import (
    payslip_list,
    payslip_detail,
    download_payslip_pdf,
    create_payslip,
)

urlpatterns = [

    path(
        '',
        payslip_list,
        name='payslip_list'
    ),

    path(
        'create/',
        create_payslip,
        name='create_payslip'
    ),

    path(
        '<int:pk>/',
        payslip_detail,
        name='payslip_detail'
    ),

    path(
        '<int:pk>/pdf/',
        download_payslip_pdf,
        name='download_payslip_pdf'
    ),

]