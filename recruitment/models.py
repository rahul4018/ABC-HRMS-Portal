from django.db import models

class JobRequirement(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    openings = models.PositiveIntegerField()
    experience = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Applicant(models.Model):
    STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('SHORTLISTED', 'Shortlisted'),
        ('INTERVIEW', 'Interview'),
        ('SELECTED', 'Selected'),
        ('REJECTED', 'Rejected'),
        ('ONBOARDED', 'Onboarded'),
    ]

    requirement = models.ForeignKey(
        JobRequirement,
        on_delete=models.CASCADE,
        related_name='applicants'
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    resume = models.FileField(upload_to='resumes/')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='APPLIED'
    )
    employee_created = models.BooleanField(default=False)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

# Complete ATS workflow models
from .workflow_models import (
    HiringRequest, JobRequirementExtra, CandidateProfile, JobPosting, Assessment,
    Interview, InterviewFeedback, Offer, BackgroundVerification,
    OnboardingTask, RecruitmentActivity,
)
