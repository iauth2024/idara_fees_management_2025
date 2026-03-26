# views.py
import csv
import datetime
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from fees_collection.models import Student
from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak

from .forms import LeaveRequestForm
from .models import LeaveRequest, StaffProfile, LeaveApprovalHistory, LeaveEvent
from .services import initiate_leave, approve_leave, reject_leave, mark_checkin


# ============================================================================
# DASHBOARD VIEWS
# ============================================================================

@login_required
def leave_dashboard(request):
    """Main dashboard with statistics and metrics"""
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    total_students = Student.objects.count()

    students_on_leave = LeaveRequest.objects.filter(
        status="approved",
        start_date__lte=today,
        end_date__gte=today
    ).count()

    overdue_students = LeaveRequest.objects.filter(
        status="approved",
        end_date__lt=today
    ).count()

    today_checkins = LeaveRequest.objects.filter(
        check_in_date__date=today
    ).count()

    monthly_leaves = LeaveRequest.objects.filter(
        start_date__month=current_month,
        start_date__year=current_year
    ).count()

    rejected_leaves = LeaveRequest.objects.filter(
        status="rejected"
    ).count()

    # Department-wise approvals
    dept_approvals = LeaveApprovalHistory.objects.filter(
        action="approved"
    ).values("department").annotate(total=Count("id"))

    dept_rejections = LeaveApprovalHistory.objects.filter(
        action="rejected"
    ).values("department").annotate(total=Count("id"))

    super_admin_approvals = LeaveApprovalHistory.objects.filter(
        action="approved",
        action_by__is_super_admin=True
    ).count()

    context = {
        "total_students": total_students,
        "students_on_leave": students_on_leave,
        "overdue_students": overdue_students,
        "today_checkins": today_checkins,
        "monthly_leaves": monthly_leaves,
        "rejected_leaves": rejected_leaves,
        "dept_approvals": dept_approvals,
        "dept_rejections": dept_rejections,
        "super_admin_approvals": super_admin_approvals,
    }

    return render(request, "leave_management/dashboard.html", context)


# ============================================================================
# LEAVE REQUEST VIEWS
# ============================================================================


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from .models import LeaveRequest


@login_required
def leave_list(request):
    """List all leave requests with filtering"""
    staff_profile = request.user.staffprofile
    today = timezone.now().date()

    # All leaves
    all_leaves = LeaveRequest.objects.select_related("student", "initiated_by").order_by("-created_at")

    # Pending approvals for department - using current_pending_department
    pending_for_me = LeaveRequest.objects.filter(
        status="pending",
        current_pending_department=staff_profile.department
    ).select_related("student", "initiated_by").order_by("-created_at")

    # Today's approved leaves (students currently on leave)
    today_approved = LeaveRequest.objects.filter(
        status="approved",
        start_date__lte=today,
        end_date__gte=today
    ).select_related("student").distinct().order_by("-created_at")

    context = {
        "all_leaves": all_leaves,
        "pending_for_me": pending_for_me,
        "today_approved": today_approved,
        "today": today
    }

    return render(request, "leave_management/leave_list.html", context)

# views.py - Updated create_leave_view

