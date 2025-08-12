from django.urls import path
from . import views

from .views import ai_chat_api, chatbot_ui
urlpatterns = [
    # Login URL
    path('login/', views.user_login, name='login'),

    # Registration URL
    path('register/', views.register, name='register'),

    # Dashboard URL (only accessible after login)
    path('dashboard/', views.dashboard, name='dashboard'),

    # Logout URL
    path('logout/', views.user_logout, name='logout'),

    # Progress report URL
    path('progress_report/', views.progress_report, name='progress_report'),

    # Marksheet upload URL
    path('upload_marksheet/', views.upload_marksheet, name='upload_marksheet'),

    # Full report URL
    path('view_full_report/', views.view_full_report, name='view_full_report'),

    # Example CSV report generation
    path('generate_report/', views.generate_report, name='generate_report'),

    # Home URL - if the user is not logged in, it redirects to login
    path('', views.home, name='home'),
    path('add_certificate/', views.add_certificate, name='add_certificate'),
    path('add_project/', views.add_project, name='add_project'),
    path('add_competitive_exam/', views.add_competitive_exam, name='add_competitive_exam'),
    path('upload-pdf/', views.upload_pdf, name='upload_pdf'),
    path('guided_plan/', views.guided_plan, name='guided_plan'),
    path('chat/', chatbot_ui, name='chat-ui'),
    path('api/chat/', ai_chat_api, name='ai-chat-api'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    
]