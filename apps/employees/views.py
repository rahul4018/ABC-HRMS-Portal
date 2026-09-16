import calendar
import os
import mimetypes
import csv
import re

from datetime import date
from datetime import datetime
from django.http import HttpResponse
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.utils import timezone

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from apps.leave.models import Leave
from .models import Asset
from .forms import AssetForm
from apps.payslips.models import Payslip
from apps.accounts.models import CompanySettings

from .models import (
    Employee,
    Department,
    Attendance,
    Announcement,
    EmployeeDocument,
    Asset,
    EmployeeLifecycle
)

from apps.employees.models import Attendance

from apps.employees.models import EmployeeDocument


from django.core.paginator import Paginator
from django.db.models import Count, Q

from django.http import HttpResponse
from decimal import Decimal, InvalidOperation

from reportlab.pdfgen import canvas
from django.conf import settings

from apps.leave.models import Leave
from apps.payslips.models import Payslip
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.pagesizes import A4
from apps.leave.models import Leave

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
    MyProfileUpdateForm,
)

from apps.accounts.decorators import role_required

from reportlab.lib import colors

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Spacer,
    Paragraph,
    Image,
    HRFlowable,

)

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet


# ==========================================
# DASHBOARD
# ==========================================

@login_required
def dashboard(request):

    employee = Employee.objects.filter(user=request.user).first()

    if employee and not _employee_can_access_dashboard(employee):
        messages.warning(
            request,
            'Please complete your profile and wait for HR approval before accessing the dashboard.'
        )
        return redirect('my_profile_edit')

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
@role_required(['SUPERVISOR'])
def employee_list(request):
    """
    HR/Supervisor employee directory with:
    - Search by name, email, employee ID, or designation
    - Department and status filters
    - Page size selector: 10 / 20 / 50
    - Pagination
    - Active/inactive summary counts
    """
    employees = (
        Employee.objects
        .select_related('user', 'department')
        .all()
        .order_by('employee_id')
    )

    # -----------------------------
    # Search
    # -----------------------------
    search_query = request.GET.get('search', '').strip()

    if search_query:
        employees = employees.filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(user__email__icontains=search_query)
            | Q(employee_id__icontains=search_query)
            | Q(designation__icontains=search_query)
        )

    # -----------------------------
    # Department filter
    # -----------------------------
    department_filter = request.GET.get('department', '').strip()

    if department_filter:
        employees = employees.filter(
            department_id=department_filter
        )

    # -----------------------------
    # Status filter
    # -----------------------------
    status_filter = request.GET.get('status', '').strip()

    if status_filter:
        employees = employees.filter(
            status=status_filter
        )

    # -----------------------------
    # Employment type filter
    # -----------------------------
    employment_type_filter = request.GET.get(
        'employment_type',
        ''
    ).strip()

    if employment_type_filter:
        employees = employees.filter(
            employment_type=employment_type_filter
        )

    # -----------------------------
    # Summary counts
    # -----------------------------
    total_employees = Employee.objects.count()

    active_employees = Employee.objects.filter(
        status='ACTIVE'
    ).count()

    inactive_employees = Employee.objects.filter(
        status='INACTIVE'
    ).count()

    contractor_count = Employee.objects.filter(
        employment_type='CONTRACT'
    ).count()

    # Leadership accounts are represented by dedicated employee IDs.
    leadership_count = Employee.objects.filter(
        employee_id__regex=r'^(CEO|CTO|CFO|HR)[0-9]+$'
    ).count()

    # -----------------------------
    # Page size: 10 / 20 / 50
    # Default = 10
    # -----------------------------
    allowed_page_sizes = (10, 20, 50)

    try:
        page_size = int(
            request.GET.get('page_size', '10')
        )
    except (TypeError, ValueError):
        page_size = 10

    if page_size not in allowed_page_sizes:
        page_size = 10

    # -----------------------------
    # Pagination
    # -----------------------------
    paginator = Paginator(
        employees,
        page_size
    )

    page_number = request.GET.get('page', '1')
    page_obj = paginator.get_page(page_number)

    departments = Department.objects.all().order_by('name')

    context = {
        'employees': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,

        'departments': departments,

        'search_query': search_query,
        'department_filter': department_filter,
        'status_filter': status_filter,
        'employment_type_filter': employment_type_filter,

        'page_size': page_size,

        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': inactive_employees,
        'contractor_count': contractor_count,
        'leadership_count': leadership_count,
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
        'Employee Name',
        'Email',
        'Department',
        'Designation',
        'Employment Type',
        'Joining Date',
        'Status',
    ])

    employees = Employee.objects.select_related(
        'user',
        'department'
    ).all()

    for employee in employees:

        writer.writerow([

            employee.employee_id,

            employee.user.get_full_name().strip() or employee.user.email,

            employee.user.email,

            employee.department,

            employee.designation,

            employee.employment_type,

            employee.joining_date,

            employee.status,

        ])

    return response