@login_required
def create_leave_view(request):
    try:
        staff_profile = request.user.staffprofile
    except StaffProfile.DoesNotExist:
        messages.error(request, "Staff profile not found.")
        return redirect("leave_list")

    if request.method == "POST":
        form = LeaveRequestForm(request.POST)

        if form.is_valid():
            admission_number = form.cleaned_data["admission_number"]
            start_date = form.cleaned_data["start_date"]
            start_time = form.cleaned_data["start_time"]
            end_date = form.cleaned_data["end_date"]
            end_time = form.cleaned_data["end_time"]
            reason = form.cleaned_data["reason"]
            notes = form.cleaned_data.get("notes")

            try:
                student = Student.objects.get(admission_number=admission_number)

                # Call updated service function with all parameters
                leave = initiate_leave(
                    student=student,
                    staff_profile=staff_profile,
                    start_date=start_date,
                    start_time=start_time,
                    end_date=end_date,
                    end_time=end_time,
                    reason=reason,
                    notes=notes
                )

                days = leave.total_days()
                messages.success(
                    request, 
                    f"✅ Leave application submitted successfully for {student.name}. "
                    f"Total duration: {days} day{'s' if days > 1 else ''}"
                )
                return redirect("leave_list")

            except Student.DoesNotExist:
                messages.error(request, f"❌ Student with admission number {admission_number} not found.")
            except ValidationError as e:
                messages.error(request, f"❌ {str(e)}")
            except Exception as e:
                messages.error(request, f"❌ Error creating leave: {str(e)}")

    else:
        form = LeaveRequestForm()

    return render(request, "leave_management/create_leave.html", {
        "form": form
    })

@login_required
def approve_leave_view(request, pk):
    """Approve a leave request"""
    leave = get_object_or_404(LeaveRequest, pk=pk)

    try:
        staff_profile = request.user.staffprofile

        # Prevent approving already approved leave
        if leave.status == "approved":
            messages.warning(request, "Leave already approved.")
            return redirect("leave_list")

        # Prevent approving rejected leave
        if leave.status == "rejected":
            messages.warning(request, "Cannot approve a rejected leave.")
            return redirect("leave_list")

        # Check if user is authorized for this department's pending approvals
        if leave.current_pending_department != staff_profile.department:
            messages.error(request, f"This leave is not pending in your department. It's pending in {leave.current_pending_department}.")
            return redirect("leave_list")

        # Determine next department based on current
        if staff_profile.department == "taleemat":
            # Taleemat approves, next is intizamia
            leave.current_pending_department = "intizamia"
            
            # Create approval history
            LeaveApprovalHistory.objects.create(
                leave=leave,
                action_by=staff_profile,
                department=staff_profile.department,
                action="approved",
                remarks=f"Approved by {staff_profile.user.get_full_name()} (Taleemat)"
            )
            
            messages.success(request, "Leave approved by Taleemat. Now pending in Intizamia.")
            
        elif staff_profile.department == "intizamia":
            # Intizamia approves, final approval
            leave.status = "approved"
            leave.current_pending_department = None  # No longer pending
            leave.final_decision_at = timezone.now()
            
            # Create approval history
            LeaveApprovalHistory.objects.create(
                leave=leave,
                action_by=staff_profile,
                department=staff_profile.department,
                action="approved",
                remarks=f"Final approval by {staff_profile.user.get_full_name()} (Intizamia)"
            )
            
            messages.success(request, "Leave fully approved.")
            
        elif staff_profile.is_super_admin:
            # Super admin can approve directly
            leave.status = "approved"
            leave.current_pending_department = None
            leave.final_decision_at = timezone.now()
            
            LeaveApprovalHistory.objects.create(
                leave=leave,
                action_by=staff_profile,
                department="admin",
                action="approved",
                remarks=f"Approved by Super Admin: {staff_profile.user.get_full_name()}"
            )
            
            messages.success(request, "Leave approved by Super Admin.")
            
        else:
            messages.error(request, "You are not authorized to approve leaves.")
            return redirect("leave_list")

        leave.save()

    except ValidationError as e:
        messages.error(request, str(e))

    return redirect("leave_list")

