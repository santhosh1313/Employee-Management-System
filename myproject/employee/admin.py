# from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'department', 'salary', 'date_joined')
    search_fields = ('name', 'email', 'department')
    list_filter = ('department',)
