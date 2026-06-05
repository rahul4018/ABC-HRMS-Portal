import os
import csv

from datetime import date
from datetime import datetime
from django.http import HttpResponse
from reportlab.pdfgen import canvas

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from django.db.models import Count, Q

from django.http import HttpResponse
from decimal import Decimal, InvalidOperation

from reportlab.pdfgen import canvas
from django.conf import settings

from apps.leave.models import Leave
from apps.payslips.models import Payslip
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import A4

from .models import (
    Employee,
    Department,
    Attendance,
    Announcement,
    EmployeeDocument,
)

from .forms import (
    EmployeeCreateForm,
    EmployeeUpdateForm,
)

from apps.accounts.decorators import role_required

from reportlab.lib import colors

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Spacer,
    Paragraph,
    Image
)

from reportlab.lib.styles import getSampleStyleSheet


# ==========================================
# DASHBOARD
# ==========================================

@login_required
def dashboard(request):

    total_employees = Employee.objects.count()

    total_departments = Department.objects.count()

    total_attendance = Attendance.objects.count()

    total_announcements = Announcement.objects.count()

    active_employees = Employee.objects.filter(
        status='ACTIVE'
    ).count()

    pending_leaves = Leave.objects.filter(
        status='PENDING'
    ).count()

    context = {

        'total_employees': total_employees,

        'total_departments': total_departments,

        'total_attendance': total_attendance,

        'total_announcements': total_announcements,

        'active_employees': active_employees,

        'pending_leaves': pending_leaves,
    }

    return render(
        request,
        'dashboard/index.html',
        context
    )


# ==========================================
# EMPLOYEE MANAGEMENT
# ==========================================

@login_required
@role_required(['SUPERVISOR', 'SUPERVISOR'])
def employee_list(request):

    employees = Employee.objects.select_related(
        'user',
        'department'
    ).all()

    search_query = request.GET.get(
        'search'
    )

    department_filter = request.GET.get(
        'department'
    )

    status_filter = request.GET.get(
        'status'
    )

    if search_query:

        employees = employees.filter(

            Q(user__email__icontains=search_query) |

            Q(employee_id__icontains=search_query) |

            Q(designation__icontains=search_query)

        )

    if department_filter:

        employees = employees.filter(
            department__id=department_filter
        )

    if status_filter:

        employees = employees.filter(
            status=status_filter
        )

    departments = Department.objects.all()

    context = {

        'employees': employees,

        'departments': departments,

        'search_query': search_query,

        'department_filter': department_filter,

        'status_filter': status_filter,
    }

    return render(
        request,
        'employees/list.html',
        context
    )


@login_required
@role_required(['SUPERVISOR', 'SUPERVISOR'])
def export_employees_csv(request):

    response = HttpResponse(
        content_type='text/csv'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="employees.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'Employee ID',
        'Email',
        'Department',
        'Designation',
        'Status',
    ])

    employees = Employee.objects.select_related(
        'user',
        'department'
    ).all()

    for employee in employees:

        writer.writerow([

            employee.employee_id,

            employee.user.email,

            employee.department,

            employee.designation,

            employee.status,

        ])

    return response


@login_required
@role_required(['SUPERVISOR', 'SUPERVISOR'])
def employee_detail(request, pk):

    employee = get_object_or_404(
        Employee,
        pk=pk
    )

    context = {
        'employee': employee
    }

    return render(
        request,
        'employees/detail.html',
        context
    )


@login_required
@role_required(['SUPERVISOR', 'SUPERVISOR'])
def employee_add(request):

    form = EmployeeCreateForm()

    if request.method == 'POST':

        form = EmployeeCreateForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Employee created successfully.'
            )

            return redirect(
                'employee_list'
            )

    context = {
        'form': form
    }

    return render(
        request,
        'employees/add.html',
        context
    )


@login_required
@role_required(['SUPERVISOR', 'SUPERVISOR'])
def employee_edit(request, pk):

    employee = get_object_or_404(
        Employee,
        pk=pk
    )

    form = EmployeeUpdateForm(
        instance=employee
    )

    if request.method == 'POST':

        form = EmployeeUpdateForm(
            request.POST,
            request.FILES,
            instance=employee
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Employee updated successfully.'
            )

            return redirect(
                'employee_detail',
                pk=employee.pk
            )

    context = {
        'form': form,
        'employee': employee,
    }

    return render(
        request,
        'employees/edit.html',
        context
    )


