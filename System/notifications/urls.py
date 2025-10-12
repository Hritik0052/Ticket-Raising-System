from django.urls import path
from . import views

urlpatterns = [
    path("request/", views.request_otp, name="request_otp"),
    path("verify/", views.verify_otp, name="verify_otp"),
]
