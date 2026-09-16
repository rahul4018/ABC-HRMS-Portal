from django.contrib import admin
from .models import (
    HiringRequest, JobRequirementExtra, CandidateProfile, Interview,
    InterviewFeedback, Offer, BackgroundVerification, OnboardingTask,
    RecruitmentActivity,
)

admin.site.register(HiringRequest)
admin.site.register(JobRequirementExtra)
admin.site.register(CandidateProfile)
admin.site.register(Interview)
admin.site.register(InterviewFeedback)
admin.site.register(Offer)
admin.site.register(BackgroundVerification)
admin.site.register(OnboardingTask)
admin.site.register(RecruitmentActivity)
