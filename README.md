# ABC HRMS Portal

A modern Human Resource Management System (HRMS) built with Django to streamline workforce management, recruitment, employee operations, performance reviews, payroll administration, and organizational reporting.

---

## Overview

ABC HRMS Portal is designed to centralize and automate core HR processes within an organization. The platform provides role-based access, employee lifecycle management, recruitment workflows, attendance tracking, leave management, document management, performance reviews, payroll support, audit tracking, and reporting capabilities.

---

## Key Features

### Authentication & Security

* Role-based authentication
* Secure login/logout
* Password reset functionality
* Session management

### Employee Management

* Employee onboarding
* Employee profiles
* Department assignment
* Employee status tracking
* Employee search and filtering

### Department Management

* Create departments
* Update departments
* Department-wise employee management

### Attendance Management

* Daily attendance tracking
* Check-in / Check-out
* Attendance history

### Leave Management

* Leave application workflow
* Leave approval and rejection
* Leave status tracking
* Supervisor review process

### Document Management System

* Employee document uploads
* Secure document access
* Document management and tracking

### Performance Management (PMR)

* Performance review submissions
* Supervisor evaluation
* Approval and resubmission workflow

### Promotion Management

* Promotion requests
* Promotion approvals
* Promotion letter generation (PDF)

### Resignation Management

* Resignation submission
* Approval workflow
* Employee exit process

### Recruitment Management

* Job requirement creation
* Applicant tracking
* Candidate shortlisting
* Candidate selection
* Employee onboarding workflow
* Applicant-to-employee conversion

### Payroll Support

* Payslip generation
* Payslip downloads

### Notifications

* System notifications
* Workflow alerts

### Audit Logs

* Activity tracking
* User action history
* Compliance monitoring

### Reporting

* Employee reports
* Attendance reports
* Leave reports
* Department reports

---

## Technology Stack

### Backend

* Python 3
* Django 5

### Frontend

* HTML5
* CSS3
* Bootstrap 5
* JavaScript

### Database

* SQLite3

### PDF Generation

* ReportLab

### Version Control

* Git
* GitHub

---

## Project Structure

```text
ABC HRMS Portal-Hrms/

├── apps/
│   ├── accounts/
│   ├── employees/
│   ├── leave/
│   ├── appraisal/
│   ├── promotions/
│   ├── resignation/
│   ├── recruitment/
│   ├── notifications/
│   ├── audit/
│   ├── payslips/
│   └── reports/
│
├── templates/
├── static/
├── media/
├── config/
├── db.sqlite3
├── manage.py
└── requirements.txt
```

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd ABC HRMS Portal-Hrms
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Git Bash:

```bash
source venv/Scripts/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Administrator Account

```bash
python manage.py createsuperuser
```

### Run Development Server

```bash
python manage.py runserver
```

### Access Application

```text
http://127.0.0.1:8000
```

---

## User Roles

### Supervisor

* Full system access
* Employee management
* Recruitment management
* Leave approvals
* PMR approvals
* Reports access
* Audit monitoring

### Employee

* Personal profile access
* Attendance management
* Leave requests
* Document uploads
* PMR submissions
* Payslip access

---

## Generated Documents

* Promotion Letters (PDF)
* Payslips (PDF)

---

## Future Enhancements

* Email notifications
* Advanced analytics dashboard
* Multi-level approval workflows
* Cloud deployment support
* Mobile application
* API integrations

---

## License

This project is proprietary software developed for organizational HR operations.

---

## Author

Developed and maintained by Rahul N.
