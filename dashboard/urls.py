from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('planner/', views.planner_view, name='planner'),
    path('routine/<int:pk>/', views.routine_detail_view, name='routine_detail'),
    path('routine/create/', views.routine_create_view, name='routine_create'),
    path('routine/<int:pk>/edit/', views.routine_edit_view, name='routine_edit'),
    path('routine/<int:pk>/delete/', views.routine_delete_view, name='routine_delete'),
    path('history/', views.history_view, name='history'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('toggle_task/', views.toggle_task_view, name='toggle_task'),
    path('create_task/', views.create_task_view, name='create_task'),
    path('export/email/', views.export_email_view, name='export_email'),
    path('export/pdf/', views.export_pdf_view, name='export_pdf'),
    path('send_report/', views.send_report_view, name='send_report'),
]