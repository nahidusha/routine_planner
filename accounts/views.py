from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from dashboard.models import Task
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_POST
import json

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # create inactive user pending admin approval
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # notify site admins if configured
            try:
                admin_emails = [a[1] for a in getattr(settings, 'ADMINS', [])]
                if admin_emails:
                    send_mail(
                        'New user awaiting approval',
                        f'User {user.username} ({user.email}) has signed up and requires approval.',
                        getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                        admin_emails,
                        fail_silently=True
                    )
            except Exception:
                pass

            messages.info(request, 'Account created. Waiting for admin approval.')
            return redirect('waiting_approval')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


def waiting_approval_view(request):
    return render(request, 'accounts/waiting_approval.html')

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


@login_required
def pending_users_view(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    from .models import CustomUser
    pending = CustomUser.objects.filter(is_active=False).order_by('-created_at')
    return render(request, 'accounts/admin_pending.html', {'pending': pending})


@login_required
def approve_user_view(request, user_id):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'not allowed'}, status=403)
    from .models import CustomUser
    user = get_object_or_404(CustomUser, pk=user_id)
    user.is_active = True
    user.save()
    # notify the user by email if available
    try:
        send_mail('Your account was approved', 'Your account has been approved by admin. You can now log in.', getattr(settings, 'DEFAULT_FROM_EMAIL', None), [user.email], fail_silently=True)
    except Exception:
        pass
    return JsonResponse({'success': True})


@login_required
@require_POST
def reset_user_password_view(request):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'not allowed'}, status=403)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    user_id = data.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'error': 'user_id required'}, status=400)
    from .models import CustomUser
    user = get_object_or_404(CustomUser, pk=user_id)
    # generate a temporary password and set it
    temp = get_random_string(12)
    user.set_password(temp)
    user.save()
    # try to email the user if possible
    try:
        send_mail('Your password was reset by admin', f'Your new temporary password is: {temp}', getattr(settings, 'DEFAULT_FROM_EMAIL', None), [user.email], fail_silently=True)
        emailed = True
    except Exception:
        emailed = False
    # Return the temporary password (one-time) so admin can copy it if email fails
    return JsonResponse({'success': True, 'temp_password': temp, 'emailed': emailed})


@login_required
@require_POST
def delete_user_view(request):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'not allowed'}, status=403)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    user_id = data.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'error': 'user_id required'}, status=400)
    from .models import CustomUser
    user = get_object_or_404(CustomUser, pk=user_id)
    # Prevent deleting superusers or self
    if user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Cannot delete superuser'}, status=403)
    if user.pk == request.user.pk:
        return JsonResponse({'success': False, 'error': 'Cannot delete yourself'}, status=403)
    # Delete user - related objects with on_delete=CASCADE will be removed
    try:
        user.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)