@login_required
def reject_leave_view(request, pk):
    """Reject a leave request"""
    leave = get_object_or_404(LeaveRequest, pk=pk)

    try:
        staff_profile = request.user.staffprofile

        # Prevent rejecting already approved leave
        if leave.status == "approved":
            messages.warning(request, "Approved leave cannot be rejected.")
            return redirect("leave_list")

        # Prevent rejecting already rejected leave
        if leave.status == "rejected":
            messages.warning(request, "Leave already rejected.")
            return redirect("leave_list")

        # Check if user is authorized for this department's pending approvals
        if leave.current_pending_department != staff_profile.department and not staff_profile.is_super_admin:
            messages.error(request, f"This leave is not pending in your department. It's pending in {leave.current_pending_department}.")
            return redirect("leave_list")

        # Department check
        if staff_profile.department not in ["taleemat", "intizamia"] and not staff_profile.is_super_admin:
            messages.error(request, "You are not authorized to reject this leave.")
            return redirect("leave_list")

        # Reject leave
        leave.status = "rejected"
        leave.current_pending_department = None  # Clear pending department
        leave.final_decision_at = timezone.now()
        
        # Create rejection history
        remarks = f"Rejected by {staff_profile.user.get_full_name()}"
        if staff_profile.is_super_admin:
            remarks = f"Rejected by Super Admin: {staff_profile.user.get_full_name()}"
            
        LeaveApprovalHistory.objects.create(
            leave=leave,
            action_by=staff_profile,
            department=staff_profile.department if not staff_profile.is_super_admin else "admin",
            action="rejected",
            remarks=remarks
        )
        
        leave.save()
        messages.success(request, "Leave rejected successfully.")

    except ValidationError as e:
        messages.error(request, str(e))

    return redirect("leave_list")
@login_required
def checkin_view(request, pk):
    """Mark student check-in for leave"""
    leave = get_object_or_404(LeaveRequest, pk=pk)
    staff_profile = request.user.staffprofile

    # Only approved leaves can be checked in
    if leave.status != "approved":
        messages.error(request, "Only approved leaves can be checked in.")
        return redirect("leave_list")

    # Prevent double check-in
    if leave.check_in_date:
        messages.warning(request, "Student already checked in.")
        return redirect("checkin_report")

    if request.method == "POST":
        custom_datetime = request.POST.get("checkin_datetime")
        notes = request.POST.get("notes")

        checkin_time = (
            timezone.datetime.fromisoformat(custom_datetime)
            if custom_datetime
            else timezone.now()
        )

        leave.status = "checked_in"
        leave.check_in_date = checkin_time
        leave.checked_in_by = staff_profile
        leave.save()

        messages.success(request, f"Student {leave.student.name} checked in successfully.")
        return redirect("checkin_report")

    return render(request, "leave_management/checkin_form.html", {
        "leave": leave
    })

# ============================================================================
# PRINT & REPORT VIEWS
# ============================================================================

@login_required
def print_leave_slip(request, pk):
    """Print individual leave slip"""
    leave = get_object_or_404(
        LeaveRequest.objects.select_related(
            "student",
            "initiated_by"
        ),
        pk=pk
    )

    history = leave.history.select_related("action_by").order_by("id")

    context = {
        "leave": leave,
        "history": history
    }

    return render(request, "leave_management/print_leave_slip.html", context)


@login_required
def print_event_slips(request):
    """Print leave slips for an event"""
    event_id = request.GET.get("event_id")
    section_filter = request.GET.get("section")
    
    event = get_object_or_404(LeaveEvent, id=event_id)
    
    # Get all students
    students = Student.objects.all()
    
    # Apply event filters if they exist
    if event.branch:
        branches = [b.strip() for b in event.branch.split(',')]
        students = students.filter(branch__in=branches)
    
    if event.course:
        courses = [c.strip() for c in event.course.split(',')]
        students = students.filter(course__in=courses)
    
    if event.section:
        sections = [s.strip() for s in event.section.split(',')]
        students = students.filter(section__in=sections)
    
    # Apply section filter from request
    if section_filter:
        students = students.filter(section=section_filter)
    
    # Check if PDF download is requested
    if request.GET.get('format') == 'pdf':
        return generate_pdf_slips(event, students)
    
    # Regular HTML view
    return render(request, "leave_management/print_event_slips.html", {
        "event": event,
        "students": students,
        "students_count": students.count(),
        "section_filter": section_filter,
        "current_date": datetime.datetime.now()
    })


