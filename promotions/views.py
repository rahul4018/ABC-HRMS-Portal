from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from apps.employees.models import Employee
from .models import Promotion


@login_required
def promotion_list(request):
    role = getattr(request.user, "role", "EMPLOYEE")

    if role == "SUPERVISOR":
        promotions = Promotion.objects.select_related(
            "employee", 
            "employee__user"
        ).all().order_by("-created_at")
    else:
        # Standard employees must only see their own career progression trail
        employee = Employee.objects.filter(user=request.user).first()
        if employee:
            promotions = Promotion.objects.filter(employee=employee).order_by("-created_at")
        else:
            promotions = Promotion.objects.none()

    return render(
        request,
        "promotions/list.html",
        {"promotions": promotions}
    )


@login_required
def create_promotion(request):
    if getattr(request.user, "role", None) != "SUPERVISOR":
        raise PermissionDenied("Unauthorized route invocation.")

    if request.method == "POST":
        employee_id = request.POST.get("employee")
        old_designation = request.POST.get("old_designation")
        new_designation = request.POST.get("new_designation")
        effective_date = request.POST.get("effective_date")
        remarks = request.POST.get("remarks")

        if not all([employee_id, old_designation, new_designation, effective_date]):
            messages.error(request, "Please populate all necessary input criteria rows.")
            employees = Employee.objects.all()
            return render(request, "promotions/create.html", {"employees": employees})

        employee = get_object_or_404(Employee, id=employee_id)

        Promotion.objects.create(
            employee=employee,
            old_designation=old_designation,
            new_designation=new_designation,
            effective_date=effective_date,
            remarks=remarks,
            status="PENDING"
        )

        messages.success(request, f"Promotion process record initiated for {employee.user.email}.")
        return redirect("promotion_list")

    employees = Employee.objects.all()
    return render(
        request,
        "promotions/create.html",
        {"employees": employees}
    )


@login_required
@require_POST
def approve_promotion(request, pk):
    if getattr(request.user, "role", None) != "SUPERVISOR":
        messages.error(request, "Unauthorized access token action.")
        return redirect("promotion_list")

    promotion = get_object_or_404(Promotion, pk=pk)
    promotion.status = "APPROVED"
    promotion.save()

    messages.success(request, f"Promotion finalized successfully for {promotion.employee.user.email}.")
    return redirect("promotion_list")


@login_required
@require_POST
def reject_promotion(request, pk):
    if getattr(request.user, "role", None) != "SUPERVISOR":
        messages.error(request, "Unauthorized access token action.")
        return redirect("promotion_list")

    promotion = get_object_or_404(Promotion, pk=pk)
    promotion.status = "REJECTED"
    promotion.save()

    messages.warning(request, f"Promotion workflow entry rejected for {promotion.employee.user.email}.")
    return redirect("promotion_list")


@login_required
def promotion_letter(request, pk):
    promotion = get_object_or_404(Promotion, pk=pk)
    role = getattr(request.user, "role", "EMPLOYEE")

    # Data privacy check: regular employees should only download their own documentation
    if role != "SUPERVISOR" and promotion.employee.user != request.user:
        raise PermissionDenied("Access to requested promotion document generation denied.")

    if promotion.status != "APPROVED":
        messages.error(request, "Document distribution restricted until workflow status turns APPROVED.")
        return redirect("promotion_list")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Promotion_Letter_{promotion.employee.employee_id}.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    pdf.setTitle("Promotion Letter")

    # Top Header Border Stroke Accent Rule
    pdf.setStrokeColor(colors.HexColor("#0F172A"))
    pdf.line(40, height - 70, width - 40, height - 70)

    # Document Header branding elements
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(50, height - 50, "ABC HRMS Portal")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, height - 65, "Employee Management Platform")

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, height - 110, "PROMOTION LETTER")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, height - 140, f"Reference No : PRO-{promotion.id:04d}")
    pdf.drawString(350, height - 140, f"Date : {promotion.effective_date}")

    # Core Segment 1 - Employee Metas Block
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 190, "Employee Information")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(70, height - 220, f"Employee ID : {promotion.employee.employee_id}")
    pdf.drawString(70, height - 245, f"Email : {promotion.employee.user.email}")

    # Core Segment 2 - Adjustments Criteria Block
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 295, "Promotion Details")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(70, height - 325, f"Previous Designation : {promotion.old_designation}")
    pdf.drawString(70, height - 350, f"New Designation : {promotion.new_designation}")
    pdf.drawString(70, height - 375, f"Effective Date : {promotion.effective_date}")

    # Letter Body Narrative Segment
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 430, "Dear Employee,")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, height - 460, "We are pleased to inform you that you have been promoted")
    pdf.drawString(50, height - 480, f"to the position of {promotion.new_designation}.")
    pdf.drawString(50, height - 510, "This promotion reflects your dedication, performance,")
    pdf.drawString(50, height - 530, "professionalism and valuable contribution to the company.")
    pdf.drawString(50, height - 560, "We look forward to your continued success and leadership.")

    # Formal Signatures Section
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 640, "Authorized Signatory")
    pdf.line(50, height - 680, 220, height - 680)

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, height - 700, "HR Department")
    pdf.drawString(50, height - 720, "ABC HRMS Portal")

    # Document Footer Block Elements
    pdf.line(40, 70, width - 40, 70)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(50, 50, "This is a system-generated promotion letter.")
    pdf.drawRightString(width - 50, 50, "ABC HRMS Portal")

    # Finalize Page Context Canvas Rendering
    pdf.showPage()
    pdf.save()

    return response