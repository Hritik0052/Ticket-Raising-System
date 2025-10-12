from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from accounts.models import User
from departments.models import Department, SubDepartment
from tickets.models import Ticket
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse


def home(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.role == "superadmin":
                return redirect("superadmin_dashboard")  # accounts/urls.py
            elif user.role == "staff_l1":
                return redirect("tickets:l1_dashboard")  # tickets/urls.py
            elif user.role == "staff_l2":
                return redirect("tickets:l2_dashboard")  # tickets/urls.py
            else:
                messages.error(request, "Role not recognized!")
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, "accounts/login.html")

# =================== Role-based Decorator =======================
def role_required(allowed_roles):
    """Decorator to restrict view access based on user roles"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("admin:login")
            if request.user.role not in allowed_roles:
                return redirect("home")  # redirect to homepage if role not allowed
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# =================== SuperAdmin Views ===========================

@login_required
@role_required(["superadmin"])
def superadmin_dashboard(request):
    """Dashboard for SuperAdmin to view tickets, departments, staff"""
    tickets = Ticket.objects.all().order_by("-created_at")
    departments = Department.objects.all()
    staff_members = User.objects.filter(role__in=["staff_l1", "staff_l2"])
    # Resolved tickets counts 
    resolved_tickets_count = Ticket.objects.filter(status="closed").count()
    return render(request, "accounts/superadmin_dashboard.html", {
        "tickets": tickets,
        "departments": departments,
        "staff_members": staff_members,
        "resolved_tickets_count":resolved_tickets_count
    })


@login_required
@role_required(["superadmin"])
def create_department(request):
    """Create a new department"""
    if request.method == "POST":
        name = request.POST.get("name")
        Department.objects.create(name=name)
        return redirect("superadmin_dashboard")
    return render(request, "accounts/create_department.html")


@login_required
@role_required(["superadmin"])
def create_staff(request):
    """Create a new staff member (L1 or L2) and assign to department"""
    departments = Department.objects.all()
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        password = request.POST.get("password")
        role = request.POST.get("role")
        email= request.POST.get("email")
        mobile = request.POST.get("mobile")
        date_joined = request.POST.get("date_joined")
        department_id = request.POST.get("department")
        department = Department.objects.get(id=department_id)

        User.objects.create(
            username=username,
            password=make_password(password),
            role=role,
            department=department,
            email=email,
            first_name=first_name,
            last_name=last_name,
            mobile=mobile,
            date_joined=date_joined
        )
        return redirect("superadmin_dashboard")

    return render(request, "accounts/create_staff.html", {"departments": departments})


# ===================== Create sub-department ====================
@login_required
@role_required(["superadmin"])
def create_subdepartment(request):
    if request.method == "POST":
        name = request.POST.get("name")
        department_id = request.POST.get("department")
        department = Department.objects.get(id=department_id)
        SubDepartment.objects.create(name=name, department=department)
        messages.success(request, "Sub-department created successfully")
        return redirect("superadmin_dashboard")

    departments = Department.objects.all()
    return render(request, "accounts/create_subdepartment.html", {"departments": departments})


# =================== Extra Methods (Optional) ===================
# Add here any future utility methods for accounts app

@login_required
@role_required(['superadmin'])
def view_all_staff(request):
    all_staff = User.objects.filter(role__in=["staff_l1", "staff_l2"])
    return render(request, "accounts/view_all_staff.html", {"all_staff":all_staff})

@login_required
@role_required(["superadmin"])
def view_staff_member(request, staff_id):
    """View details of a single staff member"""
    all_staff = User.objects.get(id=staff_id, role__in=["staff_l1", "staff_l2"])
    return render(request, "accounts/view_staff.html", {"all_staff": all_staff})

# =================== LogOut method =============================
def user_logout(request):
    logout(request)
    return redirect("main_page")  # redirect to main landing page



def get_subdepartments(request, dept_id):
    try:
        department = Department.objects.get(id=dept_id)
        sub_departments = department.subdepartments.all().values("id", "name")
        return JsonResponse({"sub_departments": list(sub_departments)})
    except Department.DoesNotExist:
        return JsonResponse({"sub_departments": []})

@login_required
@role_required(['superadmin'])
def view_all_tickets(tickets):
    all_tickets = Ticket.objects.all()
    return render(request, "accounts/all_tickets.html", {"all_tickets":all_tickets})

@login_required
@role_required(['superadmin'])
def view_all_departments(request):
    all_departments = Department.objects.all()
    return render(request, "accounts/all_departments.html", {"all_departments":all_departments})