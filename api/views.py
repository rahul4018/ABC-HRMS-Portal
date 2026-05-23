from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.employees.models import Employee
from .serializers import EmployeeSerializer


@api_view(['GET'])
def employee_api(request):

    employees = Employee.objects.all()

    serializer = EmployeeSerializer(
        employees,
        many=True
    )

    return Response(serializer.data)