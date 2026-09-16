from datetime import time
from django.db import models
from django.conf import settings


# ==========================================
# Department Model
# ==========================================

class Department(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    department_head = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    # Structured fields for department management. The legacy department_head
    # field is retained for backward compatibility.
    code = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )
    head_employee = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def employee_count(self):
        return self.employee_set.count()

    def __str__(self):
        return self.name


# ==========================================
# Employee Model
# ==========================================

class Employee(models.Model):
    # --- Choices ---
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]

    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
    ]

    EMPLOYMENT_TYPE_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('INTERN', 'Intern'),
    ]

    WORK_MODE_CHOICES = [
        ('OFFICE', 'Office'),
        ('REMOTE', 'Remote'),
        ('HYBRID', 'Hybrid'),
    ]

    # --- Fields ---
    employee_id = models.CharField(
        max_length=20,
        unique=True
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    department = models.ForeignKey(
        'Department',  # Using a string syntax avoids import order issues
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    reporting_manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates'
    )

    designation = models.CharField(
        max_length=100
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='FULL_TIME'
    )

    work_mode = models.CharField(
        max_length=20,
        choices=WORK_MODE_CHOICES,
        default='OFFICE'
    )

    phone = models.CharField(
        max_length=15
    )

    address = models.TextField()

    location = models.CharField(
        max_length=100,
        default='Demo City'
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )

    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        blank=True,
        null=True
    )

    blood_group = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    nationality = models.CharField(
        max_length=50,
        default='Indian'
    )

    joining_date = models.DateField()

    probation_end_date = models.DateField(
        null=True,
        blank=True
    )

    exit_date = models.DateField(
        null=True,
        blank=True
    )

    profile_picture = models.ImageField(
        upload_to='employees/',
        blank=True,
        null=True
    )

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    bank_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    account_number = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    account_holder_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    ifsc_code = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    uan_number = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    pan_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    aadhaar_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    passport_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    pf_number = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    esi_number = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    emergency_contact_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    emergency_contact_relation = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )

    # --- Employee Profile Onboarding Status ---
    # PROFILE_PENDING: Employee must complete personal/profile information.
    # PROFILE_SUBMITTED: Employee has submitted the profile for HR review.
    # HR_REVIEW: HR is currently reviewing/updating the profile.
    # ACTIVE: HR has approved the profile and normal dashboard access is allowed.
    PROFILE_STATUS_CHOICES = [
        ('PROFILE_PENDING', 'Profile Pending'),
        ('PROFILE_SUBMITTED', 'Profile Submitted'),
        ('HR_REVIEW', 'HR Review'),
        ('ACTIVE', 'Active'),
    ]

    profile_status = models.CharField(
        max_length=20,
        choices=PROFILE_STATUS_CHOICES,
        default='PROFILE_PENDING',
        db_index=True
    )

    profile_submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        # Best practice: use a fallback if user relation isn't loaded yet
        email = self.user.email if self.user else "No User"
        return f"{self.employee_id} - {email}"

