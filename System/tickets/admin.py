from django.contrib import admin
from .models import Ticket, TicketHistory, TicketAttachment

# Register your models here.
admin.site.register(Ticket)
admin.site.register(TicketHistory)
admin.site.register(TicketAttachment)