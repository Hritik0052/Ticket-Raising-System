import random
from django.core.mail import send_mail
from .models import OTP
from django.core.mail import send_mail
from django.conf import settings
from tickets.models import Ticket

def generate_otp(email):
    code = str(random.randint(100000, 999999))
    OTP.objects.create(email=email, code=code)
    return code

def send_otp_email(email, code):
    subject = "Your OTP Code"
    message = f"Your OTP is {code}. It will expire in 2 minutes."
    send_mail(subject, message, "no-reply@ticketsystem.com", [email])


from django.utils import timezone

def send_ticket_email(ticket, new_status, updated_by=None, remarks=None):
    # Recipient
    recipients = [ticket.email]

    # Email subject
    subject = f"Ticket #{ticket.ticket_id} status updated"

    # Get timestamp from last history
    last_history = ticket.history.order_by('-updated_at').first()
    updated_time = last_history.updated_at.strftime('%Y-%m-%d %H:%M') if last_history else timezone.now().strftime('%Y-%m-%d %H:%M')

    # Body
    updated_by_name = updated_by.username if updated_by else "System"
    remarks_text = remarks if remarks else "No remarks provided"
    body = f"""
Hello {ticket.sender_name},

The status of your ticket has been updated.

Ticket ID: {ticket.ticket_id}
Subject: {ticket.subject}
New Status: {new_status}
Updated By: {updated_by_name}
Remarks: {remarks_text}
Updated At: {updated_time}

You can login to check more details.

Regards,
Support Team
"""

    # Send email
    from django.core.mail import send_mail
    from django.conf import settings

    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
    )
