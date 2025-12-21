from django.contrib import admin
from .models import DailyRoutine, Task, TaskCategory

@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']

@admin.register(DailyRoutine)
class DailyRoutineAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'completion_percentage', 'created_at']
    list_filter = ['date', 'user']
    search_fields = ['user__username', 'notes']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['time', 'description', 'routine', 'is_completed', 'is_ibadah']
    list_filter = ['is_completed', 'is_ibadah', 'category']
    search_fields = ['description']
    list_editable = ['is_completed']