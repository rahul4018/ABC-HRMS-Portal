from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.http import HttpResponse

from reportlab.pdfgen import canvas

from apps.employees.models import Employee

from .models import Promotion


def promotion_list(request):

    promotions = Promotion.objects.select_related(
        'employee',
        'employee__user'
    ).all().order_by('-created_at')

    return render(
        request,
        'promotions/list.html',
        {
            'promotions': promotions
        }
    )


def create_promotion(request):

    if request.method == 'POST':

        employee = Employee.objects.get(
            id=request.POST.get('employee')
        )

        Promotion.objects.create(
            employee=employee,
            old_designation=request.POST.get(
                'old_designation'
            ),
            new_designation=request.POST.get(
                'new_designation'
            ),
            effective_date=request.POST.get(
                'effective_date'
            ),
            remarks=request.POST.get(
                'remarks'
            )
        )

        return redirect(
            'promotion_list'
        )

    employees = Employee.objects.all()

    return render(
        request,
        'promotions/create.html',
        {
            'employees': employees
        }
    )


def approve_promotion(
    request,
    pk
):

    promotion = get_object_or_404(
        Promotion,
        pk=pk
    )

    promotion.status = 'APPROVED'

    promotion.save()

    return redirect(
        'promotion_list'
    )


def reject_promotion(
    request,
    pk
):

    promotion = get_object_or_404(
        Promotion,
        pk=pk
    )

    promotion.status = 'REJECTED'

    promotion.save()

    return redirect(
        'promotion_list'
    )


def promotion_letter(
    request,
    pk
):

    promotion = get_object_or_404(
        Promotion,
        pk=pk
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = (
        f'attachment; '
        f'filename="Promotion_Letter_{promotion.employee.employee_id}.pdf"'
    )

    pdf = canvas.Canvas(
        response
    )

    pdf.setTitle(
        "Promotion Letter"
    )

    pdf.setFont(
        "Helvetica-Bold",
        18
    )

    pdf.drawString(
        180,
        800,
        "PROMOTION LETTER"
    )

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        50,
        740,
        f"Employee ID: {promotion.employee.employee_id}"
    )

    pdf.drawString(
        50,
        710,
        f"Employee Email: {promotion.employee.user.email}"
    )

    pdf.drawString(
        50,
        680,
        f"Old Designation: {promotion.old_designation}"
    )

    pdf.drawString(
        50,
        650,
        f"New Designation: {promotion.new_designation}"
    )

    pdf.drawString(
        50,
        620,
        f"Effective Date: {promotion.effective_date}"
    )

    pdf.drawString(
        50,
        560,
        "Congratulations on your promotion."
    )

    pdf.drawString(
        50,
        530,
        "We appreciate your contribution"
    )

    pdf.drawString(
        50,
        500,
        "and wish you success in your"
    )

    pdf.drawString(
        50,
        470,
        "new role and responsibilities."
    )

    pdf.drawString(
        50,
        400,
        "Authorized By"
    )

    pdf.drawString(
        50,
        370,
        "Supervisor"
    )

    pdf.showPage()

    pdf.save()

    return response