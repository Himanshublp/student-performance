from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Authentication
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),

    # Marksheet & Reports
    path('upload_marksheet/', views.upload_marksheet, name='upload_marksheet'),
    path('upload-pdf/', views.upload_pdf, name='upload_pdf'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('view_full_report/', views.view_full_report, name='view_full_report'),
    path('progress_report/', views.progress_report, name='progress_report'),

    # Add Data
    path('add_certificate/', views.add_certificate, name='add_certificate'),
    path('add_project/', views.add_project, name='add_project'),
    path('add_competitive_exam/', views.add_competitive_exam, name='add_competitive_exam'),

    # Other
    path('guided_plan/', views.guided_plan, name='guided_plan'),
    path('chat/', views.chatbot_ui, name='chat_ui'),
    path('api/chat/', views.ai_chat_api, name='ai_chat_api'),

    # APIs
    path('api/get-user-data/', views.get_user_data, name='get_user_data'),
    path('api/get-certificates/', views.get_certificates, name='get_certificates'),
    path('api/get-projects/', views.get_projects, name='get_projects'),
    path('api/get-exams/', views.get_exams, name='get_exams'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)