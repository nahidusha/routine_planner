from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('waiting-approval/', views.waiting_approval_view, name='waiting_approval'),
    path('pending/', views.pending_users_view, name='pending_users'),
    path('pending/approve/<int:user_id>/', views.approve_user_view, name='approve_user'),
    path('admin/reset-password/', views.reset_user_password_view, name='reset_user_password'),
    path('admin/delete-user/', views.delete_user_view, name='delete_user'),
]