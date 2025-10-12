from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from tickets.models import Ticket

class Command(BaseCommand):
    help = 'Automatically escalates tickets pending beyond SLA to L2 staff'

    def handle(self, *args, **options):
        SLA_MINUTES = 1   # set your SLA time here
        now = timezone.now()

        # Find tickets that are still pending and SLA expired
        tickets_to_escalate = Ticket.objects.filter(
            status='pending',
            status_changed_at__lt=now - timedelta(minutes=SLA_MINUTES)
        ).exclude(status__in=['verified', 'closed'])
        
        print("DEBUG", tickets_to_escalate)

        count = 0
        for ticket in tickets_to_escalate:
            ticket.status = 'escalated'
            ticket.save()  # save() handles history and status_changed_at
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Escalated {count} tickets.'))
