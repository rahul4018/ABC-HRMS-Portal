from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.shortcuts import render
from django.utils import timezone

from apps.employees.models import (
    Employee,
    Department,
    Attendance,
    EmployeeDocument,
)

from apps.leave.models import (
    Leave,
    LeaveBalance,
    Holiday,
)

from apps.payslips.models import Payslip

from appraisal.models import PMR
from resignation.models import Resignation
from recruitment.models import JobRequirement, Applicant
from notifications.models import Notification
from audit.models import AuditLog


# =========================================================
# ACCESS ROLES
# =========================================================

MANAGEMENT_ROLES = {
    'MASTER_ADMIN',
    'FOUNDER',
    'HR',
}


# =========================================================
# PUBLIC LANDING PAGE
# =========================================================

def landing_page(request):
    """Public ABC HRMS Portal website. No login required."""
    return render(request, 'public/landing.html')


# =========================================================
# COMMON MANAGEMENT DASHBOARD DATA
# =========================================================

def _common_context(request):
    today = timezone.localdate()

    month_start = today.replace(day=1)

    next_month = (
        month_start + timedelta(days=32)
    ).replace(day=1)

    employees = Employee.objects.select_related(
        'user',
        'department',
    )

    active_employees = employees.filter(
        status='ACTIVE',
    )

    return {
        'today': today,

        'total_employees': employees.count(),

        'active_employees': active_employees.count(),

        'departments': (
            Department.objects
            .annotate(
                employee_count=Count('employee'),
            )
            .order_by(
                '-employee_count',
                'name',
            )
        ),

        'present_today': (
            Attendance.objects
            .filter(
                date=today,
                status='PRESENT',
            )
            .count()
        ),

        'absent_today': (
            Attendance.objects
            .filter(
                date=today,
                status='ABSENT',
            )
            .count()
        ),

        'half_day_today': (
            Attendance.objects
            .filter(
                date=today,
                status='HALF_DAY',
            )
            .count()
        ),

        'on_leave_today': (
            Leave.objects
            .filter(
                status='APPROVED',
                start_date__lte=today,
                end_date__gte=today,
            )
            .count()
        ),

        'new_joiners': (
            employees
            .filter(
                joining_date__gte=month_start,
                joining_date__lt=next_month,
            )
            .count()
        ),

        'pending_leaves': (
            Leave.objects
            .filter(
                status='PENDING',
            )
            .count()
        ),

        'pending_docs': (
            EmployeeDocument.objects
            .filter(
                status='PENDING',
            )
            .count()
        ),

        'pending_pmrs': (
            PMR.objects
            .filter(
                status='PENDING',
            )
            .count()
        ),

        'pending_resignations': (
            Resignation.objects
            .filter(
                status='PENDING',
            )
            .count()
        ),

        'open_positions': (
            JobRequirement.objects
            .filter(
                status='OPEN',
            )
            .count()
        ),

        'applications': (
            Applicant.objects
            .count()
        ),

        'unread_notifications': (
            Notification.objects
            .filter(
                user=request.user,
                is_read=False,
            )
            .count()
        ),

        'incomplete_profiles': (
            employees
            .filter(
                Q(bank_name__isnull=True)
                | Q(bank_name='')
                | Q(account_number__isnull=True)
                | Q(account_number='')
                | Q(pan_number__isnull=True)
                | Q(pan_number='')
                | Q(pf_number__isnull=True)
                | Q(pf_number='')
            )
            .count()
        ),
    }


# =========================================================
# PAYROLL CONTEXT
# =========================================================

def _payroll_context(
    month='August',
    year=2026,
):
    qs = Payslip.objects.filter(
        month=month,
        year=year,
    )

    aggregate = qs.aggregate(
        gross=Sum('gross_salary'),
        deductions=Sum('total_deductions'),
        net=Sum('net_salary'),
        employer=Sum(
            'total_employer_contribution'
        ),
    )

    processed = qs.count()

    total = (
        Employee.objects
        .filter(
            status='ACTIVE',
        )
        .count()
    )

    return {
        'payroll_month': month,

        'payroll_year': year,

        'payroll_processed': processed,

        'payroll_total': total,

        'payroll_pending': max(
            total - processed,
            0,
        ),

        'payroll_gross': (
            aggregate['gross']
            or Decimal('0')
        ),

        'payroll_deductions': (
            aggregate['deductions']
            or Decimal('0')
        ),

        'payroll_net': (
            aggregate['net']
            or Decimal('0')
        ),

        'payroll_employer': (
            aggregate['employer']
            or Decimal('0')
        ),
    }