@login_required
@role_required(['SUPERVISOR'])  # Cleaned up the duplicate role declaration
def employee_detail(request, pk):
    employee = get_object_or_404(
        Employee,
        pk=pk
    )

    # Profile Completion Logic
    profile_fields = [
        employee.phone,
        employee.address,
        employee.date_of_birth,
        employee.gender,
        employee.bank_name,
        employee.account_number,
        employee.pan_number,
        employee.aadhaar_number,
        employee.emergency_contact_name,
        employee.emergency_contact_number,
    ]

    completed_fields = sum(
        1 for field in profile_fields
        if field is not None and str(field).strip() != ""
    )

    total_fields = len(profile_fields)

    completion_percentage = (
        int((completed_fields / total_fields) * 100)
        if total_fields > 0 else 0
    )
    attendance_count = Attendance.objects.filter(
            employee=employee
            ).count()
    document_count = EmployeeDocument.objects.filter(
        employee=employee
        ).count()
    payslip_count = Payslip.objects.filter(
        employee=employee
        ).count()
    recent_leaves = Leave.objects.filter(
        employee=employee
        ).order_by('-applied_at')[:5]
    leave_count = Leave.objects.filter(
        employee=employee
        ).count()
    approved_leave_count = Leave.objects.filter(
        employee=employee,
        status='APPROVED'
        ).count()
    pending_leave_count = Leave.objects.filter(
        employee=employee,
        status='PENDING'
        ).count()
    
    asset_count = Asset.objects.filter(
        assigned_to=employee
        ).count()
    lifecycle = EmployeeLifecycle.objects.filter(
        employee=employee
        ).first()

    timeline = []
    for attendance in Attendance.objects.filter(
        employee=employee
        ).order_by('-date')[:5]:

        timeline.append({
            'date': attendance.date,
            'event': 'Attendance Marked',
            'description': attendance.status
            })
        for document in EmployeeDocument.objects.filter(
            employee=employee
            ).order_by('-uploaded_at')[:5]:

            timeline.append({
                'date': document.uploaded_at,
                'event': 'Document Uploaded',
                'description': document.title
                })
            
            for payslip in Payslip.objects.filter(
                employee=employee
                ).order_by('-generated_at')[:5]:

                timeline.append({
                    'date': payslip.generated_at,
                    'event': 'Payslip Generated',
                    'description': f"{payslip.month} {payslip.year}"
                    })
                
                for leave in Leave.objects.filter(
                    employee=employee
                    ).order_by('-applied_at')[:5]:

                    timeline.append({
                        'date': leave.applied_at,
                        'event': 'Leave Applied',
                        'description': leave.get_leave_type_display()})
                    
                    timeline = sorted(
                        timeline,
                        key=lambda x: x['date'],
                        reverse=True
                        )[:15]
                       

    # Context Data Fetching (Matches the updated 360 UI Template)
    context = {
        'employee': employee,
        'timeline': timeline,
        'lifecycle': lifecycle,
        'asset_count': asset_count,
        'completion_percentage': completion_percentage,
        'attendance_count': attendance_count,
        'document_count': document_count,
        'recent_leaves': recent_leaves,
        'leave_count': leave_count,
        'approved_leave_count': approved_leave_count,
        'pending_leave_count': pending_leave_count,
        'payslip_count': payslip_count,
        
        'recent_attendance': Attendance.objects.filter(
            employee=employee
        ).order_by('-date')[:10],  # Added sorting by recent date if applicable

        'recent_documents': EmployeeDocument.objects.filter(
            employee=employee
        )[:10],

        'recent_payslips': Payslip.objects.filter(
            employee=employee
        ).order_by('-year', '-id')[:5],  # Ensures chronological order for stats

        'recent_leaves': Leave.objects.filter(
            employee=employee
        ).order_by('-id')[:5],  # Added Missing Section 3: Leave Summary
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
        'form': form,
        'departments': Department.objects.all().order_by('name'),
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
@login_required
def employee_profile_pdf(request, pk):
    employee = get_object_or_404(
        Employee,
        pk=pk
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = (
        f'attachment; filename="Employee_{employee.employee_id}.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    elements = []

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
            width=140,
            height=70
        )
        logo.hAlign = 'CENTER'
        elements.append(logo)

    # ==========================================
    # COMPANY HEADER
    # ==========================================
    title_style = ParagraphStyle(
        'CompanyTitle',
        parent=styles['Title'],
        alignment=1
    )

    normal_center = ParagraphStyle(
        'NormalCenter',
        parent=styles['Normal'],
        alignment=1
    )

    company = CompanySettings.objects.first()
    company_name = company.company_name if company else "ABC HRMS Portal"
    company_address = company.company_address if company else "Bengaluru, Karnataka"
    company_email = company.company_email if company else "admin@ABC HRMS Portal.com"
    company_phone = company.company_phone if company else "9999999999"

    elements.append(
        Paragraph(company_name, title_style)
    )

    elements.append(
        Paragraph(company_address, normal_center)
    )

    elements.append(
        Paragraph(f"{company_email} | {company_phone}", normal_center)
    )

    elements.append(
        Spacer(1, 15)
    )

    elements.append(
        Paragraph(
            "<b>EMPLOYEE PROFILE REPORT</b>",
            title_style
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    # ==========================================
    # PRIVACY COMPLIANCE MASKING
    # ==========================================
    raw_aadhaar = str(employee.aadhaar_number).strip() if employee.aadhaar_number else ""
    if raw_aadhaar and raw_aadhaar != "-":
        # Format display securely (Masking first 8 characters, showing final 4)
        clean_aadhaar = raw_aadhaar.replace(" ", "").replace("-", "")
        if len(clean_aadhaar) >= 4:
            masked_aadhaar = f"XXXX-XXXX-{clean_aadhaar[-4:]}"
        else:
            masked_aadhaar = "[Aadhaar Omitted]"
    else:
        masked_aadhaar = "-"

    # ==========================================
    # EMPLOYEE DATA TABLE
    # ==========================================
    data = [
        ["Employee ID", employee.employee_id],
        ["Employee Name", employee.user.get_full_name().strip() or employee.user.email],
        ["Work Email", employee.user.email],
        ["Department", str(employee.department) if employee.department else "-"],
        ["Designation", employee.designation],
        ["Phone", employee.phone or "-"],
        ["Location", employee.location or "-"],
        ["Date of Birth", employee.date_of_birth or "-"],
        ["Gender", employee.gender or "-"],
        ["Joining Date", str(employee.joining_date)],
        ["Employment Type", employee.employment_type or "-"],
        ["Work Mode", employee.work_mode or "-"],
        ["Reporting Manager", employee.reporting_manager or "-"],
        ["Salary", f"₹ {employee.salary}"],
        ["PAN Number", employee.pan_number or "-"],
        ["Aadhaar Number", masked_aadhaar],
        ["Passport Number", employee.passport_number or "-"],
        ["PF Number", employee.pf_number or "-"],
        ["ESI Number", employee.esi_number or "-"],
        ["UAN Number", employee.uan_number or "-"],
        ["Bank Name", employee.bank_name or "-"],
        ["Account Holder Name", employee.account_holder_name or (employee.user.get_full_name().strip() or "-")],
        ["IFSC Code", employee.ifsc_code or "-"],
        ["Account Number", _mask_account_number(employee.account_number)],
        ["Emergency Contact", employee.emergency_contact_name or "-"],
        ["Emergency Number", employee.emergency_contact_number or "-"],
        ["Emergency Relation", employee.emergency_contact_relation or "-"],
        ["Address", employee.address or "-"]
    ]

    table = Table(
        data,
        colWidths=[180, 320]
    )

    table.setStyle(
        TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (1, 0), (-1, -1), [colors.white, colors.whitesmoke]),
        ])
    )

    elements.append(table)
    elements.append(Spacer(1, 20))

    # ==========================================
    # FOOTER
    # ==========================================
    elements.append(
        Paragraph(
            f"Generated On: {timezone.now().strftime('%d-%b-%Y %I:%M %p')}",
            styles['Italic']
        )
    )

    elements.append(
        Spacer(1, 10)
    )

    elements.append(
        Paragraph(
            "This is a system generated employee profile and does not require signature.",
            styles['Italic']
        )
    )

    doc.build(elements)
    return response


# ==========================================
# MY PROFILE / EMPLOYEE ONBOARDING
# ==========================================

def _employee_profile_needs_setup(employee):
    """
    Return True when an employee must complete or submit
    their mandatory profile information before normal access.
    """
    return bool(
        employee
        and getattr(employee, 'profile_status', None)
        in {'PROFILE_PENDING', 'PROFILE_SUBMITTED', 'HR_REVIEW'}
    )


def _employee_can_access_dashboard(employee):
    """
    Normal employee dashboard access is allowed only after HR approval.
    Older Employee rows without the onboarding field are treated as active
    for backward compatibility.
    """
    if not employee:
        return True

    profile_status = getattr(employee, 'profile_status', None)

    if profile_status is None:
        return True

    return profile_status == 'ACTIVE'


@login_required
@role_required([
    'SUPERVISOR',
    'EMPLOYEE',
])
def my_profile(request):
    employee = (
        Employee.objects
        .select_related('user', 'department', 'reporting_manager')
        .filter(user=request.user)
        .first()
    )

    if not employee:
        messages.error(
            request,
            'Employee profile not found.'
        )
        return redirect('dashboard')

    profile_status = getattr(
        employee,
        'profile_status',
        'ACTIVE',
    )

    context = {
        'employee': employee,
        'profile_status': profile_status,
        'profile_pending': profile_status == 'PROFILE_PENDING',
        'profile_submitted': profile_status == 'PROFILE_SUBMITTED',
        'hr_review': profile_status == 'HR_REVIEW',
        'profile_approved': profile_status == 'ACTIVE',
    }

    return render(
        request,
        'employees/profile.html',
        context
    )


# ==========================================
# MY PROFILE EDIT / ONBOARDING
# ==========================================

@login_required
@role_required([
    'SUPERVISOR',
    'EMPLOYEE',
])
def my_profile_edit(request):
    employee = (
        Employee.objects
        .select_related('user', 'department', 'reporting_manager')
        .filter(user=request.user)
        .first()
    )

    if not employee:
        messages.error(
            request,
            'Employee profile not found.'
        )
        return redirect('dashboard')

    profile_status = getattr(
        employee,
        'profile_status',
        'ACTIVE',
    )

    # Once the employee submits the profile, HR owns the review.
    if profile_status in {'PROFILE_SUBMITTED', 'HR_REVIEW'}:
        messages.info(
            request,
            'Your profile has already been submitted and is currently under HR review.'
        )
        return redirect('my_profile')

    if profile_status == 'ACTIVE':
        # Existing active employees may still use the same self-service
        # page to update their personal information.
        pass

    if request.method == 'POST':
        form = MyProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=employee
        )

        if form.is_valid():
            form.save()

            # First profile completion moves the employee into the HR queue.
            if hasattr(employee, 'profile_status'):
                employee.profile_status = 'PROFILE_SUBMITTED'
                employee.profile_submitted_at = timezone.now()
                employee.save(
                    update_fields=[
                        'profile_status',
                        'profile_submitted_at',
                        'updated_at',
                    ]
                )

            messages.success(
                request,
                'Your profile has been submitted successfully. HR will review it before dashboard access is enabled.'
            )

            return redirect('my_profile')
    else:
        form = MyProfileUpdateForm(
            instance=employee
        )

    return render(
        request,
        'employees/my_profile_edit.html',
        {
            'form': form,
            'employee': employee,
            'profile_status': profile_status,
            'is_onboarding': profile_status == 'PROFILE_PENDING',
        }
    )


