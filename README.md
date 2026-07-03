# Employee-Management-System
A full-stack Employee Management System built with Django, SQLite, Bootstrap 5, and custom CSS. Features secure authentication, employee CRUD operations, search functionality, admin dashboard, responsive UI, and deployment support using Gunicorn, WhiteNoise, and Render.

# Employee Management System — Build From Scratch in VS Code
**Stack:** Django + SQLite + Bootstrap 5
**Features:** Login system, Add / Update / Delete / Search Employee, Admin Dashboard

---

## Step 0: Prerequisites

Install these before starting:
- Python 3.10+ → `python --version`
- VS Code with the **Python** extension installed

No database server to install — SQLite ships with Python/Django and just creates a local `db.sqlite3` file.

---

## Step 1: Project Folder & Virtual Environment

Open VS Code → Terminal → New Terminal, then:

```bash
mkdir employee-management-system
cd employee-management-system
python -m venv venv
```

Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

VS Code will likely prompt "Select Interpreter" — choose the one inside `venv`.

---

## Step 2: Install Dependencies

```bash
pip install django django-crispy-forms crispy-bootstrap5
pip freeze > requirements.txt
```

---

## Step 3: Create the Django Project & App

```bash
django-admin startproject myproject .
python manage.py startapp employee
```

Your folder now looks like:
```
employee-management-system/
├── manage.py
├── requirements.txt
├── myproject/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
└── employee/
    ├── models.py
    ├── views.py
    ├── admin.py
```

---

## Step 4: Database

Nothing to create manually — SQLite is file-based. Django's default project already points to it:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
Leave this exactly as `django-admin startproject` generated it. The `db.sqlite3` file will be created automatically the first time you run migrations in Step 6.

---

## Step 5: Configure `settings.py`

Open `myproject/settings.py` and edit:

**5a. Register the app + crispy forms**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'employee',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
```

**5b. Login redirect settings — add anywhere at the bottom**
```python
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
```

**5d. Static files — confirm this exists**
```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

---

## Step 6: Build the Employee Model

`employee/models.py`
```python
from django.db import models

class Employee(models.Model):
    DEPARTMENT_CHOICES = [
        ('HR', 'Human Resources'),
        ('IT', 'Information Technology'),
        ('Finance', 'Finance'),
        ('Sales', 'Sales'),
        ('Marketing', 'Marketing'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='IT')
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    date_joined = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-date_joined']
```

Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Step 7: Register Model in Admin (Admin Dashboard)

`employee/admin.py`
```python
from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'department', 'salary', 'date_joined')
    search_fields = ('name', 'email', 'department')
    list_filter = ('department',)
```

Create a superuser (for `/admin/` login):
```bash
python manage.py createsuperuser
```

---

## Step 8: Create the Employee Form

Create `employee/forms.py`:
```python
from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'email', 'department', 'salary']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control'}),
        }
```

---

## Step 9: Build the Views (Login + CRUD + Search)

`employee/views.py`
```python
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
```

---

## Step 10: URL Routing

`employee/urls.py` (new file):
```python
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_update, name='employee_update'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
]
```

`myproject/urls.py` — replace with:
```python
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='login/', permanent=False)),
    path('', include('employee.urls')),
]
```

---

## Step 11: Templates

Create folders: `employee/templates/employee/`

