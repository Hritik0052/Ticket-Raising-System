from django.db import models
from django.utils import timezone
from accounts.models import User
from departments.models import Department, SubDepartment

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
        ('escalated', 'Escalated'),
    )

    sender_name = models.CharField(max_length=100, null=True, blank=True, default="Anonymous")
    mobile_no = models.CharField(max_length=15, null=True, blank=True, default="Not Provided")
    email = models.EmailField(null=True, blank=True)
    ticket_id = models.CharField(max_length=20, unique=True)  # Unique ID for user reference
    subject = models.CharField(max_length=200)
    description = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    status_changed_at = models.DateTimeField(auto_now_add=True)

    sub_department = models.ForeignKey(
        SubDepartment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="tickets"
    )

    def __str__(self):
        return f"{self.ticket_id} - {self.subject} ({self.status})"

    def save(self, *args, **kwargs):
        self._old_status = None
        if self.pk:
            old = Ticket.objects.get(pk=self.pk)
            self._old_status = old.status
            if old.status != self.status:
                self.status_changed_at = timezone.now()
        else:
            self.status_changed_at = timezone.now()
        super().save(*args, **kwargs)



class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="ticket_attachments/", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticket.ticket_id} - {self.file.name}"


class TicketHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=20)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.ticket.ticket_id} - {self.status} by {self.updated_by}"
