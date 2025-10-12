from django.shortcuts import render
from django.contrib.auth import logout

def main_page(request):
    logout(request)
    return render(request,'main.html')