# ==========================================
# HR PROFILE REVIEW / APPROVAL
# ==========================================

@login_required
@role_required(['SUPERVISOR'])
def profile_review_list(request):
    """
    HR queue for employee profiles waiting for review.
    """
    employees = (
        Employee.objects
        .select_related('user', 'department')
        .filter(
            profile_status__in=[
                'PROFILE_SUBMITTED',
                'HR_REVIEW',
            ]
        )
        .order_by(
            'profile_submitted_at',
            'employee_id',
        )
    )

    pending_count = Employee.objects.filter(
        profile_status='PROFILE_SUBMITTED'
    ).count()

    review_count = Employee.objects.filter(
        profile_status='HR_REVIEW'
    ).count()

    approved_count = Employee.objects.filter(
        profile_status='ACTIVE'
    ).count()

    return render(
        request,
        'employees/profile_review_list.html',
        {
            'employees': employees,
            'pending_count': pending_count,
            'review_count': review_count,
            'approved_count': approved_count,
        }
    )


@login_required
@role_required(['SUPERVISOR'])
def profile_review(request, pk):
    """
    HR can review the submitted employee profile.

    HR may update only statutory fields here:
    - PF Number
    - UAN Number
    - ESI Number

    HR can then approve the profile, which changes the profile status
    to ACTIVE and unlocks normal dashboard access.
    """
    employee = get_object_or_404(
        Employee.objects.select_related(
            'user',
            'department',
            'reporting_manager',
        ),
        pk=pk,
    )

    profile_status = getattr(
        employee,
        'profile_status',
        'ACTIVE',
    )

    if profile_status == 'PROFILE_SUBMITTED':
        employee.profile_status = 'HR_REVIEW'
        employee.save(
            update_fields=[
                'profile_status',
                'updated_at',
            ]
        )
        profile_status = 'HR_REVIEW'

    if request.method == 'POST':
        action = request.POST.get('action', 'save').strip().lower()

        employee.pf_number = (
            request.POST.get('pf_number', '').strip()
            or None
        )
        employee.uan_number = (
            request.POST.get('uan_number', '').strip()
            or None
        )
        employee.esi_number = (
            request.POST.get('esi_number', '').strip()
            or None
        )

        if action == 'approve':
            employee.profile_status = 'ACTIVE'

            employee.save(
                update_fields=[
                    'pf_number',
                    'uan_number',
                    'esi_number',
                    'profile_status',
                    'updated_at',
                ]
            )

            messages.success(
                request,
                f'{employee.employee_id} profile has been approved successfully.'
            )

            return redirect(
                'profile_review_list'
            )

        employee.save(
            update_fields=[
                'pf_number',
                'uan_number',
                'esi_number',
                'updated_at',
            ]
        )

        messages.success(
            request,
            f'{employee.employee_id} statutory information has been updated.'
        )

        return redirect(
            'profile_review',
            pk=employee.pk,
        )

    context = {
        'employee': employee,
        'profile_status': profile_status,
        'profile_submitted_at': getattr(
            employee,
            'profile_submitted_at',
            None,
        ),
    }

    return render(
        request,
        'employees/profile_review.html',
        context,
    )


# ==========================================
# DEPARTMENT MANAGEMENT
# ==========================================
@login_required
@role_required(['SUPERVISOR'])
def department_list(request):
    departments = Department.objects.select_related('head_employee', 'head_employee__user').annotate(
        employee_count=Count('employee')
    ).order_by('name')

    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    if query:
        departments = departments.filter(
            Q(name__icontains=query)
            | Q(code__icontains=query)
            | Q(description__icontains=query)
            | Q(head_employee__user__first_name__icontains=query)
            | Q(head_employee__user__last_name__icontains=query)
        )

    if status in {'ACTIVE', 'INACTIVE'}:
        departments = departments.filter(status=status)

    total_departments = Department.objects.count()
    active_departments = Department.objects.filter(status='ACTIVE').count()
    unassigned_heads = Department.objects.filter(head_employee__isnull=True, status='ACTIVE').count()
    total_employees = Employee.objects.filter(status='ACTIVE').count()

    return render(request, 'departments/list.html', {
        'departments': departments,
        'query': query,
        'selected_status': status,
        'total_departments': total_departments,
        'active_departments': active_departments,
        'unassigned_heads': unassigned_heads,
        'total_employees': total_employees,
    })


