import csv

from datetime import date
from datetime import datetime

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib import messages

from django.contrib.auth.decorators import login_required

from django.db.models import Count, Q

from django.http import HttpResponse

from reportlab.pdfgen import canvas

from apps.leave.models import Leave
from apps.payslips.models import Payslip

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
@role_required(['CEO', 'HR_ADMIN'])
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
@role_required(['CEO', 'HR_ADMIN'])
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
@role_required(['CEO', 'HR_ADMIN'])
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
@role_required(['CEO', 'HR_ADMIN'])
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
@role_required(['CEO', 'HR_ADMIN'])
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
@role_required(['CEO'])
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
    'CEO',
    'HR_ADMIN',
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
@role_required(['CEO', 'HR_ADMIN'])
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
@role_required(['CEO', 'HR_ADMIN'])
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
@role_required(['CEO', 'HR_ADMIN'])
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
@role_required(['CEO'])
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

    if request.user.role in ['CEO', 'HR_ADMIN']:

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


# ==========================================
# ATTENDANCE MANAGEMENT
# ==========================================

@login_required
def attendance_list(request):

    if request.user.role in ['CEO', 'HR_ADMIN']:

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
@role_required(['CEO', 'HR_ADMIN'])
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
@role_required(['CEO', 'HR_ADMIN'])
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


# ==========================================
# PAYSLIP PDF DOWNLOAD
# ==========================================

@login_required
def download_payslip_pdf(request, pk):

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

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = f'attachment; filename="Payslip_{payslip.id}.pdf"'

    pdf = canvas.Canvas(response)

    pdf.setTitle('Employee Payslip')

    pdf.setFont(
        'Helvetica-Bold',
        18
    )

    pdf.drawString(
        180,
        800,
        'SkillChekHub HRMS'
    )

    pdf.setFont(
        'Helvetica',
        12
    )

    pdf.drawString(
        50,
        740,
        f'Employee: {payslip.employee.user.email}'
    )

    pdf.drawString(
        50,
        710,
        f'Department: {payslip.employee.department}'
    )

    pdf.drawString(
        50,
        680,
        f'Month: {payslip.month}'
    )

    pdf.drawString(
        50,
        650,
        f'Year: {payslip.year}'
    )

    pdf.drawString(
        50,
        620,
        f'Net Salary: ₹ {payslip.net_salary}'
    )

    pdf.save()

    return response


# ==========================================
# DOCUMENT MANAGEMENT
# ==========================================

@login_required
def document_list(request):

    if request.user.role in ['CEO', 'HR_ADMIN']:

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

    if request.user.role in ['CEO', 'HR_ADMIN']:

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