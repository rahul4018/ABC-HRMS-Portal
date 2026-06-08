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
        default='Bangalore'
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
        ordering = ['-date']

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

class EmployeeDocument(models.Model):
    DOCUMENT_TYPES = [
        ('AADHAAR', 'Aadhaar'),
        ('PAN', 'PAN'),
        ('RESUME', 'Resume'),
        ('CERTIFICATE', 'Certificate'),
        ('CONTRACT', 'Contract'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SENT_BACK', 'Sent Back'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    title = models.CharField(
        max_length=200
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPES
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
    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f"{self.employee.employee_id} - {self.title}"
    
# ==========================================
# Asset Management
# ==========================================

class Asset(models.Model):

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
        
        offer_letter_issued = models.BooleanField(default=False)
        documents_verified = models.BooleanField(default=False)
        email_created = models.BooleanField(default=False)
        laptop_assigned = models.BooleanField(default=False)
        id_card_issued = models.BooleanField(default=False)
        training_completed = models.BooleanField(default=False)

        exit_initiated = models.BooleanField(default=False)
        assets_returned = models.BooleanField(default=False)
        fnf_completed = models.BooleanField(default=False)
        relieving_letter_issued = models.BooleanField(default=False)

        created_at = models.DateTimeField(auto_now_add=True)

        def onboarding_completion(self):
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