from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from fees_collection.models import Student


# ===============================
# Staff Profile
# ===============================
class StaffProfile(models.Model):

    DEPARTMENT_CHOICES = [
        ('taleemat', 'Taleemat'),
        ('intizamia', 'Intizamia'),
        ('admin', 'Super Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    is_super_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.department})"


# ===============================
# Holiday Event (Bulk Leave System)
# ===============================
class LeaveEvent(models.Model):

    STATUS_CHOICES = [
        ("active", "Active"),
        ("cancelled", "Cancelled"),
    ]

    name = models.CharField(max_length=200)

    start_date = models.DateField()
    end_date = models.DateField()

    branch = models.CharField(max_length=50, blank=True, null=True)
    course = models.CharField(max_length=50, blank=True, null=True)
    section = models.CharField(max_length=50, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    created_by = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)


# ===============================
# Leave Request (Core System)
# ===============================
class LeaveRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('checked_in', 'Checked In'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT
    )

    initiated_by = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='initiated_leaves'
    )

    start_date = models.DateField()
    start_time = models.TimeField(default="09:00")
    end_date = models.DateField()
    end_time = models.TimeField(default="17:00")
    notes = models.TextField(blank=True, null=True)
    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    current_pending_department = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # Link to holiday event (NEW FEATURE)
    event = models.ForeignKey(
        LeaveEvent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_leaves"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    final_decision_at = models.DateTimeField(null=True, blank=True)

    # Check-In Tracking
    check_in_date = models.DateTimeField(null=True, blank=True)

    checked_in_by = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checkins'
    )

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date")

    def total_days(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{self.student.name} ({self.start_date} → {self.end_date})"


# ===============================
# Leave Approval History (Audit Log)
# ===============================
class LeaveApprovalHistory(models.Model):

    ACTION_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    leave = models.ForeignKey(
        LeaveRequest,
        on_delete=models.CASCADE,
        related_name='history'
    )

    action_by = models.ForeignKey(
        StaffProfile,
        on_delete=models.SET_NULL,
        null=True
    )

    department = models.CharField(max_length=20)

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    remarks = models.TextField(null=True, blank=True)

    action_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.leave.student.name} - {self.action}"


# ===============================
# Leave Reason
# ===============================
class LeaveReason(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name