@login_required
@role_required(['SUPERVISOR'])
def department_add(request):
    employees = Employee.objects.select_related('user', 'department').filter(status='ACTIVE').order_by('user__first_name', 'user__last_name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        code = request.POST.get('code', '').strip().upper()
        head_id = request.POST.get('head_employee', '').strip()
        status = request.POST.get('status', 'ACTIVE').strip()

        if not name:
            messages.error(request, 'Department name is required.')
        elif Department.objects.filter(name__iexact=name).exists():
            messages.error(request, 'A department with this name already exists.')
        elif code and Department.objects.filter(code__iexact=code).exists():
            messages.error(request, 'A department with this code already exists.')
        else:
            head = Employee.objects.filter(pk=head_id, status='ACTIVE').first() if head_id else None
            Department.objects.create(
                name=name,
                code=code or None,
                description=description,
                head_employee=head,
                department_head=(head.user.get_full_name().strip() if head else ''),
                status=status if status in {'ACTIVE', 'INACTIVE'} else 'ACTIVE',
            )
            messages.success(request, 'Department created successfully.')
            return redirect('department_list')

    return render(request, 'departments/add.html', {'employees': employees})


@login_required
@role_required(['SUPERVISOR'])
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    employees = Employee.objects.select_related('user', 'department').filter(status='ACTIVE').order_by('user__first_name', 'user__last_name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        code = request.POST.get('code', '').strip().upper()
        head_id = request.POST.get('head_employee', '').strip()
        status = request.POST.get('status', 'ACTIVE').strip()

        duplicate_name = Department.objects.filter(name__iexact=name).exclude(pk=department.pk).exists()
        duplicate_code = code and Department.objects.filter(code__iexact=code).exclude(pk=department.pk).exists()

        if not name:
            messages.error(request, 'Department name is required.')
        elif duplicate_name:
            messages.error(request, 'A department with this name already exists.')
        elif duplicate_code:
            messages.error(request, 'A department with this code already exists.')
        else:
            head = Employee.objects.filter(pk=head_id, status='ACTIVE').first() if head_id else None
            department.name = name
            department.code = code or None
            department.description = description
            department.head_employee = head
            department.department_head = head.user.get_full_name().strip() if head else ''
            department.status = status if status in {'ACTIVE', 'INACTIVE'} else 'ACTIVE'
            department.save()
            messages.success(request, 'Department updated successfully.')
            return redirect('department_detail', pk=department.pk)

    return render(request, 'departments/edit.html', {
        'department': department,
        'employees': employees,
    })


@login_required
@role_required(['SUPERVISOR'])
def department_detail(request, pk):
    department = get_object_or_404(
        Department.objects.select_related('head_employee', 'head_employee__user'),
        pk=pk,
    )
    employees = Employee.objects.select_related('user', 'department').filter(department=department).order_by(
        'user__first_name', 'user__last_name'
    )
    active_count = employees.filter(status='ACTIVE').count()
    inactive_count = employees.filter(status='INACTIVE').count()

    return render(request, 'departments/detail.html', {
        'department': department,
        'employees': employees,
        'active_count': active_count,
        'inactive_count': inactive_count,
    })


@login_required
@role_required(['SUPERVISOR'])
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        department.status = 'INACTIVE'
        department.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'{department.name} has been deactivated.')
        return redirect('department_list')

    return render(request, 'departments/delete.html', {'department': department})

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
        messages.error(request, 'Access denied.')
        return redirect('payslip_list')

    employees = Employee.objects.select_related('user', 'department').order_by('employee_id')

    if request.method == 'POST':
        employee = get_object_or_404(Employee, id=request.POST.get('employee'))

        def get_decimal(field_name):
            val = request.POST.get(field_name, '0').strip()
            try:
                return Decimal(val if val else '0')
            except InvalidOperation:
                return Decimal('0')

        def get_int(field_name, default=0):
            try:
                return int(request.POST.get(field_name) or default)
            except (TypeError, ValueError):
                return default

        try:
            Payslip.objects.create(
                employee=employee,
                payslip_number=request.POST.get('payslip_number') or None,
                month=request.POST.get('month'),
                year=get_int('year', timezone.localdate().year),
                pay_date=request.POST.get('pay_date') or timezone.localdate(),
                payment_mode=request.POST.get('payment_mode') or 'BANK_TRANSFER',
                days_in_month=get_int('days_in_month', 30),
                effective_work_days=get_int('effective_work_days', 30),
                lop=get_int('lop', 0),
                basic_salary=get_decimal('basic_salary'),
                hra=get_decimal('hra'),
                conveyance=get_decimal('conveyance'),
                special_allowance=get_decimal('special_allowance'),
                overtime=get_decimal('overtime'),
                bonus=get_decimal('bonus'),
                other_earnings=get_decimal('other_earnings'),
                pf=get_decimal('pf'),
                esi=get_decimal('esi'),
                professional_tax=get_decimal('professional_tax'),
                income_tax=get_decimal('income_tax'),
                lop_deduction=get_decimal('lop_deduction'),
                other_deduction=get_decimal('other_deduction'),
                employer_pf=get_decimal('employer_pf'),
                employer_esi=get_decimal('employer_esi'),
                employer_other=get_decimal('employer_other'),
            )
            messages.success(request, 'Payslip generated successfully.')
        except Exception as e:
            messages.error(request, f'Error generating payslip: {e}')
        return redirect('payslip_list')

    return render(request, 'payslips/create.html', {
        'employees': employees,
        'today': timezone.localdate(),
    })

# ==========================================
# ATTENDANCE MANAGEMENT
# ==========================================


def _attendance_manager(request):
    """Return True when the user may view organization-wide attendance."""
    role = getattr(request.user, 'role', None)
    portal_role = getattr(request.user, 'portal_role', None)
    return role in {'SUPERVISOR', 'CEO', 'HR_ADMIN'} or portal_role in {
        'ADMIN', 'CEO', 'HR', 'FOUNDER'
    }


def _attendance_metrics(attendance):
    """Attach display-only payroll/attendance metrics to a record."""
    from datetime import datetime as _datetime

    ABCeduled_in = attendance.ABCeduled_check_in
    ABCeduled_out = attendance.ABCeduled_check_out
    attendance.late_minutes = 0
    attendance.overtime_minutes = 0
    attendance.work_minutes = 0

    if attendance.check_in:
        start = _datetime.combine(attendance.date, attendance.check_in)
        ABCeduled_start = _datetime.combine(attendance.date, ABCeduled_in)
        attendance.late_minutes = max(0, int((start - ABCeduled_start).total_seconds() // 60))

        if attendance.check_out:
            end = _datetime.combine(attendance.date, attendance.check_out)
            attendance.work_minutes = max(0, int((end - start).total_seconds() // 60))
            ABCeduled_end = _datetime.combine(attendance.date, ABCeduled_out)
            attendance.overtime_minutes = max(0, int((end - ABCeduled_end).total_seconds() // 60))

    h, minutes = divmod(attendance.work_minutes, 60)
    attendance.hours_display = f"{h}h {minutes:02d}m" if attendance.work_minutes else "--"
    attendance.late_display = f"{attendance.late_minutes} min" if attendance.late_minutes else "On time"
    attendance.overtime_display = f"{attendance.overtime_minutes} min" if attendance.overtime_minutes else "--"
    return attendance


def _attendance_queryset(request):
    qs = Attendance.objects.select_related(
        'employee', 'employee__user', 'employee__department'
    ).all()

    if not _attendance_manager(request):
        employee = Employee.objects.filter(user=request.user).first()
        if employee:
            qs = qs.filter(employee=employee)
        else:
            qs = qs.none()

    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    department = request.GET.get('department', '').strip()
    date_filter = request.GET.get('date', '').strip()
    month = request.GET.get('month', '').strip()

    if query:
        qs = qs.filter(
            Q(employee__user__first_name__icontains=query)
            | Q(employee__user__last_name__icontains=query)
            | Q(employee__user__email__icontains=query)
            | Q(employee__employee_id__icontains=query)
        )
    if status:
        qs = qs.filter(status=status)
    if department:
        qs = qs.filter(employee__department_id=department)
    if date_filter:
        qs = qs.filter(date=date_filter)
    if month and len(month) == 7:
        try:
            year, month_no = [int(v) for v in month.split('-')]
            qs = qs.filter(date__year=year, date__month=month_no)
        except ValueError:
            pass

    return qs


@login_required
def attendance_list(request):
    from apps.leave.models import Leave as LeaveModel

    attendances = list(_attendance_queryset(request))
    for attendance in attendances:
        _attendance_metrics(attendance)

    today = timezone.localdate()
    active_employees = Employee.objects.filter(status='ACTIVE')
    if not _attendance_manager(request):
        employee = Employee.objects.filter(user=request.user).first()
        if employee:
            active_employees = active_employees.filter(pk=employee.pk)

    today_records = list(
        Attendance.objects.filter(date=today, employee__in=active_employees)
    )
    present_today = sum(1 for a in today_records if a.status == 'PRESENT')
    half_day_today = sum(1 for a in today_records if a.status == 'HALF_DAY')
    late_today = sum(1 for a in today_records if _attendance_metrics(a).late_minutes > 0)

    on_leave_today = LeaveModel.objects.filter(
        employee__in=active_employees,
        status='APPROVED',
        start_date__lte=today,
        end_date__gte=today,
    ).values('employee_id').distinct().count()

    absent_today = max(
        active_employees.count() - present_today - half_day_today - on_leave_today,
        0
    )

    overtime_minutes = sum(
        _attendance_metrics(a).overtime_minutes for a in today_records
    )

    departments = Department.objects.order_by('name')
    context = {
        'attendances': attendances,
        'departments': departments,
        'is_manager': _attendance_manager(request),
        'today': today,
        'total_employees': active_employees.count(),
        'present_today': present_today,
        'absent_today': absent_today,
        'on_leave_today': on_leave_today,
        'half_day_today': half_day_today,
        'late_today': late_today,
        'overtime_today': overtime_minutes,
        'filters': request.GET,
    }

    return render(request, 'attendance/list.html', context)


@login_required
def mark_attendance(request):
    employee = Employee.objects.filter(user=request.user).first()

    if not employee:
        messages.error(request, 'Employee profile not found.')
        return redirect('attendance_list')

    today = timezone.localdate()
    attendance = Attendance.objects.filter(employee=employee, date=today).first()

    if request.method == 'POST':
        current_time = timezone.localtime().time().replace(microsecond=0)

        if not attendance:
            Attendance.objects.create(
                employee=employee,
                date=today,
                check_in=current_time,
                ABCeduled_check_in=datetime.strptime('09:00', '%H:%M').time(),
                ABCeduled_check_out=datetime.strptime('18:00', '%H:%M').time(),
                shift_name='GENERAL',
                attendance_source='WEB',
                status='PRESENT',
            )
            messages.success(request, 'Check-in successful.')
        elif not attendance.check_out:
            attendance.check_out = current_time
            attendance.save()
            messages.success(request, 'Check-out successful.')
        else:
            messages.warning(request, 'Attendance already completed today.')

        return redirect('attendance_list')

    if attendance:
        _attendance_metrics(attendance)

    return render(request, 'attendance/mark.html', {
        'attendance': attendance,
        'today': today,
    })


@login_required
def attendance_detail(request, pk):
    attendance = get_object_or_404(
        Attendance.objects.select_related(
            'employee', 'employee__user', 'employee__department'
        ), pk=pk
    )

    if not _attendance_manager(request) and attendance.employee.user != request.user:
        messages.error(request, 'You do not have permission to view this attendance record.')
        return redirect('attendance_list')

    _attendance_metrics(attendance)

    return render(request, 'attendance/detail.html', {
        'attendance': attendance,
        'is_manager': _attendance_manager(request),
    })


@login_required
def attendance_monthly(request):
    """Monthly attendance calendar for HR or the logged-in employee."""
    today = timezone.localdate()
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
        if not 1 <= month <= 12:
            raise ValueError
    except (TypeError, ValueError):
        year, month = today.year, today.month

    if _attendance_manager(request):
        employee_id = request.GET.get('employee', '').strip()
        employees = Employee.objects.select_related('user', 'department').filter(status='ACTIVE').order_by('user__first_name')
        employee = employees.filter(pk=employee_id).first() if employee_id else employees.first()
    else:
        employees = Employee.objects.select_related('user', 'department').filter(user=request.user)
        employee = employees.first()

    records = {}
    if employee:
        for item in Attendance.objects.filter(
            employee=employee,
            date__year=year,
            date__month=month,
        ):
            _attendance_metrics(item)
            records[item.date.day] = item

    days = []
    for day in range(1, calendar.monthrange(year, month)[1] + 1):
        record = records.get(day)
        days.append({
            'date': date(year, month, day),
            'record': record,
        })

    summary = {
        'present': sum(1 for r in records.values() if r.status == 'PRESENT'),
        'half_day': sum(1 for r in records.values() if r.status == 'HALF_DAY'),
        'absent': sum(1 for r in records.values() if r.status == 'ABSENT'),
        'late': sum(1 for r in records.values() if r.late_minutes > 0),
        'overtime_minutes': sum(r.overtime_minutes for r in records.values()),
    }

    return render(request, 'attendance/monthly.html', {
        'employee': employee,
        'employees': employees,
        'days': days,
        'summary': summary,
        'year': year,
        'month': month,
        'month_name': date(year, month, 1).strftime('%B %Y'),
        'is_manager': _attendance_manager(request),
    })


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

def _mask_account_number(value):
    value = str(value or '').strip()
    if not value:
        return '-'
    digits = re.sub(r'\s+', '', value)
    if len(digits) <= 4:
        return digits
    return 'X' * (len(digits) - 4) + digits[-4:]


def _amount_words(number):
    # Indian numbering wording for common payroll amounts.
    ones = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
            'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
            'Seventeen', 'Eighteen', 'Nineteen']
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']

    def below_thousand(n):
        parts = []
        if n >= 100:
            parts += [ones[n // 100], 'Hundred']
            n %= 100
            if n:
                parts.append('and')
        if n >= 20:
            parts.append(tens[n // 10])
            if n % 10:
                parts.append(ones[n % 10])
        elif n:
            parts.append(ones[n])
        return ' '.join(parts)

    try:
        value = Decimal(str(number)).quantize(Decimal('0.01'))
    except Exception:
        return '-'
    integer = int(value)
    paise = int((value - integer) * 100)
    if integer == 0:
        result = 'Zero'
    else:
        result_parts = []
        crore, integer = divmod(integer, 10_000_000)
        lakh, integer = divmod(integer, 100_000)
        thousand, integer = divmod(integer, 1_000)
        if crore: result_parts += [below_thousand(crore), 'Crore']
        if lakh: result_parts += [below_thousand(lakh), 'Lakh']
        if thousand: result_parts += [below_thousand(thousand), 'Thousand']
        if integer: result_parts.append(below_thousand(integer))
        result = ' '.join(result_parts)
    if paise:
        return f"Rupees {result} and {below_thousand(paise)} Paise Only"
    return f"Rupees {result} Only"


@login_required
def download_payslip_pdf(request, pk):
    payslip = get_object_or_404(
        Payslip.objects.select_related(
            'employee',
            'employee__user',
            'employee__department'
        ),
        pk=pk
    )

    if (
        getattr(request.user, 'role', None) == 'EMPLOYEE'
        and payslip.employee.user != request.user
    ):
        messages.error(request, 'Access denied.')
        return redirect('payslip_list')

    response = HttpResponse(content_type='application/pdf')

    safe_month = re.sub(
        r'[^A-Za-z0-9_-]+',
        '',
        str(payslip.month)
    )

    response['Content-Disposition'] = (
        f'attachment; filename="Payslip_{safe_month}_{payslip.year}.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=28,
        leftMargin=28,
        topMargin=24,
        bottomMargin=24
    )

    styles = getSampleStyleSheet()
    elements = []

    company = CompanySettings.objects.first()
    company_address = (
        'Demo Corporate Office, India'
    )
    company_phone = '+91 1234567890'
    company_email = 'hr@ABC HRMS Portal.com'
    company_contact = ParagraphStyle(
        'CorporateCompanyContact',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#555555')
    )

    payslip_title = ParagraphStyle(
        'CorporatePayslipTitle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#111827'),
        spaceBefore=6,
        spaceAfter=10
    )

    section_heading = ParagraphStyle(
        'CorporateSectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10,
        textColor=colors.HexColor('#111827')
    )

    body = ParagraphStyle(
        'CorporateBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=10.5,
        textColor=colors.HexColor('#1f2937')
    )

    label = ParagraphStyle(
        'CorporateLabel',
        parent=body,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#374151')
    )

    amount = ParagraphStyle(
        'CorporateAmount',
        parent=body,
        alignment=TA_RIGHT
    )

    total_label = ParagraphStyle(
        'CorporateTotal',
        parent=body,
        fontName='Helvetica-Bold'
    )

    net_label = ParagraphStyle(
        'CorporateNetLabel',
        parent=body,
        fontName='Helvetica-Bold',
        fontSize=9.5
    )

    net_value = ParagraphStyle(
        'CorporateNetValue',
        parent=body,
        alignment=TA_RIGHT,
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=17,
        textColor=colors.HexColor('#0f5132')
    )

    words_style = ParagraphStyle(
        'CorporateWords',
        parent=body,
        fontSize=8.5,
        leading=11
    )

    footer_style = ParagraphStyle(
        'CorporateFooter',
        parent=company_contact,
        fontSize=7.5,
        leading=9
    )

    logo_path = os.path.join(
        settings.BASE_DIR,
        'static',
        'images',
        'logo.png'
    )

    if os.path.exists(logo_path):
        logo = Image(
            logo_path,
            width=125,
            height=55
        )
        logo.hAlign = 'CENTER'
        elements.append(logo)

    elements.append(
        Paragraph(
            f'{company_address}<br/>Phone: {company_phone}  |  Email: {company_email}',
            company_contact
        )
    )

    elements.append(Spacer(1, 7))

    elements.append(
        Paragraph(
            f'<b>PAYSLIP — {payslip.month} {payslip.year}</b>',
            payslip_title
        )
    )


    def _payslip_amount(value):
        try:
            amount = Decimal(str(value or 0))
            return 'NIL' if amount == 0 else f'Rs. {amount:,.2f}'
        except Exception:
            return 'NIL'

    employee = payslip.employee

    full_name = (
        employee.user.get_full_name().strip()
        or employee.user.email
    )

    employee_info = [
        ['Payslip No.', payslip.payslip_number or '-', 'Pay Date', str(payslip.pay_date)],
        ['Employee ID', employee.employee_id or '-', 'Employee Name', full_name],
        ['Department', str(employee.department or '-'), 'Designation', employee.designation or '-'],
        ['Joining Date', str(employee.joining_date), 'Location', employee.location or '-'],
        ['PF Number', employee.pf_number or '-', 'UAN Number', employee.uan_number or '-'],
        ['ESI Number', employee.esi_number or '-', 'Days in Month', str(payslip.days_in_month)],
        ['Paid Days', str(payslip.effective_work_days), 'LOP Days', str(payslip.lop)],
        ['Payment Mode', payslip.get_payment_mode_display(), '', ''],
    ]

    employee_table = Table(
        employee_info,
        colWidths=[82, 178, 82, 178]
    )

    employee_table.setStyle(
        TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#9ca3af')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f3f4f6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ])
    )

    elements.append(employee_table)
    elements.append(Spacer(1, 10))



    elements.append(Spacer(1, 10))

    earnings_rows = [
        ('Basic Salary', payslip.basic_salary),
        ('HRA', payslip.hra),
        ('Conveyance', payslip.conveyance),
        ('Special Allowance', payslip.special_allowance),
        ('Overtime', payslip.overtime),
        ('Bonus', payslip.bonus),
        ('Other Earnings', payslip.other_earnings),
    ]

    deduction_rows = [
        ('PF', payslip.pf),
        ('ESI', payslip.esi),
        ('Professional Tax', payslip.professional_tax),
        ('Income Tax / TDS', payslip.income_tax),
        ('LOP Deduction', payslip.lop_deduction),
        ('Other Deductions', payslip.other_deduction),
    ]

    salary_data = [[
        Paragraph('EARNINGS', section_heading),
        Paragraph('AMOUNT', section_heading),
        Paragraph('DEDUCTIONS', section_heading),
        Paragraph('AMOUNT', section_heading),
    ]]

    for i in range(max(len(earnings_rows), len(deduction_rows))):
        earning_name = ''
        earning_value = ''
        deduction_name = ''
        deduction_value = ''

        if i < len(earnings_rows):
            name, value = earnings_rows[i]
            earning_name = Paragraph(name, body)
            earning_value = Paragraph(
                _payslip_amount(value),
                amount
            )

        if i < len(deduction_rows):
            name, value = deduction_rows[i]
            deduction_name = Paragraph(name, body)
            deduction_value = Paragraph(
                _payslip_amount(value),
                amount
            )

        salary_data.append([
            earning_name,
            earning_value,
            deduction_name,
            deduction_value,
        ])

    salary_data.append([
        Paragraph('GROSS EARNINGS', total_label),
        Paragraph(
            _payslip_amount(payslip.gross_salary),
            amount
        ),
        Paragraph('TOTAL DEDUCTIONS', total_label),
        Paragraph(
            _payslip_amount(payslip.total_deductions),
            amount
        ),
    ])

    salary_table = Table(
        salary_data,
        colWidths=[130, 130, 130, 130]
    )

    salary_table.setStyle(
        TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#9ca3af')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f8fafc')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ])
    )

    elements.append(salary_table)
    elements.append(Spacer(1, 12))

    net_table = Table(
        [[
            Paragraph('NET SALARY PAYABLE', net_label),
            Paragraph(
                _payslip_amount(payslip.net_salary),
                net_value
            ),
        ]],
        colWidths=[330, 190]
    )

    net_table.setStyle(
        TableStyle([
            ('BOX', (0, 0), (-1, -1), 1.0, colors.HexColor('#6b7280')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecfdf5')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 9),
            ('RIGHTPADDING', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ])
    )

    elements.append(net_table)
    elements.append(Spacer(1, 7))

    elements.append(
        Paragraph(
            f'<b>Amount in Words:</b> {_amount_words(payslip.net_salary)}',
            words_style
        )
    )

    elements.append(Spacer(1, 18))

    elements.append(
        HRFlowable(
            width='100%',
            thickness=0.6,
            color=colors.HexColor('#d1d5db'),
            spaceBefore=0,
            spaceAfter=7
        )
    )

    elements.append(
        Paragraph(
            'This is a computer-generated payslip and does not require a signature.',
            footer_style
        )
    )

    elements.append(
        Paragraph(
            'Confidential payroll document. Please retain securely.',
            footer_style
        )
    )

    doc.build(elements)

    return response

@login_required
def document_list(request):
    from datetime import timedelta

    is_hr = _document_is_hr(request)

    if is_hr:
        documents = EmployeeDocument.objects.select_related(
            'employee',
            'employee__user',
            'employee__department',
            'uploaded_by',
            'reviewed_by'
        ).filter(is_active=True)
    else:
        employee = Employee.objects.filter(
            user=request.user
        ).first()
        documents = (
            EmployeeDocument.objects.select_related(
                'employee',
                'employee__user',
                'employee__department'
            ).filter(employee=employee, is_active=True)
            if employee else EmployeeDocument.objects.none()
        )

    search = request.GET.get('search', '').strip()
    department = request.GET.get('department', '').strip()
    category = request.GET.get('category', '').strip()
    document_type = request.GET.get('document_type', '').strip()
    status = request.GET.get('status', '').strip()
    expiry = request.GET.get('expiry', '').strip()

    if search:
        documents = documents.filter(
            Q(title__icontains=search) |
            Q(document_number__icontains=search) |
            Q(employee__employee_id__icontains=search) |
            Q(employee__user__first_name__icontains=search) |
            Q(employee__user__last_name__icontains=search) |
            Q(employee__user__email__icontains=search)
        )

    if department:
        documents = documents.filter(employee__department_id=department)

    if category:
        documents = documents.filter(category=category)

    if document_type:
        documents = documents.filter(document_type=document_type)

    if status:
        documents = documents.filter(status=status)

    today = timezone.localdate()

    if expiry == 'EXPIRED':
        documents = documents.filter(expiry_date__lt=today)
    elif expiry == '30_DAYS':
        documents = documents.filter(
            expiry_date__gte=today,
            expiry_date__lte=today + timedelta(days=30)
        )
    elif expiry == '7_DAYS':
        documents = documents.filter(
            expiry_date__gte=today,
            expiry_date__lte=today + timedelta(days=7)
        )
    elif expiry == 'NO_EXPIRY':
        documents = documents.filter(expiry_date__isnull=True)

    base_documents = (
        EmployeeDocument.objects.select_related(
            'employee',
            'employee__user',
            'employee__department'
        ).filter(is_active=True)
    )

    total_documents = base_documents.count()
    pending_documents = base_documents.filter(
        status__in=['PENDING', 'UNDER_REVIEW', 'SENT_BACK']
    ).count()
    approved_documents = base_documents.filter(status='APPROVED').count()
    rejected_documents = base_documents.filter(status='REJECTED').count()
    expiring_soon = base_documents.filter(
        expiry_date__gte=today,
        expiry_date__lte=today + timedelta(days=30)
    ).count()

    required_types = ['PAN', 'AADHAAR', 'BANK_PROOF']
    employees = Employee.objects.filter(status='ACTIVE').prefetch_related('documents')
    missing_documents = 0

    for employee in employees:
        available = {
            doc.document_type
            for doc in employee.documents.all()
            if doc.is_active and doc.status == 'APPROVED'
        }
        if any(required_type not in available for required_type in required_types):
            missing_documents += 1

    allowed_page_sizes = [10, 20, 50]
    try:
        page_size = int(request.GET.get('page_size', '10'))
    except (TypeError, ValueError):
        page_size = 10
    if page_size not in allowed_page_sizes:
        page_size = 10

    paginator = Paginator(
        documents.order_by('-uploaded_at'),
        page_size
    )
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'documents': page_obj.object_list,
        'page_obj': page_obj,
        'departments': Department.objects.order_by('name'),
        'categories': EmployeeDocument.CATEGORY_CHOICES,
        'document_types': EmployeeDocument.DOCUMENT_TYPES,
        'statuses': EmployeeDocument.STATUS_CHOICES,
        'search': search,
        'selected_department': department,
        'selected_category': category,
        'selected_document_type': document_type,
        'selected_status': status,
        'selected_expiry': expiry,
        'page_size': page_size,
        'total_documents': total_documents,
        'pending_documents': pending_documents,
        'approved_documents': approved_documents,
        'rejected_documents': rejected_documents,
        'expiring_soon': expiring_soon,
        'missing_documents': missing_documents,
        'is_hr': is_hr,
    }

    return render(
        request,
        'documents/list.html',
        context
    )


@login_required
def upload_document(request):
    is_hr = _document_is_hr(request)

    if is_hr:
        employees = Employee.objects.select_related('user', 'department').filter(
            status='ACTIVE'
        )
    else:
        employees = Employee.objects.filter(user=request.user)

    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        employee = get_object_or_404(Employee, pk=employee_id)

        if not is_hr and employee.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('document_list')

        file = request.FILES.get('file')
        error = _validate_document_file(file)
        if error:
            messages.error(request, error)
            return render(request, 'documents/upload.html', {
                'employees': employees,
                'categories': EmployeeDocument.CATEGORY_CHOICES,
                'document_types': EmployeeDocument.DOCUMENT_TYPES,
                'selected_employee': employee_id,
            })

        document = EmployeeDocument.objects.create(
            employee=employee,
            category=request.POST.get('category', 'OTHER'),
            title=request.POST.get('title', '').strip(),
            document_type=request.POST.get('document_type'),
            document_number=request.POST.get('document_number', '').strip() or None,
            issue_date=parse_date(request.POST.get('issue_date', '')) if request.POST.get('issue_date') else None,
            expiry_date=parse_date(request.POST.get('expiry_date', '')) if request.POST.get('expiry_date') else None,
            confidentiality=request.POST.get('confidentiality', 'NORMAL'),
            remarks=request.POST.get('remarks', '').strip(),
            file=file,
            uploaded_by=request.user,
            status='PENDING',
        )

        messages.success(
            request,
            f'{document.title} uploaded for {employee.user.get_full_name() or employee.user.email}.'
        )
        return redirect('document_list')

    return render(request, 'documents/upload.html', {
        'employees': employees,
        'categories': EmployeeDocument.CATEGORY_CHOICES,
        'document_types': EmployeeDocument.DOCUMENT_TYPES,
        'confidentiality_choices': EmployeeDocument.CONFIDENTIALITY_CHOICES,
    })


@login_required
def document_detail(request, pk):
    document = get_object_or_404(
        EmployeeDocument.objects.select_related(
            'employee',
            'employee__user',
            'employee__department',
            'uploaded_by',
            'reviewed_by'
        ),
        pk=pk,
        is_active=True
    )

    is_hr = _document_is_hr(request)

    if not is_hr and document.employee.user != request.user:
        raise PermissionDenied('Access denied.')

    return render(
        request,
        'documents/detail.html',
        {
            'document': document,
            'versions': document.versions.select_related('uploaded_by').all(),
            'is_hr': is_hr,
        }
    )


@login_required
def download_document(request, pk):
    document = get_object_or_404(
        EmployeeDocument,
        pk=pk,
        is_active=True
    )

    is_hr = _document_is_hr(request)

    if not is_hr and document.employee.user != request.user:
        raise PermissionDenied('Access denied.')

    if document.status == 'EXPIRED':
        messages.warning(request, 'This document has expired.')

    file_handle = document.file.open('rb')
    content_type, _ = mimetypes.guess_type(document.file.name)
    response = FileResponse(
        file_handle,
        as_attachment=True,
        filename=os.path.basename(document.file.name),
        content_type=content_type or 'application/octet-stream'
    )
    response['X-Frame-Options'] = 'DENY'
    response['Cache-Control'] = 'private, no-store'

    try:
        create_audit_log(
            request.user,
            'Document',
            f'Downloaded document {document.pk} for {document.employee.employee_id}'
        )
    except Exception:
        pass

    return response


@login_required
@require_POST
def replace_document(request, pk):
    if not _document_is_hr(request):
        raise PermissionDenied('Only HR/Admin can replace documents.')

    document = get_object_or_404(
        EmployeeDocument,
        pk=pk,
        is_active=True
    )

    new_file = request.FILES.get('file')
    error = _validate_document_file(new_file)

    if error:
        messages.error(request, error)
        return redirect('document_detail', pk=pk)

    from .models import DocumentVersion

    last_version = document.versions.order_by('-version_number').first()
    next_version = (last_version.version_number + 1) if last_version else 1

    # Preserve the previous file as a version before replacing it.
    if document.file:
        DocumentVersion.objects.create(
            document=document,
            version_number=next_version,
            file=document.file,
            uploaded_by=request.user,
            note=request.POST.get('version_note', '').strip() or 'Previous file version',
        )

    document.file = new_file
    document.status = 'PENDING'
    document.rejection_reason = None
    document.reviewed_by = None
    document.reviewed_at = None
    document.save()

    messages.success(request, 'Document replaced and sent for review.')
    return redirect('document_detail', pk=pk)


@login_required
@require_POST
def approve_document(request, pk):
    if not _document_is_hr(request):
        raise PermissionDenied('Only HR/Admin can approve documents.')

    document = get_object_or_404(EmployeeDocument, pk=pk, is_active=True)
    document.status = 'APPROVED'
    document.reviewed_by = request.user
    document.reviewed_at = timezone.now()
    document.rejection_reason = None
    document.save()

    messages.success(request, 'Document approved successfully.')
    return redirect('document_detail', pk=pk)


@login_required
@require_POST
def reject_document(request, pk):
    if not _document_is_hr(request):
        raise PermissionDenied('Only HR/Admin can reject documents.')

    document = get_object_or_404(EmployeeDocument, pk=pk, is_active=True)
    document.status = 'REJECTED'
    document.reviewed_by = request.user
    document.reviewed_at = timezone.now()
    document.rejection_reason = request.POST.get('rejection_reason', '').strip()
    document.save()

    messages.success(request, 'Document rejected with review comments.')
    return redirect('document_detail', pk=pk)


@login_required
@require_POST
def send_back_document(request, pk):
    if not _document_is_hr(request):
        raise PermissionDenied('Only HR/Admin can send documents back.')

    document = get_object_or_404(EmployeeDocument, pk=pk, is_active=True)
    document.status = 'SENT_BACK'
    document.reviewed_by = request.user
    document.reviewed_at = timezone.now()
    document.rejection_reason = request.POST.get('rejection_reason', '').strip()
    document.save()

    messages.success(request, 'Document sent back for correction.')
    return redirect('document_detail', pk=pk)


@login_required
@require_POST
def delete_document(request, pk):
    if not _document_is_hr(request):
        raise PermissionDenied('Only HR/Admin can archive documents.')

    document = get_object_or_404(
        EmployeeDocument,
        pk=pk,
        is_active=True
    )

    document.is_active = False
    document.save(update_fields=['is_active', 'updated_at'])

    messages.success(request, 'Document archived successfully.')
    return redirect('document_list')

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

@login_required
def global_search(request):
    query = request.GET.get('q', '').strip()

    # Initialize empty QuerySets using .none()
    employees = Employee.objects.none()
    payslips = Payslip.objects.none()
    documents = EmployeeDocument.objects.none()
    attendance = Attendance.objects.none()
    leaves = Leave.objects.none()

    if query:
        # Search employees by ID, user email, or designation
        employees = Employee.objects.filter(
            Q(employee_id__icontains=query) |
            Q(user__email__icontains=query) |
            Q(designation__icontains=query)
        )[:10]

        # Search payslips by month name
        payslips = Payslip.objects.filter(
            Q(month__icontains=query)
        )[:10]

        # Search documents by title
        documents = EmployeeDocument.objects.filter(
            Q(title__icontains=query)
        )[:10]

        # Search attendance records by status string (e.g., 'PRESENT')
        attendance = Attendance.objects.filter(
            Q(status__icontains=query)
        )[:10]

        # Search leave requests by status string (e.g., 'APPROVED')
        leaves = Leave.objects.filter(
    Q(status__icontains=query)
)[:10]

    return render(
        request,
        'search/results.html',
        {
            'query': query,
            'employees': employees,
            'payslips': payslips,
            'documents': documents,
            'attendance': attendance,
            'leaves': leaves,
        }
    )

@login_required
def asset_list(request):

    assets = Asset.objects.select_related(
        'assigned_to'
    ).all()

    return render(
        request,
        'assets/list.html',
        {'assets': assets}
    )


@login_required
def asset_add(request):

    form = AssetForm()

    if request.method == 'POST':

        form = AssetForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Asset created successfully.'
            )

            return redirect(
                'asset_list'
            )

    return render(
        request,
        'assets/add.html',
        {'form': form}
    )


@login_required
def asset_detail(request, pk):

    asset = get_object_or_404(
        Asset,
        pk=pk
    )

    return render(
        request,
        'assets/detail.html',
        {'asset': asset}
    )