@login_required
@role_required(['SUPERVISOR'])
def employee_delete(request, pk):

    employee = get_object_or_404(
        Employee,
        pk=pk
    )

    employee.delete()

    messages.success(
        request,
        'Employee deleted successfully.'
    )

    return redirect(
        'employee_list'
    )


# ==========================================
# MY PROFILE
# ==========================================

@login_required
@role_required([
    'SUPERVISOR',
    'SUPERVISOR',
    'EMPLOYEE'
])
def my_profile(request):

    employee = Employee.objects.filter(
        user=request.user
    ).first()

    context = {
        'employee': employee
    }

    return render(
        request,
        'employees/profile.html',
        context
    )


# ==========================================
# DEPARTMENT MANAGEMENT
# ==========================================

@login_required
@role_required(['SUPERVISOR', 'SUPERVISOR'])
def department_list(request):

    departments = Department.objects.annotate(
        employee_count=Count('employee')
    ).order_by('name')

    context = {
        'departments': departments
    }

    return render(
        request,
        'departments/list.html',
        context
    )


@login_required
@role_required(['SUPERVISOR', 'SUPERVISOR'])
def department_add(request):

    if request.method == 'POST':

        Department.objects.create(

            name=request.POST.get('name'),

            description=request.POST.get(
                'description'
            ),

            department_head=request.POST.get(
                'department_head'
            )

        )

        messages.success(
            request,
            'Department created successfully.'
        )

        return redirect(
            'department_list'
        )

    return render(
        request,
        'departments/add.html'
    )


@login_required
@role_required(['SUPERVISOR', 'SUPERVISOR'])
def department_edit(request, pk):

    department = get_object_or_404(
        Department,
        pk=pk
    )

    if request.method == 'POST':

        department.name = request.POST.get(
            'name'
        )

        department.description = request.POST.get(
            'description'
        )

        department.department_head = request.POST.get(
            'department_head'
        )

        department.save()

        messages.success(
            request,
            'Department updated successfully.'
        )

        return redirect(
            'department_list'
        )

    context = {
        'department': department
    }

    return render(
        request,
        'departments/edit.html',
        context
    )


@login_required
@role_required(['SUPERVISOR'])
def department_delete(request, pk):

    department = get_object_or_404(
        Department,
        pk=pk
    )

    if request.method == 'POST':

        department.delete()

        messages.success(
            request,
            'Department deleted successfully.'
        )

        return redirect(
            'department_list'
        )

    context = {
        'department': department
    }

    return render(
        request,
        'departments/delete.html',
        context
    )


# ==========================================
# PAYSLIP MANAGEMENT
# ==========================================

@login_required
def payslip_list(request):

    if request.user.role in ['SUPERVISOR', 'SUPERVISOR']:

        payslips = Payslip.objects.select_related(
            'employee',
            'employee__user'
        ).all()

    else:

        payslips = Payslip.objects.filter(
            employee__user=request.user
        )

    context = {
        'payslips': payslips
    }

    return render(
        request,
        'payslips/list.html',
        context
    )


@login_required
def payslip_detail(request, pk):

    payslip = get_object_or_404(
        Payslip,
        pk=pk
    )

    if (
        request.user.role == 'EMPLOYEE'
        and payslip.employee.user != request.user
    ):

        messages.error(
            request,
            'Access denied.'
        )

        return redirect(
            'payslip_list'
        )

    context = {
        'payslip': payslip
    }

    return render(
        request,
        'payslips/detail.html',
        context
    )
