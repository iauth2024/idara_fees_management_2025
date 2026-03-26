from django.contrib import admin
from .models import StaffProfile, LeaveRequest, LeaveApprovalHistory,LeaveReason


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'is_super_admin')
    list_filter = ('department', 'is_super_admin')
@admin.register(LeaveReason)
class LeaveReasonAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

class LeaveApprovalInline(admin.TabularInline):
    model = LeaveApprovalHistory
    extra = 0
    readonly_fields = ('action_by', 'department', 'action', 'action_time')


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'status', 'current_pending_department', 'start_date', 'end_date')
    list_filter = ('status', 'current_pending_department')
    inlines = [LeaveApprovalInline]


@admin.register(LeaveApprovalHistory)
class LeaveApprovalHistoryAdmin(admin.ModelAdmin):
    list_display = ('leave', 'action_by', 'department', 'action', 'action_time')
    list_filter = ('department', 'action')

from django.contrib import admin
from .models import LeaveEvent


@admin.register(LeaveEvent)
class LeaveEventAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "start_date",
        "end_date",
        "branch",
        "course",
        "section",
        "created_by",
    )

    list_filter = (
        "branch",
        "course",
        "section",
    )

    search_fields = (
        "name",
    )