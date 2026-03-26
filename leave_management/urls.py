# leave_management/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.leave_dashboard, name="leave_dashboard"),
    path("list/", views.leave_list, name="leave_list"),
    path("create/", views.create_leave_view, name="create_leave"),
    path("<int:pk>/approve/", views.approve_leave_view, name="approve_leave"),
    path("<int:pk>/reject/", views.reject_leave_view, name="reject_leave"),
    path("<int:pk>/checkin/", views.checkin_view, name="checkin_leave"),
    path("student-details/", views.get_student_details, name="student_details"),
    path("checkin-report/", views.checkin_report, name="checkin_report"),
    path("reports/", views.leave_reports, name="leave_reports"),
    path("download-leave-report/", views.download_leave_report, name="download_leave_report"),
    path("events/", views.event_list, name="event_list"),
    path("events/create/", views.create_event, name="create_event"),
    path("events/print-slips/", views.print_event_slips, name="print_event_slips"),
    path("leave/print/<int:pk>/", views.print_leave_slip, name="print_leave_slip"),
    path("events/cancel/<int:event_id>/", views.cancel_event, name="cancel_event"),
]