**`base.html`**
```html
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <title>Employee Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% if user.is_authenticated %}
    <nav class="navbar navbar-dark bg-dark px-3">
        <a class="navbar-brand" href="{% url 'dashboard' %}">Employee MS</a>
        <div>
            <a class="btn btn-outline-light btn-sm" href="{% url 'employee_list' %}">Employees</a>
            <a class="btn btn-outline-light btn-sm" href="/admin/">Admin</a>
            <a class="btn btn-danger btn-sm" href="{% url 'logout' %}">Logout</a>
        </div>
    </nav>
    {% endif %}

    <div class="container mt-4">
        {% for message in messages %}
        <div class="alert alert-info">{{ message }}</div>
        {% endfor %}
        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

**`login.html`**
```html
{% extends 'employee/base.html' %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-md-4">
    <h3 class="mb-3">Login</h3>
    <form method="POST">
      {% csrf_token %}
      <div class="mb-3">
        <label>Username</label>
        <input type="text" name="username" class="form-control" required>
      </div>
      <div class="mb-3">
        <label>Password</label>
        <input type="password" name="password" class="form-control" required>
      </div>
      <button type="submit" class="btn btn-primary w-100">Login</button>
    </form>
  </div>
</div>
{% endblock %}
```

**`dashboard.html`**
```html
{% extends 'employee/base.html' %}
{% block content %}
<h2>Welcome, {{ user.username }}</h2>
<div class="card p-3 mt-3" style="max-width: 300px;">
    <h5>Total Employees</h5>
    <h1>{{ total_employees }}</h1>
</div>
<a href="{% url 'employee_list' %}" class="btn btn-primary mt-3">View All Employees</a>
{% endblock %}
```

**`employee_list.html`**
```html
{% extends 'employee/base.html' %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
    <h2>Employees</h2>
    <a href="{% url 'employee_create' %}" class="btn btn-success">+ Add Employee</a>
</div>

<form method="GET" class="mb-3 d-flex">
    <input type="text" name="search" value="{{ query }}" class="form-control me-2" placeholder="Search by name/department/email">
    <button class="btn btn-outline-primary">Search</button>
</form>

<table class="table table-bordered table-hover">
    <thead class="table-dark">
        <tr><th>Name</th><th>Email</th><th>Department</th><th>Salary</th><th>Actions</th></tr>
    </thead>
    <tbody>
        {% for emp in employees %}
        <tr>
            <td>{{ emp.name }}</td>
            <td>{{ emp.email }}</td>
            <td>{{ emp.department }}</td>
            <td>{{ emp.salary }}</td>
            <td>
                <a href="{% url 'employee_update' emp.pk %}" class="btn btn-sm btn-warning">Edit</a>
                <a href="{% url 'employee_delete' emp.pk %}" class="btn btn-sm btn-danger">Delete</a>
            </td>
        </tr>
        {% empty %}
        <tr><td colspan="5" class="text-center">No employees found.</td></tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

**`employee_form.html`**
```html
{% extends 'employee/base.html' %}
{% block content %}
<h2>{{ action }} Employee</h2>
<form method="POST">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-primary">{{ action }}</button>
    <a href="{% url 'employee_list' %}" class="btn btn-secondary">Cancel</a>
</form>
{% endblock %}
```

**`employee_confirm_delete.html`**
```html
{% extends 'employee/base.html' %}
{% block content %}
<h2>Delete Employee</h2>
<p>Are you sure you want to delete <strong>{{ employee.name }}</strong>?</p>
<form method="POST">
    {% csrf_token %}
    <button type="submit" class="btn btn-danger">Yes, Delete</button>
    <a href="{% url 'employee_list' %}" class="btn btn-secondary">Cancel</a>
</form>
{% endblock %}
```

---

## Step 12: Run the Server

```bash
python manage.py runserver
```

Test these URLs:
| URL | Purpose |
|---|---|
| `http://127.0.0.1:8000/login/` | User login |
| `http://127.0.0.1:8000/dashboard/` | Dashboard (after login) |
| `http://127.0.0.1:8000/employees/` | List + Search |
| `http://127.0.0.1:8000/employees/add/` | Add employee |
| `http://127.0.0.1:8000/admin/` | Admin dashboard (superuser login) |

For the `/login/` page, since you haven't created a regular user yet, either:
- Use your superuser credentials (works for both `/login/` and `/admin/`), or
- Create a normal user via `/admin/` → Users → Add.

---

## Step 13: Prepare for Deployment — `requirements.txt`

Install the two extra production packages, then regenerate `requirements.txt`:
```bash
pip install gunicorn whitenoise
pip freeze > requirements.txt
```

Your `requirements.txt` should now look like this:
```
Django>=5.0
django-crispy-forms>=2.1
crispy-bootstrap5>=2024.2
gunicorn>=21.2.0
whitenoise>=6.6.0
```
(exact version numbers will vary — that's fine, `pip freeze` fills them in for you)

---

## Step 14: Update `settings.py` for Production

Add WhiteNoise to serve static files, and read the secret key/debug flag from environment variables:

**14a. Middleware — add WhiteNoise right after SecurityMiddleware**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # add this line
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

**14b. Static files config — add below `STATIC_URL`**
```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**14c. Allowed hosts + CSRF trust for Render's domain**
```python
import os

DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-fallback-key-change-me')
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.onrender.com']
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']
```

---

## Step 15: Create `render.yaml`

In the project root (same level as `manage.py`), create `render.yaml`:
```yaml
services:
  - type: web
    name: employee-management-system
    runtime: python
    buildCommand: "pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate"
    startCommand: "gunicorn myproject.wsgi:application"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: "False"
      - key: WEB_CONCURRENCY
        value: 2
```

This tells Render: install dependencies → collect static files → run migrations → start the app with Gunicorn (pointing at your `wsgi.py`, which is exactly what that file is for).

> Note: `migrate` runs on every deploy, which recreates tables in the fresh SQLite file each time Render's filesystem resets — your schema comes back, but any data added after the last deploy is lost. That's the tradeoff of SQLite on Render's free tier.

---

## Step 16: `.gitignore` and Push to GitHub

Create `.gitignore` in the project root:
```
venv/
__pycache__/
*.pyc
db.sqlite3
staticfiles/
.env
```

`db.sqlite3` is excluded on purpose — it's generated fresh by `migrate` on every deploy, so there's no need to commit your local data/schema file.

```bash
git init
git add .
git commit -m "Employee Management System - initial build"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

---

## Step 17: Deploy on Render

1. Go to [render.com](https://render.com) → **New** → **Blueprint** (this reads your `render.yaml` automatically) → connect your GitHub repo.
2. Render detects `render.yaml`, provisions the web service, and auto-generates `SECRET_KEY` for you.
3. Once deployed, create your admin user via Render's **Shell** tab:
   ```bash
   python manage.py createsuperuser
   ```
   (You'll need to redo this after every redeploy, for the same ephemeral-filesystem reason above.)
4. Visit `https://<your-app-name>.onrender.com/login/`.
