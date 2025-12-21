from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from dashboard.models import Task

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user

    # Compute simple stats to avoid complex template expressions
    total_routines = user.dailyroutine_set.count()
    total_tasks = Task.objects.filter(routine__user=user).count()
    completed_tasks = Task.objects.filter(routine__user=user, is_completed=True).count()

    if request.method == 'POST':
        # Minimal profile update: first_name, last_name, email
        first = request.POST.get('first_name', '')
        last = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        user.first_name = first
        user.last_name = last
        user.email = email
        # optional fields
        if 'phone' in request.POST:
            try:
                user.phone = request.POST.get('phone')
            except Exception:
                pass
        user.save()
        messages.success(request, 'Profile updated')
        return redirect('profile')

    return render(request, 'accounts/profile.html', {
        'user': user,
        'total_routines': total_routines,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
    })