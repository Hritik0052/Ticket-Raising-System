from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("superadmin/dashboard/", views.superadmin_dashboard, name="superadmin_dashboard"),
    path("superadmin/create-department/", views.create_department, name="create_department"),
    path("superadmin/create-staff/", views.create_staff, name="create_staff"),
    path('superadmin/create-subdepartment/', views.create_subdepartment, name='create_subdepartment'),
    path('get-subdepartments/<int:dept_id>/', views.get_subdepartments, name='get_subdepartments'),
    path("logout/", views.user_logout, name="logout"),
    path("superadmin/view_all_staff", views.view_all_staff, name='view_all_staff'),
    path("superadmin/view_all_tickets", views.view_all_tickets, name='view_all_tickets'),
    path("superadmin/view_all_departments", views.view_all_departments, name='view_all_departments')
]
