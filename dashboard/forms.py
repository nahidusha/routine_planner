from django import forms
from django.forms import modelformset_factory
from .models import DailyRoutine, Task, TaskCategory

class DailyRoutineForm(forms.ModelForm):
    class Meta:
        model = DailyRoutine
        fields = ['date', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['time', 'description', 'category', 'is_ibadah', 'order']
        widgets = {
            'time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 08:00 AM'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'is_ibadah': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

TaskFormSet = modelformset_factory(Task, form=TaskForm, extra=1, can_delete=True)