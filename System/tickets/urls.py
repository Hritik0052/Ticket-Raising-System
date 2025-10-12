from django.urls import path
from . import views

app_name = "tickets"
urlpatterns = [
    path("raise/", views.raise_ticket, name="raise_ticket"),
    path("check/", views.check_status, name="check_status"),
    path("verify-status/", views.verify_status_otp, name="verify_status_otp"),
    path("l1-dashboard/", views.l1_dashboard, name="l1_dashboard"),
    path("l1-dashboard/processed/", views.processed_tickets, name="processed_tickets"),
    path("l2-dashboard/", views.l2_dashboard, name="l2_dashboard"),
    path("l1/verify/<str:ticket_id>/", views.verify_ticket, name="verify_ticket"),
    path("l2/update/<str:ticket_id>/", views.update_ticket_status, name="update_ticket_status"),
    path("details/<str:ticket_id>/", views.ticket_detail, name='ticket_detail'),
]

