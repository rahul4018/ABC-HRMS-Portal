from django.contrib import admin
from .models import (
    ApprovalWorkflow, Designation, EmploymentHistory, ExitCase, ExitClearance,
    ExitDocument, ExitInterview, FinalSettlement, HRRequest, JobGrade,
    Location, RehireRecord, Team, UserModulePermission,
)


@admin.register(ExitCase)
class ExitCaseAdmin(admin.ModelAdmin):
    list_display = ('employee', 'exit_type', 'status', 'actual_last_working_day', 'approved_by', 'created_at')
    list_filter = ('exit_type', 'status')
    search_fields = ('employee__employee_id', 'employee__user__first_name', 'employee__user__last_name')


for model in [Location, Team, Designation, JobGrade, EmploymentHistory, ApprovalWorkflow,
              UserModulePermission, ExitClearance, ExitInterview, FinalSettlement,
              ExitDocument, RehireRecord, HRRequest]:
    admin.site.register(model)