def generate_pdf_slips(event, students):
    """Generate PDF with leave slips for all students - Half A4 size (A5)"""
    buffer = BytesIO()
    
    # Use A5 size (half of A4) - portrait orientation
    doc = SimpleDocTemplate(buffer, pagesize=A5,
                           rightMargin=36, leftMargin=36,
                           topMargin=36, bottomMargin=36)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles for A5 size
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#667eea'),
        alignment=1,
        spaceAfter=20,
        leading=16
    )
    
    subheading_style = ParagraphStyle(
        'Subheading',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.HexColor('#28a745'),
        alignment=0,
        spaceAfter=10,
        leading=14
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=9,
        leading=12
    )
    
    # Add header for each student
    for i, student in enumerate(students):
        # Title
        story.append(Paragraph("LEAVE SLIP", title_style))
        story.append(Paragraph(f"{event.name}", normal_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Event details
        event_data = [
            ["Event:", event.name],
            ["From:", event.start_date.strftime('%d/%m/%Y')],
            ["To:", event.end_date.strftime('%d/%m/%Y')],
        ]
        
        event_table = Table(event_data, colWidths=[1*inch, 3*inch])
        event_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(event_table)
        story.append(Spacer(1, 0.1*inch))
        
        # Student details
        story.append(Paragraph("<b>STUDENT DETAILS</b>", subheading_style))
        
        student_data = [
            ["Name:", student.name],
            ["Adm No:", student.admission_number],
            ["Branch:", student.branch],
            ["Course:", student.course],
            ["Section:", student.section],
        ]
        
        student_table = Table(student_data, colWidths=[1*inch, 3*inch])
        student_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(student_table)
        
        # Signature section
        story.append(Spacer(1, 0.2*inch))
        
        signature_data = [
            ["Student", "Parent", "Authority"],
            ["__________", "__________", "__________"],
            ["(with date)", "(with date)", "(with date)"],
        ]
        
        signature_table = Table(signature_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
        signature_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#666666')),
        ]))
        story.append(signature_table)
        
        # Date and slip number
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"Date: {datetime.datetime.now().strftime('%d/%m/%Y')}", normal_style))
        story.append(Paragraph(f"Slip #{i+1}/{len(students)}", normal_style))
        
        # Add page break after each slip except the last
        if i < len(students) - 1:
            story.append(PageBreak())
    
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    filename = f"leave_slips_{event.name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filename = filename.replace(' ', '_')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf)
    
    return response


# ============================================================================
# REPORT VIEWS
# ============================================================================

@login_required
def leave_reports(request):
    """Generate leave reports with filters"""
    leaves = LeaveRequest.objects.select_related("student").all().order_by("-start_date")

    # Apply filters
    adm_no = request.GET.get("adm_no")
    name = request.GET.get("name")
    branch = request.GET.get("branch")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if adm_no:
        leaves = leaves.filter(student__admission_number__icontains=adm_no)

    if name:
        leaves = leaves.filter(student__name__icontains=name)

    if branch:
        leaves = leaves.filter(student__branch__icontains=branch)

    if from_date:
        leaves = leaves.filter(start_date__gte=from_date)

    if to_date:
        leaves = leaves.filter(end_date__lte=to_date)

    # Prepare report data
    report_data = []
    for leave in leaves:
        checkin = leave.check_in_date
        if checkin:
            late_status = "Late" if checkin.time().hour > 9 else "On Time"
        else:
            late_status = "Not Returned"

        report_data.append({
            "adm_no": leave.student.admission_number,
            "name": leave.student.name,
            "branch": leave.student.branch,
            "course": leave.student.course,
            "section": leave.student.section,
            "start_date": leave.start_date,
            "end_date": leave.end_date,
            "days": leave.total_days(),
            "status": leave.status,
            "checkin": leave.check_in_date,
            "late": late_status,
        })

    return render(request, "leave_management/reports.html", {"leaves": report_data})


