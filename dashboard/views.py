from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import DailyRoutine, Task, TaskCategory
from .forms import DailyRoutineForm, TaskFormSet
import json
from datetime import date, timedelta
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Avg, Q
from .forms import DailyRoutineForm, TaskFormSet

from django.db.models import Count, Avg, Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import DailyRoutine, Task, TaskCategory
from .forms import DailyRoutineForm, TaskFormSet



@login_required
def routine_create_view(request):
    if request.method == 'POST':
        routine_form = DailyRoutineForm(request.POST)
        task_formset = TaskFormSet(request.POST)
        
        if routine_form.is_valid() and task_formset.is_valid():
            routine = routine_form.save(commit=False)
            routine.user = request.user
            routine.save()
            
            tasks = task_formset.save(commit=False)
            for task in tasks:
                task.routine = routine
                task.save()
            
            messages.success(request, 'Routine created successfully!')
            return redirect('routine_detail', pk=routine.pk)
    else:
        routine_form = DailyRoutineForm()
        task_formset = TaskFormSet(queryset=Task.objects.none())
    
    return render(request, 'dashboard/routine_edit.html', {
        'routine_form': routine_form,
        'task_formset': task_formset,
        'title': 'Create Routine'
    })

@login_required
def routine_edit_view(request, pk):
    routine = get_object_or_404(DailyRoutine, pk=pk, user=request.user)
    
    if request.method == 'POST':
        routine_form = DailyRoutineForm(request.POST, instance=routine)
        task_formset = TaskFormSet(request.POST, queryset=routine.tasks.all())
        
        if routine_form.is_valid() and task_formset.is_valid():
            routine_form.save()
            tasks = task_formset.save(commit=False)
            for task in tasks:
                task.routine = routine
                task.save()
            
            messages.success(request, 'Routine updated successfully!')
            return redirect('routine_detail', pk=routine.pk)
    else:
        routine_form = DailyRoutineForm(instance=routine)
        task_formset = TaskFormSet(queryset=routine.tasks.all())
    
    return render(request, 'dashboard/routine_edit.html', {
        'routine_form': routine_form,
        'task_formset': task_formset,
        'title': 'Edit Routine'
    })

@login_required
def routine_delete_view(request, pk):
    routine = get_object_or_404(DailyRoutine, pk=pk, user=request.user)
    
    if request.method == 'POST':
        routine.delete()
        messages.success(request, 'Routine deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'dashboard/routine_confirm_delete.html', {'routine': routine})

@login_required
def export_email_view(request):
    # Implement email export logic here
    messages.info(request, 'Email export feature coming soon!')
    return redirect('dashboard')

@login_required
def export_pdf_view(request):
    # Implement PDF export logic here
    messages.info(request, 'PDF export feature coming soon!')
    return redirect('dashboard')


@login_required
def dashboard_view(request):
    today = timezone.now().date()
    
    # Get or create today's routine
    routine, created = DailyRoutine.objects.get_or_create(
        user=request.user,
        date=today,
        defaults={'notes': ''}
    )
    
    # Get statistics
    total_routines = DailyRoutine.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(routine__user=request.user, is_completed=True).count()
    total_tasks = Task.objects.filter(routine__user=request.user).count()
    
    # Get recent routines
    recent_routines = DailyRoutine.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Weekly progress - FIXED: Calculate manually instead of querying property
    week_ago = today - timedelta(days=7)
    weekly_routines = DailyRoutine.objects.filter(
        user=request.user,
        date__gte=week_ago
    ).prefetch_related('tasks')
    
    # Calculate completion percentage for each routine
    weekly_progress = []
    for routine_item in weekly_routines:
        tasks = routine_item.tasks.all()
        if tasks:
            completed = tasks.filter(is_completed=True).count()
            percentage = int((completed / tasks.count()) * 100)
        else:
            percentage = 0
        weekly_progress.append({
            'date': routine_item.date,
            'completion_percentage': percentage
        })
    
    context = {
        'routine': routine,
        'today': today,
        'total_routines': total_routines,
        'completed_tasks': completed_tasks,
        'total_tasks': total_tasks,
        'recent_routines': recent_routines,
        'weekly_progress': weekly_progress,
        'categories': TaskCategory.objects.all(),
    }
    
    return render(request, 'dashboard/index.html', context)
@login_required
def routine_detail_view(request, pk):
    routine = get_object_or_404(DailyRoutine, pk=pk, user=request.user)
    tasks = routine.tasks.all()
    
    return render(request, 'dashboard/routine_detail.html', {
        'routine': routine,
        'tasks': tasks
    })

@login_required
def history_view(request):
    routines = DailyRoutine.objects.filter(user=request.user).order_by('-date')
    
    # Filter by date if provided
    date_filter = request.GET.get('date')
    if date_filter:
        routines = routines.filter(date=date_filter)
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(routines, 10)
    
    try:
        routines_page = paginator.page(page)
    except PageNotAnInteger:
        routines_page = paginator.page(1)
    except EmptyPage:
        routines_page = paginator.page(paginator.num_pages)
    
    return render(request, 'dashboard/history.html', {
        'routines': routines_page,
        'date_filter': date_filter
    })

@login_required
def statistics_view(request):
    routines = DailyRoutine.objects.filter(user=request.user).prefetch_related('tasks')
    
    # Calculate statistics
    total_days = routines.count()
    total_tasks = Task.objects.filter(routine__user=request.user).count()
    completed_tasks = Task.objects.filter(routine__user=request.user, is_completed=True).count()
    
    # Calculate average completion manually
    total_percentage = 0
    count = 0
    best_day = None
    best_percentage = -1
    
    for routine in routines:
        tasks = routine.tasks.all()
        if tasks:
            completed = tasks.filter(is_completed=True).count()
            percentage = int((completed / tasks.count()) * 100)
            total_percentage += percentage
            count += 1
            
            # Track best day
            if percentage > best_percentage:
                best_percentage = percentage
                best_day = routine
    
    avg_completion = total_percentage / count if count > 0 else 0
    
    # Category breakdown
    categories = TaskCategory.objects.annotate(
        task_count=Count('task', filter=Q(task__routine__user=request.user)),
        completed_count=Count('task', filter=Q(task__routine__user=request.user, task__is_completed=True))
    )
    
    context = {
        'total_days': total_days,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'avg_completion': round(avg_completion, 1),
        'best_day': best_day,
        'categories': categories,
    }
    
    return render(request, 'dashboard/statistics.html', context)
# API Views for AJAX
@login_required
def toggle_task_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        
        try:
            task = Task.objects.get(id=task_id, routine__user=request.user)
            task.is_completed = not task.is_completed
            task.save()
            
            # Update routine completion
            routine = task.routine
            completion = routine.completion_percentage
            
            return JsonResponse({
                'success': True,
                'task_completed': task.is_completed,
                'completion_percentage': completion
            })
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})