@login_required
def create_payslip(request):
    if request.user.role != 'SUPERVISOR':
        messages.error(
            request,
            'Access denied.'
        )
        return redirect(
            'payslip_list'
        )

    employees = Employee.objects.select_related(
        'user'
    ).all()

    if request.method == 'POST':
        employee = get_object_or_404(
            Employee,
            id=request.POST.get('employee')
        )

        # 1. Cleaner parsing: Fallback to string '0' or '30' so Decimal/int conversion never crashes
        def get_decimal(field_name):
            val = request.POST.get(field_name, '0').strip()
            try:
                return Decimal(val if val != '' else '0')
            except InvalidOperation:
                return Decimal('0')

        basic_salary = get_decimal('basic_salary')
        hra = get_decimal('hra')
        conveyance = get_decimal('conveyance')
        special_allowance = get_decimal('special_allowance')
        bonus = get_decimal('bonus')

        pf = get_decimal('pf')
        esi = get_decimal('esi')
        professional_tax = get_decimal('professional_tax')
        income_tax = get_decimal('income_tax')
        other_deduction = get_decimal('other_deduction')

        days_in_month = int(request.POST.get('days_in_month') or 30)
        effective_work_days = int(request.POST.get('effective_work_days') or 30)
        lop = int(request.POST.get('lop') or 0)

        # 2. Let the Payslip model handle gross_salary, total_deductions, and net_salary calculations!
        try:
            Payslip.objects.create(
                employee=employee,
                month=request.POST.get('month'),
                year=request.POST.get('year'),
                days_in_month=days_in_month,
                effective_work_days=effective_work_days,
                lop=lop,
                basic_salary=basic_salary,
                hra=hra,
                conveyance=conveyance,
                special_allowance=special_allowance,
                bonus=bonus,
                pf=pf,
                esi=esi,
                professional_tax=professional_tax,
                income_tax=income_tax,
                other_deduction=other_deduction
                # Notice: gross_salary, total_deductions, and net_salary are omitted.
                # The model's save() method will generate them accurately.
            )
            
            messages.success(
                request,
                'Payslip generated successfully.'
            )
        except Exception as e:
            # Catching duplicate records if unique_together constraint is violated
            messages.error(
                request,
                f'Error generating payslip: {e}'
            )

        return redirect(
            'payslip_list'
        )

    return render(
        request,
        'payslips/create.html',
        {
            'employees': employees
        }
    )

# ==========================================
# ATTENDANCE MANAGEMENT
# ==========================================

@login_required
def attendance_list(request):

    if request.user.role in ['SUPERVISOR', 'SUPERVISOR']:

        attendances = Attendance.objects.select_related(
            'employee',
            'employee__user'
        ).all()

    else:

        employee = Employee.objects.filter(
            user=request.user
        ).first()

        attendances = Attendance.objects.filter(
            employee=employee
        )

    context = {
        'attendances': attendances
    }

    return render(
        request,
        'attendance/list.html',
        context
    )


@login_required
def mark_attendance(request):

    employee = Employee.objects.filter(
        user=request.user
    ).first()

    if not employee:

        messages.error(
            request,
            'Employee profile not found.'
        )

        return redirect(
            'attendance_list'
        )

    today = date.today()

    attendance = Attendance.objects.filter(
        employee=employee,
        date=today
    ).first()

    if request.method == 'POST':

        current_time = datetime.now().time()

        if not attendance:

            Attendance.objects.create(
                employee=employee,
                date=today,
                check_in=current_time,
                status='PRESENT'
            )

            messages.success(
                request,
                'Check-in successful.'
            )

        elif not attendance.check_out:

            attendance.check_out = current_time

            attendance.save()

            messages.success(
                request,
                'Check-out successful.'
            )

        else:

            messages.warning(
                request,
                'Attendance already completed today.'
            )

        return redirect(
            'attendance_list'
        )

    context = {
        'attendance': attendance
    }

    return render(
        request,
        'attendance/mark.html',
        context
    )


@login_required
def attendance_detail(request, pk):

    attendance = get_object_or_404(
        Attendance,
        pk=pk
    )

    context = {
        'attendance': attendance
    }

    return render(
        request,
        'attendance/detail.html',
        context
    )


# ==========================================
# ANNOUNCEMENT MANAGEMENT
# ==========================================

@login_required
def announcement_list(request):

    announcements = Announcement.objects.filter(
        is_active=True
    )

    context = {
        'announcements': announcements
    }

    return render(
        request,
        'announcements/list.html',
        context
    )


@login_required
@role_required(['SUPERVISOR', 'SUPERVISOR'])
def announcement_add(request):

    if request.method == 'POST':

        Announcement.objects.create(

            title=request.POST.get('title'),

            message=request.POST.get('message'),

            created_by=request.user

        )

        messages.success(
            request,
            'Announcement published successfully.'
        )

        return redirect(
            'announcement_list'
        )

    return render(
        request,
        'announcements/add.html'
    )


@login_required
def announcement_detail(request, pk):

    announcement = get_object_or_404(
        Announcement,
        pk=pk
    )

    context = {
        'announcement': announcement
    }

    return render(
        request,
        'announcements/detail.html',
        context
    )


# ==========================================
# REPORTS & ANALYTICS
# ==========================================

