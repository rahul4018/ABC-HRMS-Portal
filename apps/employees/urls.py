from apps.employees import views as employee_document_views
from django.urls import path

from .views import (
    # ==========================================
    # EMPLOYEE
    # ==========================================
    employee_list,
    employee_detail,
    employee_add,
    employee_profile_pdf,
    asset_list,
    asset_add,
    asset_detail,
    employee_edit,
    employee_delete,

    # ==========================================
    # PROFILE
    # ==========================================
    my_profile,
    my_profile_edit,
    profile_review_list,
    profile_review,

    # ==========================================
    # DEPARTMENTS
    # ==========================================
    department_list,
    department_add,
    department_edit,
    department_delete,

    # ==========================================
    # PAYSLIPS
    # ==========================================
    payslip_list,
    payslip_detail,
    download_payslip_pdf,

    # ==========================================
    # ATTENDANCE
    # ==========================================
    attendance_list,
    mark_attendance,

    # ==========================================
    # ANNOUNCEMENTS
    # ==========================================
    announcement_list,

    # ==========================================
    # REPORTS
    # ==========================================
    reports_dashboard,

    # ==========================================
    # DOCUMENTS
    # ==========================================
    document_list,
    upload_document,
    delete_document,

    # ==========================================
    # EXPORTS
    # ==========================================
    export_employees_csv,
)


urlpatterns = [

    # ==========================================
    # EMPLOYEE URLS
    # ==========================================

    path(
        '',
        employee_list,
        name='employee_list'
    ),

    path(
        'add/',
        employee_add,
        name='employee_add'
    ),

    path(
        'export/csv/',
        export_employees_csv,
        name='export_employees_csv'
    ),

    path(
        '<int:pk>/',
        employee_detail,
        name='employee_detail'
    ),

    path(
        '<int:pk>/edit/',
        employee_edit,
        name='employee_edit'
    ),

    path(
        '<int:pk>/delete/',
        employee_delete,
        name='employee_delete'
    ),

    # ==========================================
    # PROFILE
    # ==========================================

    path(
        'my-profile/',
        my_profile,
        name='my_profile'
    ),

    path(
        'my-profile/edit/',
        my_profile_edit,
        name='my_profile_edit'
    ),

    # ==========================================
    # HR PROFILE REVIEW
    # ==========================================

    path(
        'profile-review/',
        profile_review_list,
        name='profile_review_list'
    ),

    path(
        'profile-review/<int:pk>/',
        profile_review,
        name='profile_review'
    ),

    # ==========================================
    # DEPARTMENT URLS
    # ==========================================

    path(
        'departments/',
        department_list,
        name='department_list'
    ),

    path(
        'departments/add/',
        department_add,
        name='add_department'
    ),

    path(
        'departments/<int:pk>/edit/',
        department_edit,
        name='edit_department'
    ),

    path(
        'departments/<int:pk>/delete/',
        department_delete,
        name='delete_department'
    ),

    # ==========================================
    # PAYSLIP URLS
    # ==========================================

    path(
        'payslips/',
        payslip_list,
        name='payslip_list'
    ),

    path(
        'payslips/<int:pk>/',
        payslip_detail,
        name='payslip_detail'
    ),

    path(
        'payslips/<int:pk>/pdf/',
        download_payslip_pdf,
        name='download_payslip_pdf'
    ),

    # ==========================================
    # ATTENDANCE URLS
    # ==========================================

    path(
        'attendance/',
        attendance_list,
        name='attendance_list'
    ),

    path(
        'attendance/mark/',
        mark_attendance,
        name='mark_attendance'
    ),

    # ==========================================
    # ANNOUNCEMENT URLS
    # ==========================================

    path(
        'announcements/',
        announcement_list,
        name='announcement_list'
    ),

    # ==========================================
    # REPORTS URLS
    # ==========================================

    path(
        'reports/',
        reports_dashboard,
        name='reports_dashboard'
    ),

    # ==========================================
    # DOCUMENT URLS
    # ==========================================

    path(
        'documents/',
        document_list,
        name='document_list'
    ),

    path(
        'documents/upload/',
        upload_document,
        name='upload_document'
    ),

    path(
        'documents/<int:pk>/delete/',
        employee_document_views.delete_document,
        name='delete_document'
    ),

    # ==========================================
    # EMPLOYEE PROFILE PDF
    # ==========================================

    path(
        'employee/<int:pk>/profile-pdf/',
        employee_profile_pdf,
        name='employee_profile_pdf'
    ),

    # ==========================================
    # ASSET URLS
    # ==========================================

    path(
        'assets/',
        asset_list,
        name='asset_list'
    ),

    path(
        'assets/add/',
        asset_add,
        name='asset_add'
    ),

    path(
        'assets/<int:pk>/',
        asset_detail,
        name='asset_detail'
    ),

    # ==========================================
    # ENHANCED DOCUMENT MANAGEMENT
    # ==========================================

    path(
        'documents/<int:pk>/',
        employee_document_views.document_detail,
        name='document_detail'
    ),

    path(
        'documents/<int:pk>/download/',
        employee_document_views.download_document,
        name='download_document'
    ),

    path(
        'documents/<int:pk>/replace/',
        employee_document_views.replace_document,
        name='replace_document'
    ),
]
