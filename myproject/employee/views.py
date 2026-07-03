# from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Employee
from .forms import EmployeeForm


# ---------- Authentication ----------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'employee/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# ---------- Dashboard ----------
@login_required
def dashboard(request):
    total_employees = Employee.objects.count()
    return render(request, 'employee/dashboard.html', {'total_employees': total_employees})


# ---------- Read + Search ----------
@login_required
def employee_list(request):
    query = request.GET.get('search', '')
    if query:
        employees = Employee.objects.filter(name__icontains=query) | \
                    Employee.objects.filter(department__icontains=query) | \
                    Employee.objects.filter(email__icontains=query)
    else:
        employees = Employee.objects.all()
    return render(request, 'employee/employee_list.html', {
        'employees': employees,
        'query': query,
    })


# ---------- Create ----------
@login_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee added successfully!')
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employee/employee_form.html', {'form': form, 'action': 'Add'})


# ---------- Update ----------
@login_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully!')
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employee/employee_form.html', {'form': form, 'action': 'Update'})


# ---------- Delete ----------
@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully!')
        return redirect('employee_list')
    return render(request, 'employee/employee_confirm_delete.html', {'employee': employee})