@login_required
@role_required(['SUPERVISOR', 'SUPERVISOR'])
def reports_dashboard(request):

    total_employees = Employee.objects.count()

    total_departments = Department.objects.count()

    active_employees = Employee.objects.filter(
        status='ACTIVE'
    ).count()

    total_leaves = Leave.objects.count()

    pending_leaves = Leave.objects.filter(
        status='PENDING'
    ).count()

    attendance_today = Attendance.objects.filter(
        date=date.today()
    ).count()

    recent_announcements = Announcement.objects.all()[:5]

    departments = Department.objects.annotate(
        total=Count('employee')
    )

    context = {

        'total_employees': total_employees,

        'total_departments': total_departments,

        'active_employees': active_employees,

        'total_leaves': total_leaves,

        'pending_leaves': pending_leaves,

        'attendance_today': attendance_today,

        'recent_announcements': recent_announcements,

        'departments': departments,
    }

    return render(
        request,
        'reports/dashboard.html',
        context
    )

@login_required
def download_payslip_pdf(request, pk):
    payslip = get_object_or_404(
        Payslip,
        pk=pk
    )

    # Authorization Check
    if (
        request.user.role == 'EMPLOYEE'
        and payslip.employee.user != request.user
    ):
        messages.error(
            request,
            'Access denied.'
        )
        return redirect(
            'payslip_list'
        )

    # Initialize PDF Response
    response = HttpResponse(
        content_type='application/pdf'
    )
    response[
        'Content-Disposition'
    ] = f'attachment; filename="Payslip_{payslip.month}_{payslip.year}.pdf"'

    # Document Setup
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    elements = []

    # Custom Typography Styles
    center_title = ParagraphStyle(
        'CenterTitle',
        parent=styles['Title'],
        alignment=TA_CENTER
    )

    center_normal = ParagraphStyle(
        'CenterNormal',
        parent=styles['Normal'],
        alignment=TA_CENTER
    )

    center_heading = ParagraphStyle(
        'CenterHeading',
        parent=styles['Heading2'],
        alignment=TA_CENTER
    )

    # ==========================================
    # COMPANY LOGO
    # ==========================================
    logo_path = os.path.join(
        settings.BASE_DIR,
        'static',
        'images',
        'logo.png'
    )

    if os.path.exists(logo_path):
        logo = Image(
            logo_path,
            width=120,
            height=55
        )
        logo.hAlign = 'CENTER'
        elements.append(logo)

    # ==========================================
    # COMPANY HEADER
    # ==========================================
    elements.append(
        Paragraph(
            "<b>SKILL CHECK HUB IT SERVICES PVT. LTD.</b>",
            center_title
        )
    )
    elements.append(
        Paragraph(
            "Bengaluru, Karnataka - 560076",
            center_normal
        )
    )
    elements.append(
        Paragraph(
            "Email: hr@skillcheckhub.com | Phone: +91 XXXXX XXXXX",
            center_normal
        )
    )
    elements.append(
        Spacer(1, 10)
    )
    elements.append(
        Paragraph(
            f"<b>Payslip for {payslip.month} {payslip.year}</b>",
            center_heading
        )
    )
    elements.append(
        Spacer(1, 20)
    )

    # ==========================================
    # EMPLOYEE DETAILS
    # ==========================================
    employee_info = [
        [
            "Employee ID",
            payslip.employee.employee_id,
            "Department",
            str(payslip.employee.department)
        ],
        [
            "Employee Name",
            payslip.employee.user.email,
            "Designation",
            payslip.employee.designation
        ],
        [
            "Joining Date",
            str(payslip.employee.joining_date),
            "Location",
            payslip.employee.location
        ],
        [
            "Bank Name",
            payslip.employee.bank_name or "-",
            "Account Number",
            payslip.employee.account_number or "-"
        ],
        [
            "PAN Number",
            payslip.employee.pan_number or "-",
            "PF Number",
            payslip.employee.pf_number or "-"
        ],
        [
            "ESI Number",
            payslip.employee.esi_number or "-",
            "LOP",
            str(payslip.lop)
        ],
    ]

    # Total width budget = 520 (Letter width 560 - margins)
    employee_table = Table(
        employee_info,
        colWidths=[100, 160, 100, 160]
    )
    employee_table.setStyle(
        TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
    )
    elements.append(employee_table)
    elements.append(Spacer(1, 20))

    # ==========================================
    # SALARY BREAKDOWN
    # ==========================================
    salary_data = [
        [
            "EARNINGS",
            "AMOUNT",
            "DEDUCTIONS",
            "AMOUNT"
        ],
        [
            "Basic Salary",
            f"Rs. {payslip.basic_salary}",
            "PF",
            f"Rs. {payslip.pf}"
        ],
        [
            "HRA",
            f"Rs. {payslip.hra}",
            "ESI",
            f"Rs. {payslip.esi}"
        ],
        [
            "Conveyance",
            f"Rs. {payslip.conveyance}",
            "Professional Tax",
            f"Rs. {payslip.professional_tax}"
        ],
        [
            "Special Allowance",
            f"Rs. {payslip.special_allowance}",
            "Income Tax",
            f"Rs. {payslip.income_tax}"
        ],
        [
            "Bonus",
            f"Rs. {payslip.bonus}",
            "Other Deduction",
            f"Rs. {payslip.other_deduction}"
        ],
        [
            "Gross Salary",
            f"Rs. {payslip.gross_salary}",
            "Total Deductions",
            f"Rs. {payslip.total_deductions}"
        ],
    ]

    # Total width budget = 520 (130 + 130 + 130 + 130)
    salary_table = Table(
        salary_data,
        colWidths=[130, 130, 130, 130]
    )
    salary_table.setStyle(
        TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
    )
    elements.append(salary_table)
    elements.append(Spacer(1, 20))

    # ==========================================
    # NET SALARY
    # ==========================================
    net_salary_table = Table(
        [
            [
                "NET SALARY PAYABLE",
                f"Rs. {payslip.net_salary}"
            ]
        ],
        colWidths=[320, 200]
    )
    net_salary_table.setStyle(
        TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
    )
    elements.append(net_salary_table)
    elements.append(Spacer(1, 30))

    # ==========================================
    # FOOTER
    # ==========================================
    elements.append(
        Paragraph(
            "This is a computer generated payslip and does not require signature.",
            center_normal
        )
    )

    # Build PDF
    doc.build(elements)

    return response

