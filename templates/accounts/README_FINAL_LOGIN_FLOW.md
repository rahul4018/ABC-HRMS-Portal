# Final HRMS Login Flow

## Master Admin

User ID:
`ABCadmin`

Password:
`ABC HRMS Portal2025`

This account is not an employee.

## Employees

Business Employee IDs remain:

`EMP1` ... `EMP40`

Login User IDs are:

`ABC1` ... `ABC40`

Temporary password for every employee:

`temp@123`

## Contractors

Business Employee IDs remain:

`C1` ... `C5`

Login User IDs are:

`ABCC1` ... `ABCC5`

Temporary password:

`temp@123`

## First Login

1. User enters User ID.
2. User enters `temp@123`.
3. Authentication succeeds.
4. `must_change_password=True` sends the user to Change Password.
5. User enters Old Password.
6. User enters New Password.
7. User enters Confirm New Password.
8. Password is saved.
9. `must_change_password=False`.
10. User is logged out.
11. User is returned to Login.
12. User logs in with the new password.

## Email

Employee email addresses stay blank for now.
Email can be added later without changing the User ID.

## Forgot Password

There is no public email reset at this stage.
The user is directed to HR / Master Admin for an authorized reset.
