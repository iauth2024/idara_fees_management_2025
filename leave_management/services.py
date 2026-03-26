# services.py

from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import LeaveRequest, LeaveApprovalHistory


def initiate_leave(student, staff_profile, start_date, start_time, end_date, end_time, reason, notes=None):
    """
    Create new leave request with time fields.
    """

    # Validate dates
    if end_date < start_date:
        raise ValidationError("End date cannot be before start date")
    
    # Validate times on same day
    if start_date == end_date and end_time <= start_time:
        raise ValidationError("End time must be after start time on the same day")

    # Determine next department
    if staff_profile.is_super_admin:
        status = "approved"
        pending_dept = None
        final_time = timezone.now()
    else:
        status = "pending"
        pending_dept = (
            "intizamia"
            if staff_profile.department == "taleemat"
            else "taleemat"
        )
        final_time = None

    leave = LeaveRequest.objects.create(
        student=student,
        initiated_by=staff_profile,
        start_date=start_date,
        start_time=start_time,  # New field
        end_date=end_date,
        end_time=end_time,      # New field
        reason=reason,
        notes=notes,            # New field
        status=status,
        current_pending_department=pending_dept,
        final_decision_at=final_time,
    )

    # If super admin → auto approve history
    if staff_profile.is_super_admin:
        LeaveApprovalHistory.objects.create(
            leave=leave,
            action_by=staff_profile,
            department=staff_profile.department,
            action="approved",
            remarks=f"Auto-approved by Super Admin with {leave.total_days()} days leave"
        )
    else:
        # Create pending history
        LeaveApprovalHistory.objects.create(
            leave=leave,
            action_by=staff_profile,
            department=staff_profile.department,
            action="pending",
            remarks=f"Leave initiated for {leave.total_days()} days"
        )

    return leave


def approve_leave(leave, staff_profile, remarks=None):
    """
    Approve leave according to workflow.
    """

    if leave.status != "pending":
        raise ValidationError("Leave is not pending.")

    if staff_profile.department != leave.current_pending_department and not staff_profile.is_super_admin:
        raise ValidationError("You are not authorized to approve this leave.")

    # Create approval history
    history = LeaveApprovalHistory.objects.create(
        leave=leave,
        action_by=staff_profile,
        department=staff_profile.department,
        action="approved",
        remarks=remarks or f"Approved by {staff_profile.department} department",
    )

    # Check if this is the final approval
    if staff_profile.department == "intizamia" or staff_profile.is_super_admin:
        # Final approval
        leave.status = "approved"
        leave.current_pending_department = None
        leave.final_decision_at = timezone.now()
        
        # Add completion remark
        history.remarks += " - Final approval completed"
        history.save()
    else:
        # Move to next department
        leave.current_pending_department = "intizamia"
        
    leave.save()

    return leave


def reject_leave(leave, staff_profile, remarks=None):
    """
    Reject leave request.
    """

    if leave.status != "pending":
        raise ValidationError("Leave is not pending.")

    if staff_profile.department != leave.current_pending_department and not staff_profile.is_super_admin:
        raise ValidationError("You are not authorized to reject this leave.")

    LeaveApprovalHistory.objects.create(
        leave=leave,
        action_by=staff_profile,
        department=staff_profile.department,
        action="rejected",
        remarks=remarks or f"Rejected by {staff_profile.department} department",
    )

    leave.status = "rejected"
    leave.current_pending_department = None
    leave.final_decision_at = timezone.now()
    leave.save()

    return leave


def mark_checkin(leave, staff_profile, checkin_time=None, notes=None):
    """
    Mark student as checked in.
    """

    if leave.status != "approved":
        raise ValidationError("Only approved leave can be checked in.")
    
    if leave.check_in_date:
        raise ValidationError("Student already checked in.")

    checkin_time = checkin_time or timezone.now()
    
    leave.status = "checked_in"
    leave.check_in_date = checkin_time
    leave.checked_in_by = staff_profile
    leave.save()

    # Create check-in history
    LeaveApprovalHistory.objects.create(
        leave=leave,
        action_by=staff_profile,
        department=staff_profile.department,
        action="checked_in",
        remarks=notes or f"Checked in by {staff_profile.user.get_full_name()}",
    )

    return leave


def get_leave_duration(leave):
    """
    Helper function to calculate leave duration in days
    """
    return leave.total_days()


def is_leave_active(leave, date=None):
    """
    Check if leave is active on a given date
    """
    if leave.status != "approved":
        return False
    
    check_date = date or timezone.now().date()
    return leave.start_date <= check_date <= leave.end_date


def get_department_pending_count(department):
    """
    Get count of pending leaves for a department
    """
    return LeaveRequest.objects.filter(
        status="pending",
        current_pending_department=department
    ).count()