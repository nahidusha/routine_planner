from django.db import models
from django.conf import settings
from django.utils import timezone

class TaskCategory(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#0F766E')  # Hex color
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Task Categories"

class DailyRoutine(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.username}'s Routine - {self.date}"
    
    @property
    def completion_percentage(self):
        tasks = self.tasks.all()
        if not tasks:
            return 0
        completed = tasks.filter(is_completed=True).count()
        return int((completed / tasks.count()) * 100)

class Task(models.Model):
    routine = models.ForeignKey(DailyRoutine, on_delete=models.CASCADE, related_name='tasks')
    time = models.CharField(max_length=20)
    description = models.CharField(max_length=200)
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    is_ibadah = models.BooleanField(default=False)  # For Salah tasks
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.time} - {self.description[:50]}"


class DefaultTask(models.Model):
    """User-specific default tasks that can be applied to each day's routine."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time = models.CharField(max_length=20, blank=True)
    description = models.CharField(max_length=200)
    is_ibadah = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Default: {self.description[:50]}"