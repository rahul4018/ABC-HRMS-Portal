from django.urls import path
from .views import (
    requirement_list,
    create_requirement,
    applicant_list,
    shortlist_applicant,
    select_applicant,
    onboard_applicant,
    convert_to_employee,
)

urlpatterns = [
    path('', requirement_list, name='requirement_list'),
    path('create/', create_requirement, name='create_requirement'),
    path('<int:requirement_id>/applicants/', applicant_list, name='applicant_list'),
    path('applicant/<int:pk>/shortlist/', shortlist_applicant, name='shortlist_applicant'),
    path('applicant/<int:pk>/select/', select_applicant, name='select_applicant'),
    path('applicant/<int:pk>/onboard/', onboard_applicant, name='onboard_applicant'),
    path('applicant/<int:pk>/convert/', convert_to_employee,name='convert_to_employee'
),
]