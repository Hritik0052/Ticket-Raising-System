import string
import random
from datetime import datetime
from .models import Ticket

def generate_unique_ticket_id(length=6):
    """
    Generates a unique ticket ID of given length.
    Combines timestamp + random uppercase letters/digits to ensure uniqueness.
    """
    while True:
        # Random uppercase letters + digits
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        
        # Optional: add a date prefix like YYMMDD
        # date_part = datetime.now().strftime("%y%m%d")
        # ticket_id = f"{date_part}{random_part}"
        ticket_id = random_part

        # Ensure uniqueness
        if not Ticket.objects.filter(ticket_id=ticket_id).exists():
            return ticket_id