# ==========================================
# Attendance Model
# ==========================================

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('HALF_DAY', 'Half Day'),
    ]

    SOURCE_CHOICES = [
        ('WEB', 'Web'),
        ('MOBILE', 'Mobile'),
        ('BIOMETRIC', 'Biometric'),
        ('MANUAL', 'Manual HR Entry'),
        ('API', 'API'),
    ]

    SHIFT_CHOICES = [
        ('MORNING', 'Morning Shift'),
        ('GENERAL', 'General Shift'),
        ('EVENING', 'Evening Shift'),
        ('NIGHT', 'Night Shift'),
        ('FLEXIBLE', 'Flexible'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )
    date = models.DateField()
    check_in = models.TimeField(
        null=True,
        blank=True
    )
    check_out = models.TimeField(
        null=True,
        blank=True
    )
    ABCeduled_check_in = models.TimeField(
        default=time(9, 0)
    )
    ABCeduled_check_out = models.TimeField(
        default=time(18, 0)
    )
    shift_name = models.CharField(
        max_length=30,
        choices=SHIFT_CHOICES,
        default='GENERAL'
    )
    attendance_source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='WEB'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PRESENT'
    )
    remarks = models.TextField(
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date', '-check_in']

    def __str__(self):
        return f"{self.employee.employee_id} - {self.date}"


# ==========================================
# Announcement Model
# ==========================================

class Announcement(models.Model):
    title = models.CharField(
        max_length=200
    )
    message = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# ==========================================
# Employee Documents Model
# ==========================================

# ==========================================
# ENHANCED DOCUMENT MANAGEMENT
# Replace the existing EmployeeDocument class
# with this class, then keep the rest of models.py.
# ==========================================

class EmployeeDocument(models.Model):
    CATEGORY_CHOICES = [
        ('IDENTITY', 'Identity'),
        ('EMPLOYMENT', 'Employment'),
        ('PAYROLL', 'Payroll / Compliance'),
        ('EDUCATION', 'Education'),
        ('OTHER', 'Other'),
    ]

    DOCUMENT_TYPES = [
        ('AADHAAR', 'Aadhaar'),
        ('PAN', 'PAN'),
        ('PASSPORT', 'Passport'),
        ('VOTER_ID', 'Voter ID'),
        ('RESUME', 'Resume'),
        ('OFFER_LETTER', 'Offer Letter'),
        ('APPOINTMENT_LETTER', 'Appointment Letter'),
        ('CONTRACT', 'Employment Contract'),
        ('NDA', 'NDA'),
        ('EXPERIENCE_LETTER', 'Experience Letter'),
        ('RELIEVING_LETTER', 'Relieving Letter'),
        ('BANK_PROOF', 'Bank Proof'),
        ('PF', 'PF'),
        ('ESI', 'ESI'),
        ('UAN', 'UAN'),
        ('CERTIFICATE', 'Certificate'),
        ('MARKSHEET', 'Marksheet'),
        ('DEGREE', 'Degree Certificate'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SENT_BACK', 'Sent Back'),
        ('EXPIRED', 'Expired'),
    ]

    CONFIDENTIALITY_CHOICES = [
        ('NORMAL', 'Normal'),
        ('CONFIDENTIAL', 'Confidential'),
        ('HIGHLY_CONFIDENTIAL', 'Highly Confidential'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default='OTHER'
    )

    title = models.CharField(
        max_length=200
    )

    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPES
    )

    document_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    issue_date = models.DateField(
        blank=True,
        null=True
    )

    expiry_date = models.DateField(
        blank=True,
        null=True
    )

    confidentiality = models.CharField(
        max_length=30,
        choices=CONFIDENTIALITY_CHOICES,
        default='NORMAL'
    )

    file = models.FileField(
        upload_to='employee_documents/'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_employee_documents'
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_employee_documents'
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['employee', 'document_type']),
            models.Index(fields=['status', 'expiry_date']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.employee.employee_id} - {self.title}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return bool(self.expiry_date and self.expiry_date < timezone.localdate())

    @property
    def expires_soon(self):
        from django.utils import timezone
        from datetime import timedelta
        if not self.expiry_date:
            return False
        today = timezone.localdate()
        return today <= self.expiry_date <= today + timedelta(days=30)


class DocumentVersion(models.Model):
    document = models.ForeignKey(
        EmployeeDocument,
        on_delete=models.CASCADE,
        related_name='versions'
    )

    version_number = models.PositiveIntegerField()

    file = models.FileField(
        upload_to='employee_documents/versions/'
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    note = models.TextField(
        blank=True,
        null=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-version_number']
        constraints = [
            models.UniqueConstraint(
                fields=['document', 'version_number'],
                name='unique_document_version'
            )
        ]

    def __str__(self):
        return f"{self.document.title} - v{self.version_number}"

class Asset(models.Model):

    # Asset lifecycle / procurement fields
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    model_name = models.CharField(max_length=150, blank=True, null=True)
    vendor = models.CharField(max_length=150, blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    warranty_start = models.DateField(blank=True, null=True)
    warranty_end = models.DateField(blank=True, null=True)
    assignment_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    condition = models.CharField(max_length=20, default='GOOD')
    location = models.CharField(max_length=150, blank=True, null=True)



    ASSET_TYPES = [
        ('LAPTOP', 'Laptop'),
        ('DESKTOP', 'Desktop'),
        ('MONITOR', 'Monitor'),
        ('MOBILE', 'Mobile'),
        ('SIM', 'SIM Card'),
        ('PRINTER', 'Printer'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('ASSIGNED', 'Assigned'),
        ('REPAIR', 'Under Repair'),
        ('LOST', 'Lost'),
        ('RETIRED', 'Retired'),
    ]

    asset_name = models.CharField(
        max_length=200
    )

    asset_code = models.CharField(
        max_length=100,
        unique=True
    )

    asset_type = models.CharField(
        max_length=50,
        choices=ASSET_TYPES
    )

    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets'
    )

    purchase_date = models.DateField()

    asset_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AVAILABLE'
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    

    def __str__(self):
        return f"{self.asset_code} - {self.asset_name}"
    
               
class EmployeeLifecycle(models.Model):

    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE
    )

    # Onboarding

    offer_letter_issued = models.BooleanField(default=False)

    documents_verified = models.BooleanField(default=False)

    email_created = models.BooleanField(default=False)

    laptop_assigned = models.BooleanField(default=False)

    id_card_issued = models.BooleanField(default=False)

    training_completed = models.BooleanField(default=False)

    # Offboarding

    exit_initiated = models.BooleanField(default=False)

    assets_returned = models.BooleanField(default=False)

    fnf_completed = models.BooleanField(default=False)

    relieving_letter_issued = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def onboarding_percentage(self):

        completed = sum([
            self.offer_letter_issued,
            self.documents_verified,
            self.email_created,
            self.laptop_assigned,
            self.id_card_issued,
            self.training_completed
        ])

        return int((completed / 6) * 100)

    def __str__(self):

        return self.employee.employee_id


# ==========================================
# Asset Lifecycle History
# ==========================================

class AssetHistory(models.Model):
    ACTION_CHOICES = [
        ('CREATED', 'Created'),
        ('ASSIGNED', 'Assigned'),
        ('TRANSFERRED', 'Transferred'),
        ('RETURNED', 'Returned'),
        ('REPAIR', 'Sent for Repair'),
        ('REPAIRED', 'Repair Completed'),
        ('LOST', 'Marked Lost'),
        ('DAMAGED', 'Marked Damaged'),
        ('RETIRED', 'Retired'),
        ('DISPOSED', 'Disposed'),
        ('UPDATED', 'Updated'),
    ]

    asset = models.ForeignKey(
        'Asset',
        on_delete=models.CASCADE,
        related_name='history'
    )

    action = models.CharField(max_length=30, choices=ACTION_CHOICES)

    from_employee = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_history_from'
    )

    to_employee = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_history_to'
    )

    event_date = models.DateTimeField(auto_now_add=True)

    notes = models.TextField(blank=True, null=True)

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asset_history_actions'
    )

    class Meta:
        ordering = ['-event_date', '-id']

    def __str__(self):
        return f"{self.asset.asset_code} - {self.get_action_display()}"

