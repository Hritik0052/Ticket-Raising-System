from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now, timedelta
import uuid
from departments.models import Department, SubDepartment
from .models import Ticket, TicketHistory, TicketAttachment
from accounts.models import User
from notifications.models import OTP
from notifications.utils import generate_otp, send_otp_email
from .utils import generate_unique_ticket_id
from django.contrib import messages


# =================== User Level Views ======================

def raise_ticket(request):
    # Step 1: Check if user has verified OTP
    email = request.session.get("verified_email")
    if not email:
        # User hasn't verified email yet → redirect to OTP request
        return redirect("request_otp")

    ticket_id = generate_unique_ticket_id()
    # Step 2: Handle ticket submission
    if request.method == "POST":
        ticket = Ticket.objects.create(
            sender_name=request.POST.get("sender_name"),
            mobile_no=request.POST.get("mobile_no"),
            email=email,
            subject=request.POST.get("subject"),
            description=request.POST.get("description"),
            department_id=request.POST.get("department") or None,
            sub_department_id=request.POST.get("sub_department") or None,
            ticket_id=ticket_id
        )

        # Multiple attachments
        files = request.FILES.getlist("attachments")
        for f in files:
            TicketAttachment.objects.create(ticket=ticket, file=f)

        # Optional: remove verified email from session to force OTP next time
        del request.session["verified_email"]

        messages.success(request, "Ticket raised successfully!")
        return render(request, "tickets/success.html", {"ticket_id":ticket_id})  # or wherever you want

    # GET → show ticket form
    departments = Department.objects.all()
    sub_departments = SubDepartment.objects.all()
    return render(request, "tickets/raise_ticket.html", {
        "departments": departments,
        "sub_departments": sub_departments,
    })


# ================= Status Views ==========================

def check_status(request):
    if request.method == "POST":
        email = request.POST.get("email")
        request.session["status_check_email"] = email

        # Generate OTP and send email
        code = generate_otp(email)
        send_otp_email(email, code)

        return redirect("tickets:verify_status_otp")

    return render(request, "tickets/check_status.html")


def verify_status_otp(request):
    if request.method == "POST":
        email = request.session.get("status_check_email")
        code = request.POST.get("otp")
        otp_record = OTP.objects.filter(email=email, code=code, is_used=False).last()

        if otp_record and otp_record.created_at >= now() - timedelta(minutes=5):
            otp_record.is_used = True
            otp_record.save()

            tickets = Ticket.objects.filter(email=email).order_by("-created_at")
            return render(request, "tickets/status_list.html", {"tickets": tickets})

        return render(request, "tickets/verify_status_otp.html", {"error": "Invalid or expired OTP"})

    return render(request, "tickets/verify_status_otp.html")


# ==================== Staff Level Views ======================

# Role-based decorator
def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("admin:login")
            if request.user.role not in allowed_roles:
                return redirect("home")  # or some "access denied" page
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ---------- L1 Staff ----------
@login_required
@role_required(["staff_l1"])
def l1_dashboard(request):
    # Pending tickets from logged-in user's department
    pending_tickets = Ticket.objects.filter(
        department=request.user.department,
        status="pending"
    ).order_by("-created_at")

    # Processed tickets (only latest 2)
    processed_tickets = Ticket.objects.filter(
        department=request.user.department,
        status__in=["verified", "rejected"]
    ).order_by("-created_at")[:2]

    more_processed_exists = Ticket.objects.filter(
        department=request.user.department,
        status__in=["verified", "rejected"]
    ).count() > 2

    return render(request, "tickets/l1_dashboard.html", {
        "pending_tickets": pending_tickets,
        "processed_tickets": processed_tickets,
        "more_processed_exists": more_processed_exists
    })

# -------- Verify by Staff_l1 -------------------
@login_required
@role_required(["staff_l1"])
def verify_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, department=request.user.department)
    action = request.GET.get("action")  # 'verify' or 'reject'

    if action == "verify":
        ticket.status = "verified"
    elif action == "reject":
        ticket.status = "rejected"
    ticket.save()

    # Save history
    TicketHistory.objects.create(ticket=ticket, status=ticket.status, updated_by=request.user)

    return redirect("tickets:l1_dashboard")

# ---------------- show processed tickets by staff_l1 ---------
@login_required
@role_required(["staff_l1"])
def processed_tickets(request):
    tickets = Ticket.objects.filter(
        department=request.user.department,
        status__in=["verified", "rejected"]
    ).order_by("-created_at").prefetch_related("history")
    return render(request, "tickets/processed_tickets.html", {"tickets": tickets})



# --------------------- L2 Staff -----------------

@login_required
@role_required(["staff_l2"])
def l2_dashboard(request):
    """
    Fetch all tickets for this L2 staff's department
    that are verified, in_progress, or closed
    """
    tickets = Ticket.objects.filter(
        department=request.user.department,
        status__in=["verified", "in_progress", "closed", "escalated"]
    ).order_by("-created_at")

    # Prefetch related history for faster modal rendering
    tickets = tickets.prefetch_related("history")

    return render(request, "tickets/l2_dashboard.html", {"tickets": tickets})

@login_required
@role_required(["staff_l2"])
def update_ticket_status(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id, department=request.user.department)

    if ticket.status == "closed":
        return redirect("tickets:l2_dashboard")

    next_status = request.POST.get("status")
    remarks = request.POST.get("remarks", "").strip()

    # Pass info to signal via temporary attributes
    ticket._updated_by = request.user
    ticket._remarks = remarks

    # Update ticket status
    ticket.status = next_status
    ticket.save(update_fields=["status"])

    return redirect("tickets:l2_dashboard")

# ============ View Ticket============

def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)

    # get all attachments for this ticket
    attachments = TicketAttachment.objects.filter(ticket=ticket)
    # attachments = ticket.attachments.all()
  
    # get ticket history
    history = TicketHistory.objects.filter(ticket=ticket).order_by('-updated_at') \
              if hasattr(ticket, 'tickethistory_set') else []

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'history': history,
        'attachments': attachments
    })
