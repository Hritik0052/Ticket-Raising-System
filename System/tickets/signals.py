from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ticket, TicketHistory
from notifications.utils import send_ticket_email

@receiver(post_save, sender=Ticket)
def create_ticket_history(sender, instance, created, **kwargs):
    if created:
        # Log when ticket is first created
        TicketHistory.objects.create(
            ticket=instance,
            status=instance.status,
            remarks="Ticket created"
        )
        send_ticket_email(instance, instance.status, None, "Ticket created")
    else:
        # Only log when status has changed
        old_status = getattr(instance, "_old_status", None)
        if old_status and old_status != instance.status:
            TicketHistory.objects.create(
                ticket=instance,
                status=instance.status,
                updated_by=getattr(instance, "_updated_by", None),
                remarks=getattr(instance, "_remarks", "Status updated")
            )
            send_ticket_email(
                ticket=instance,
                new_status=instance.status,
                updated_by=getattr(instance, "_updated_by", None),
                remarks=getattr(instance, "_remarks", "Status updated")
            )
