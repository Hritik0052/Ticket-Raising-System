from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLES = (
        ('superadmin', 'SuperAdmin'),
        ('staff_l1', 'Staff L1'),
        ('staff_l2', 'Staff L2'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='staff_l1')
    mobile=models.CharField(null=True, blank=True, max_length=10)
    department = models.ForeignKey(
        'departments.Department',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="users"
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