# =========================================================
# DEPARTMENT DISTRIBUTION
# =========================================================

def _department_distribution():
    return (
        Department.objects
        .annotate(
            employee_total=Count('employee')
        )
        .order_by(
            '-employee_total',
            'name',
        )
    )


# =========================================================
# ATTENDANCE TREND
# =========================================================

def _attendance_trend():
    today = timezone.localdate()

    rows = []

    for offset in range(6, -1, -1):

        day = today - timedelta(
            days=offset,
        )

        present = (
            Attendance.objects
            .filter(
                date=day,
                status='PRESENT',
            )
            .count()
        )

        rows.append(
            {
                'date': day,
                'present': present,
            }
        )

    return rows


# =========================================================
# MAIN AUTHENTICATED DASHBOARD
# =========================================================

@login_required
def dashboard(request):
    """
    Main authenticated HRMS dashboard.

    New access roles:

        MASTER_ADMIN
        FOUNDER
        HR
        EMPLOYEE
        CONTRACTOR

    The old portal_role field is retained as a fallback
    for compatibility with older parts of the system.
    """

    # -----------------------------------------------------
    # Prefer the new access_role field.
    # -----------------------------------------------------

    access_role = getattr(
        request.user,
        'access_role',
        None,
    )

    # -----------------------------------------------------
    # Backward compatibility.
    # -----------------------------------------------------

    if not access_role:

        access_role = getattr(
            request.user,
            'portal_role',
            'EMPLOYEE',
        )

    # =====================================================
    # MASTER ADMIN
    # =====================================================

    if access_role == 'MASTER_ADMIN':

        common = _common_context(request)

        common.update(
            _payroll_context()
        )

        common.update(
            {
                'role_label': 'Master Admin',

                'access_role': access_role,

                'total_users': (
                    request.user.__class__
                    .objects
                    .count()
                ),

                'staff_users': (
                    request.user.__class__
                    .objects
                    .filter(
                        is_staff=True,
                    )
                    .count()
                ),

                'superusers': (
                    request.user.__class__
                    .objects
                    .filter(
                        is_superuser=True,
                    )
                    .count()
                ),

                'audit_entries': (
                    AuditLog.objects
                    .count()
                ),

                'recent_audit': (
                    AuditLog.objects
                    .select_related(
                        'user',
                    )[:8]
                ),

                'recent_users': (
                    request.user.__class__
                    .objects
                    .order_by(
                        '-date_joined',
                    )[:6]
                ),
            }
        )

        return render(
            request,
            'dashboard/admin.html',
            common,
        )

    # =====================================================
    # FOUNDER
    # =====================================================

    if access_role == 'FOUNDER':

        common = _common_context(request)

        common.update(
            _payroll_context()
        )

        common.update(
            {
                'role_label': 'Founder',

                'access_role': access_role,

                'total_compensation_cost': (
                    common['payroll_gross']
                    + common[
                        'payroll_employer'
                    ]
                ),

                'approved_resignations': (
                    Resignation.objects
                    .filter(
                        status='APPROVED',
                    )
                    .count()
                ),

                'recruitment_openings': (
                    JobRequirement.objects
                    .filter(
                        status='OPEN',
                    )
                    .aggregate(
                        total=Sum('openings'),
                    )['total']
                    or 0
                ),

                'selected_candidates': (
                    Applicant.objects
                    .filter(
                        status='SELECTED',
                    )
                    .count()
                ),

                'recent_audit': (
                    AuditLog.objects
                    .select_related(
                        'user',
                    )[:6]
                ),
            }
        )

        return render(
            request,
            'dashboard/founder.html',
            common,
        )

    # =====================================================
    # HR
    # =====================================================

    if access_role == 'HR':

        common = _common_context(request)

        common.update(
            _payroll_context()
        )

        common.update(
            {
                'role_label': 'HR',

                'access_role': access_role,

                'probation_ending': (
                    Employee.objects
                    .select_related(
                        'user',
                        'department',
                    )
                    .filter(
                        status='ACTIVE',
                        probation_end_date__isnull=False,
                        probation_end_date__gte=timezone.localdate(),
                        probation_end_date__lte=(
                            timezone.localdate()
                            + timedelta(days=30)
                        ),
                    )
                    .order_by(
                        'probation_end_date',
                    )[:6]
                ),

                'upcoming_birthdays': (
                    Employee.objects
                    .select_related(
                        'user',
                    )
                    .filter(
                        date_of_birth__isnull=False,
                    )[:6]
                ),

                'pending_leave_items': (
                    Leave.objects
                    .filter(
                        status='PENDING',
                    )
                    .select_related(
                        'employee__user',
                    )[:6]
                ),

                'pending_document_items': (
                    EmployeeDocument.objects
                    .filter(
                        status='PENDING',
                    )
                    .select_related(
                        'employee__user',
                    )[:6]
                ),

                'pending_pmr_items': (
                    PMR.objects
                    .filter(
                        status='PENDING',
                    )
                    .select_related(
                        'employee__user',
                    )[:6]
                ),

                'pending_resignation_items': (
                    Resignation.objects
                    .filter(
                        status='PENDING',
                    )
                    .select_related(
                        'employee__user',
                    )[:6]
                ),

                'recent_audit': (
                    AuditLog.objects
                    .select_related(
                        'user',
                    )[:8]
                ),
            }
        )

        return render(
            request,
            'dashboard/hr.html',
            common,
        )

    # =====================================================
    # EMPLOYEE / CONTRACTOR
    # =====================================================

    employee = (
        Employee.objects
        .select_related(
            'user',
            'department',
        )
        .filter(
            user=request.user,
        )
        .first()
    )

    leave_balance = None

    personal_leaves = (
        Leave.objects.none()
    )

    personal_attendance = (
        Attendance.objects.none()
    )

    personal_payslips = (
        Payslip.objects.none()
    )

    personal_pmrs = (
        PMR.objects.none()
    )

    if employee:

        leave_balance = (
            LeaveBalance.objects
            .filter(
                employee=employee,
            )
            .first()
        )

        personal_leaves = (
            Leave.objects
            .filter(
                employee=employee,
            )[:5]
        )

        personal_attendance = (
            Attendance.objects
            .filter(
                employee=employee,
            )[:5]
        )

        personal_payslips = (
            Payslip.objects
            .filter(
                employee=employee,
            )[:5]
        )

        personal_pmrs = (
            PMR.objects
            .filter(
                employee=employee,
            )[:5]
        )

    role_label = 'Contractor'

    if access_role == 'EMPLOYEE':
        role_label = 'Employee'

    elif access_role == 'CONTRACTOR':
        role_label = 'Contractor'

    context = {
        'role_label': role_label,

        'access_role': access_role,

        'employee': employee,

        'leave_balance': leave_balance,

        'personal_leaves': personal_leaves,

        'personal_attendance': personal_attendance,

        'personal_payslips': personal_payslips,

        'personal_pmrs': personal_pmrs,

        'profile_completion': (
            _employee_profile_completion(
                employee
            )
        ),

        'upcoming_holidays': (
            Holiday.objects
            .filter(
                holiday_date__gte=timezone.localdate()
            )
            .order_by(
                'holiday_date'
            )[:5]
        ),
    }

    return render(
        request,
        'dashboard/employee.html',
        context,
    )


# =========================================================
# EMPLOYEE PROFILE COMPLETION
# =========================================================

def _employee_profile_completion(employee):

    if not employee:
        return 0

    checks = [
        bool(
            employee.user
            and employee.user.first_name
            and employee.user.last_name
        ),

        bool(employee.phone),

        bool(employee.address),

        bool(employee.location),

        bool(employee.department),

        bool(employee.designation),

        bool(employee.joining_date),

        bool(employee.pan_number),

        bool(employee.bank_name),

        bool(employee.account_number),

        bool(
            employee.emergency_contact_name
        ),
    ]

    return round(
        sum(checks) * 100 / len(checks)
    )