from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import OTP
from .utils import generate_otp, send_otp_email
from django.utils.timezone import now, timedelta

def request_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        code = generate_otp(email)
        send_otp_email(email, code)
        request.session["pending_email"] = email 
        return redirect("verify_otp")            
    return render(request, "notifications/request_otp.html")

def verify_otp(request):
    if request.method == "POST":
        email = request.session.get("pending_email")
        code = request.POST.get("otp")

        otp_record = OTP.objects.filter(email=email, code=code, is_used=False).last()
        if otp_record and otp_record.created_at >= now() - timedelta(minutes=2):
            otp_record.is_used = True
            otp_record.save()
            request.session["verified_email"] = email 
            del request.session["pending_email"]    
            return redirect("tickets:raise_ticket")         
        return render(request, "notifications/verify_otp.html", {"error": "Invalid or expired OTP"})
    return render(request, "notifications/verify_otp.html")