# ==========================================
# DOCUMENT MANAGEMENT
# ==========================================

@login_required
def document_list(request):

    if request.user.role in ['SUPERVISOR', 'SUPERVISOR']:

        documents = EmployeeDocument.objects.select_related(
            'employee',
            'employee__user'
        ).all()

    else:

        employee = Employee.objects.filter(
            user=request.user
        ).first()

        documents = EmployeeDocument.objects.filter(
            employee=employee
        )

    context = {
        'documents': documents
    }

    return render(
        request,
        'documents/list.html',
        context
    )


@login_required
def upload_document(request):

    if request.user.role in ['SUPERVISOR', 'SUPERVISOR']:

        employees = Employee.objects.select_related(
            'user'
        ).all()

    else:

        employees = Employee.objects.filter(
            user=request.user
        )

    if request.method == 'POST':

        employee = get_object_or_404(
            Employee,
            id=request.POST.get('employee')
        )

        if (
            request.user.role == 'EMPLOYEE'
            and employee.user != request.user
        ):

            messages.error(
                request,
                'Access denied.'
            )

            return redirect(
                'document_list'
            )

        file = request.FILES.get('file')

        if not file:

            messages.error(
                request,
                'Please select a file.'
            )

            return redirect(
                'upload_document'
            )

        EmployeeDocument.objects.create(

            employee=employee,

            title=request.POST.get('title'),

            document_type=request.POST.get(
                'document_type'
            ),

            file=file,

            uploaded_by=request.user

        )

        messages.success(
            request,
            'Document uploaded successfully.'
        )

        return redirect(
            'document_list'
        )

    context = {
        'employees': employees
    }

    return render(
        request,
        'documents/upload.html',
        context
    )


@login_required
def delete_document(request, pk):

    document = get_object_or_404(
        EmployeeDocument,
        pk=pk
    )

    if (
        request.user.role == 'EMPLOYEE'
        and document.employee.user != request.user
    ):

        messages.error(
            request,
            'Access denied.'
        )

        return redirect(
            'document_list'
        )

    document.file.delete()

    document.delete()

    messages.success(
        request,
        'Document deleted successfully.'
    )

    return redirect(
        'document_list'
    )
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
# Assuming these are your custom decorators


@login_required
@role_required(['SUPERVISOR'])
def approve_document(request, pk):
    document = get_object_or_404(EmployeeDocument, pk=pk)
    document.status = 'APPROVED'
    document.save()
    
    messages.success(request, 'Document approved successfully.')
    return redirect('document_list')


@login_required
@role_required(['SUPERVISOR'])
def reject_document(request, pk):
    document = get_object_or_404(EmployeeDocument, pk=pk)
    document.status = 'REJECTED'
    document.save()
    
    messages.success(request, 'Document rejected successfully.')
    return redirect('document_list')


@login_required
@role_required(['SUPERVISOR'])
def send_back_document(request, pk):
    document = get_object_or_404(EmployeeDocument, pk=pk)
    document.status = 'SENT_BACK'
    document.save()
    
    messages.success(request, 'Document sent back for correction.')
    return redirect('document_list')