@login_required
def download_leave_report(request):
    """Download leave report as CSV"""
    leaves = LeaveRequest.objects.select_related('student').all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="leave_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Admission No",
        "Name",
        "Branch",
        "Course",
        "Section",
        "Start Date",
        "End Date",
        "Days",
        "Checkin",
        "Status"
    ])

    for leave in leaves:
        days = (leave.end_date - leave.start_date).days + 1
        checkin = leave.check_in_date
        late = "Late" if checkin and checkin.hour > 9 else "On Time"

        writer.writerow([
            leave.student.admission_number,
            leave.student.name,
            leave.student.branch,
            leave.student.course,
            leave.student.section,
            leave.start_date,
            leave.end_date,
            days,
            checkin,
            late
        ])

    return response


@login_required
def checkin_report(request):
    """Generate check-in report"""
    today = timezone.now().date()
    search_query = request.GET.get("search")

    base_queryset = LeaveRequest.objects.filter(status="approved")

    if search_query:
        base_queryset = base_queryset.filter(
            student__admission_number__icontains=search_query
        )

    today_returns = base_queryset.filter(end_date=today)
    overdue = base_queryset.filter(end_date__lt=today)
    future = base_queryset.filter(end_date__gt=today)

    context = {
        "today_returns": today_returns,
        "overdue": overdue,
        "future": future,
        "today": today,
    }

    return render(request, "leave_management/checkin_report.html", context)


# ============================================================================
# EVENT VIEWS
# ============================================================================

@login_required
def event_list(request):
    """List all leave events"""
    events = LeaveEvent.objects.all().order_by("-created_at")
    return render(request, "leave_management/event_list.html", {
        "events": events
    })


@login_required
def create_event(request):
    """Create a new leave event"""
    # Get dynamic lists from Student table
    branches = Student.objects.values_list("branch", flat=True).distinct()
    courses = Student.objects.values_list("course", flat=True).distinct()
    sections = Student.objects.values("section", "course").distinct()

    # Existing events for print dropdown
    events = LeaveEvent.objects.filter(status="active").order_by("-start_date")

    try:
        staff_profile = request.user.staffprofile
    except:
        staff_profile = None

    if request.method == "POST":
        name = request.POST.get("name")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        branches_selected = request.POST.getlist("branch")
        courses_selected = request.POST.getlist("course")
        sections_selected = request.POST.getlist("section")

        LeaveEvent.objects.create(
            name=name,
            start_date=start_date,
            end_date=end_date,
            branch=", ".join(branches_selected) if branches_selected else None,
            course=", ".join(courses_selected) if courses_selected else None,
            section=", ".join(sections_selected) if sections_selected else None,
            created_by=staff_profile
        )

        messages.success(request, "Holiday event created successfully.")
        return redirect("create_event")

    return render(request, "leave_management/create_event.html", {
        "branches": branches,
        "courses": courses,
        "sections": sections,
        "events": events
    })


@login_required
def cancel_event(request, event_id):
    """Cancel an event"""
    staff = request.user.staffprofile

    if not staff.is_super_admin:
        messages.error(request, "Only Super Admin can cancel events.")
        return redirect("event_list")

    event = get_object_or_404(LeaveEvent, id=event_id)
    leaves = LeaveRequest.objects.filter(event=event)

    for leave in leaves:
        if leave.status == "approved" and leave.check_in_date is None:
            leave.delete()
        else:
            leave.event = None
            leave.save()

    event.status = "cancelled"
    event.save()

    messages.success(request, "Event cancelled successfully.")
    return redirect("event_list")


# ============================================================================
# AJAX VIEWS
# ============================================================================

@login_required
def get_student_details(request):
    """Get student details via AJAX"""
    admission_number = request.GET.get("admission_number")

    try:
        student = Student.objects.get(admission_number=admission_number)
        data = {
            "name": student.name,
            "course": student.course,
            "section": student.section,
            "branch": student.branch,
        }
        return JsonResponse(data)

    except Student.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)