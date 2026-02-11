from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.models import User

import json
import csv
import os
import base64
from io import BytesIO, StringIO
import datetime
import random

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from .models import (
    Marksheet, ExamType, Performance, Semester, Subject,
    Certificate, Project, CompetitiveExam, Document
)
from .forms import CertificateForm, ProjectForm, CompetitiveExamForm, MarksheetUploadForm

# Home view
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

# Registration view
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email', '')

        if password1 != password2:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Passwords do not match!'}, status=400)
            messages.error(request, 'Passwords do not match!')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Username already exists!'}, status=400)
            messages.error(request, 'Username already exists!')
            return render(request, 'register.html')

        user = User.objects.create_user(username=username, password=password1, email=email)
        user.save()
        
        # Create dummy data for new user
        create_dummy_data(user)

        messages.success(request, 'Registration successful! You can now log in.')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Registration successful!',
                'user': {'username': username, 'email': email}
            })

        return redirect('login')

    form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def create_dummy_data(user):
    """Create dummy data for new users to see demo content"""
    
    # Create dummy certificates
    certificates = [
        {'name': 'Python for Data Science', 'issued_by': 'Coursera', 'date_issued': datetime.date.today() - datetime.timedelta(days=30)},
        {'name': 'Web Development Bootcamp', 'issued_by': 'Udemy', 'date_issued': datetime.date.today() - datetime.timedelta(days=60)},
        {'name': 'Machine Learning Basics', 'issued_by': 'Stanford Online', 'date_issued': datetime.date.today() - datetime.timedelta(days=15)},
    ]
    
    for cert_data in certificates:
        Certificate.objects.create(
            user=user,
            name=cert_data['name'],
            issued_by=cert_data['issued_by'],
            date_issued=cert_data['date_issued']
        )
    
    # Create dummy projects
    projects = [
        {'title': 'E-Commerce Website', 'description': 'Full-stack e-commerce platform with React and Django', 
         'date_started': datetime.date.today() - datetime.timedelta(days=90), 'date_completed': datetime.date.today() - datetime.timedelta(days=10)},
        {'title': 'Chat Application', 'description': 'Real-time chat app with WebSockets and React', 
         'date_started': datetime.date.today() - datetime.timedelta(days=45), 'date_completed': datetime.date.today() - datetime.timedelta(days=5)},
    ]
    
    for proj_data in projects:
        Project.objects.create(
            user=user,
            title=proj_data['title'],
            description=proj_data['description'],
            date_started=proj_data['date_started'],
            date_completed=proj_data['date_completed']
        )
    
    # Create dummy competitive exams
    exams = [
        {'exam_name': 'JEE Main', 'score': 'AIR 4521', 'date_taken': datetime.date.today() - datetime.timedelta(days=200)},
        {'exam_name': 'GATE CS', 'score': 'AIR 234', 'date_taken': datetime.date.today() - datetime.timedelta(days=100)},
        {'exam_name': 'CAT', 'score': '98.5%', 'date_taken': datetime.date.today() - datetime.timedelta(days=150)},
    ]
    
    for exam_data in exams:
        CompetitiveExam.objects.create(
            user=user,
            exam_name=exam_data['exam_name'],
            score=exam_data['score'],
            date_taken=exam_data['date_taken']
        )
    
    # Create dummy semester data
    semester_names = ['1st Semester', '2nd Semester', '3rd Semester', '4th Semester']
    sgpa_values = [8.2, 8.5, 8.7, 9.0]
    
    for i, (sem_name, sgpa) in enumerate(zip(semester_names, sgpa_values)):
        semester = Semester.objects.create(
            semester_number=i+1,
            sgpa=sgpa,
            total_marks=random.randint(450, 500),
            result_status='PASS'
        )
        
        # Create subjects for each semester
        subjects = [
            {'code': 'CS101', 'name': 'Programming Fundamentals', 'internal': 28, 'external': 65, 'grade': 'A'},
            {'code': 'CS201', 'name': 'Data Structures', 'internal': 27, 'external': 68, 'grade': 'A'},
            {'code': 'CS301', 'name': 'Database Systems', 'internal': 26, 'external': 70, 'grade': 'A+'},
            {'code': 'MA101', 'name': 'Engineering Mathematics', 'internal': 25, 'external': 62, 'grade': 'B+'},
        ]
        
        for subj_data in subjects:
            Subject.objects.create(
                semester=semester,
                code=subj_data['code'],
                name=subj_data['name'],
                internal_marks=subj_data['internal'],
                external_marks=subj_data['external'],
                grade=subj_data['grade']
            )
            
            # Create performance record
            exam_type, _ = ExamType.objects.get_or_create(name=subj_data['name'])
            Performance.objects.create(
                user=user,
                exam_type=exam_type,
                score=subj_data['internal'] + subj_data['external'],
                semester=f"Semester {i+1}",
                date=datetime.date.today() - datetime.timedelta(days=(4-i)*30)
            )

# Login view
def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # Check if user has data, if not create dummy data
            if not Certificate.objects.filter(user=user).exists():
                create_dummy_data(user)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Login successful!',
                    'redirect': '/dashboard/',
                    'user': {'username': user.username, 'email': user.email}
                })

            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Invalid credentials!'}, status=400)

    return render(request, 'login.html')

# Logout view
def user_logout(request):
    logout(request)
    return redirect('login')

# Get user data API
@login_required
def get_user_data(request):
    return JsonResponse({
        'success': True,
        'user': {
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'date_joined': request.user.date_joined.strftime('%Y-%m-%d')
        }
    })

# Dashboard view
@login_required
def dashboard(request):
    semesters = Semester.objects.all().order_by('semester_number')
    performance_data = []

    for sem in semesters:
        subjects = sem.subjects.all()
        weak_subjects = [sub.name for sub in subjects if sub.grade in ('C', 'D', 'E', 'F')]

        performance_data.append({
            'semester': sem.semester_number,
            'sgpa': sem.sgpa,
            'total_marks': sem.total_marks,
            'result_status': sem.result_status,
            'weak_subjects': weak_subjects,
        })

    # Generate SGPA trend plot
    if semesters.exists():
        sgpas = [sem.sgpa for sem in semesters]
        semesters_labels = [f"Sem {sem.semester_number}" for sem in semesters]
        
        plt.figure(figsize=(10, 5))
        plt.plot(semesters_labels, sgpas, marker='o', color='#667eea', linewidth=3, markersize=10)
        plt.fill_between(semesters_labels, sgpas, alpha=0.2, color='#667eea')
        plt.title('SGPA Trend Across Semesters', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Semester', fontsize=12)
        plt.ylabel('SGPA', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 10)
        
        for i, (label, sgpa) in enumerate(zip(semesters_labels, sgpas)):
            plt.annotate(f'{sgpa}', (label, sgpa), textcoords="offset points", xytext=(0,10), ha='center', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        buffer.close()
        plt.close()
    else:
        # Create placeholder with dummy data
        plt.figure(figsize=(10, 5))
        dummy_semesters = ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4']
        dummy_sgpas = [8.2, 8.5, 8.7, 9.0]
        
        plt.plot(dummy_semesters, dummy_sgpas, marker='o', color='#667eea', linewidth=3, markersize=10)
        plt.fill_between(dummy_semesters, dummy_sgpas, alpha=0.2, color='#667eea')
        plt.title('Sample SGPA Trend (Upload your marksheet to see real data)', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Semester', fontsize=12)
        plt.ylabel('SGPA', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 10)
        
        for i, (label, sgpa) in enumerate(zip(dummy_semesters, dummy_sgpas)):
            plt.annotate(f'{sgpa}', (label, sgpa), textcoords="offset points", xytext=(0,10), ha='center', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        buffer.close()
        plt.close()
        
        # Add dummy performance data
        performance_data = [
            {'semester': 1, 'sgpa': 8.2, 'total_marks': 468, 'result_status': 'PASS', 'weak_subjects': []},
            {'semester': 2, 'sgpa': 8.5, 'total_marks': 475, 'result_status': 'PASS', 'weak_subjects': []},
            {'semester': 3, 'sgpa': 8.7, 'total_marks': 482, 'result_status': 'PASS', 'weak_subjects': []},
            {'semester': 4, 'sgpa': 9.0, 'total_marks': 490, 'result_status': 'PASS', 'weak_subjects': []},
        ]

    return render(request, 'dashboard.html', {
        'performance_data': performance_data,
        'performance_trend': image_base64,
    })

# Upload marksheet
@login_required
def upload_marksheet(request):
    if request.method == 'POST' and request.FILES.get('marksheet'):
        marksheet_file = request.FILES['marksheet']
        
        # Save file
        marksheet = Marksheet.objects.create(user=request.user, file=marksheet_file)
        
        # Create dummy performance data
        subjects = ['Mathematics', 'Physics', 'Chemistry', 'Computer Science', 'English']
        for i, subject in enumerate(subjects):
            exam_type, _ = ExamType.objects.get_or_create(name=subject)
            Performance.objects.create(
                user=request.user,
                exam_type=exam_type,
                score=random.randint(65, 95),
                semester=f"Semester {random.randint(1, 4)}",
                date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 100))
            )
        
        messages.success(request, "Marksheet uploaded and processed successfully!")
        return render(request, 'upload_success.html')
    
    return render(request, 'upload_marksheet.html')

# Generate report
@login_required
def generate_report(request):
    performances = Performance.objects.filter(user=request.user)
    
    if not performances.exists():
        # Create dummy data for report
        for i in range(5):
            exam_type, _ = ExamType.objects.get_or_create(name=f"Subject {i+1}")
            Performance.objects.create(
                user=request.user,
                exam_type=exam_type,
                score=random.randint(70, 95),
                semester=f"Semester {random.randint(1, 4)}",
                date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 100))
            )
        performances = Performance.objects.filter(user=request.user)

    performance_data = [p.score for p in performances]
    performance_labels = [p.exam_type.name for p in performances[:10]]
    weak_subjects = performances.filter(score__lt=70)[:5]

    context = {
        'performance_data': json.dumps(performance_data[:10]),
        'performance_labels': json.dumps(performance_labels),
        'weak_subjects': weak_subjects,
    }

    return render(request, 'performance_report.html', context)

# View full report
@login_required
def view_full_report(request):
    performances = Performance.objects.filter(user=request.user).order_by('semester')
    
    if not performances.exists():
        # Create dummy data
        for i in range(8):
            exam_type, _ = ExamType.objects.get_or_create(name=f"Subject {i+1}")
            Performance.objects.create(
                user=request.user,
                exam_type=exam_type,
                score=random.randint(65, 95),
                semester=f"Semester {i//2 + 1}",
                date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 200))
            )
        performances = Performance.objects.filter(user=request.user).order_by('semester')
    
    semesters = performances.values_list('semester', flat=True).distinct()
    
    report_data = {}
    for sem in semesters:
        report_data[sem] = performances.filter(semester=sem)

    semester_labels = list(semesters)
    subject_labels = set()
    
    for p in performances:
        subject_labels.add(p.exam_type.name)

    context = {
        'report_data': report_data,
        'semester_labels': json.dumps(semester_labels),
        'subject_labels': json.dumps(list(subject_labels)[:10]),
    }

    return render(request, 'report.html', context)

# Progress report
@login_required
def progress_report(request):
    performance = Performance.objects.filter(user=request.user)
    
    if not performance.exists():
        # Create dummy data
        for i in range(10):
            exam_type, _ = ExamType.objects.get_or_create(name=f"Test {i+1}")
            Performance.objects.create(
                user=request.user,
                exam_type=exam_type,
                score=random.randint(60, 98),
                semester=f"Week {i+1}",
                date=datetime.date.today() - datetime.timedelta(days=(10-i)*7)
            )
        performance = Performance.objects.filter(user=request.user)
    
    return render(request, 'progress_report.html', {'performance': performance})

# Add certificate
@login_required
def add_certificate(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.user = request.user
            certificate.save()
            messages.success(request, "Certificate added successfully!")
            return redirect('student_dashboard')
    else:
        form = CertificateForm()
    return render(request, 'add_certificate.html', {'form': form})

# Add project
@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, "Project added successfully!")
            return redirect('student_dashboard')
    else:
        form = ProjectForm()
    return render(request, 'add_project.html', {'form': form})

# Add competitive exam
@login_required
def add_competitive_exam(request):
    if request.method == 'POST':
        form = CompetitiveExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.user = request.user
            exam.save()
            messages.success(request, "Competitive exam added successfully!")
            return redirect('student_dashboard')
    else:
        form = CompetitiveExamForm()
    return render(request, 'add_competitive_exam.html', {'form': form})

# Upload PDF
@login_required
def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        pdf_file = request.FILES['pdf_file']
        document = Document.objects.create(title=pdf_file.name, pdf_file=pdf_file)
        messages.success(request, "PDF uploaded successfully!")
        return render(request, 'upload_success.html')
    return render(request, 'upload_pdf.html')

# Guided plan
@login_required
def guided_plan(request):
    return render(request, 'guided_plan.html')

# AI Chat API
@csrf_exempt
def ai_chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").lower()
            professional = data.get("professional", "teacher")

            # Enhanced response system
            responses = {
                "teacher": {
                    "hello": "Hello student! 👋 How can I help you with your studies today?",
                    "hi": "Hi there! Ready to learn something new?",
                    "help": "I can help you with:\n• Subject doubts\n• Assignment guidance\n• Exam preparation\n• Study techniques\n\nWhat do you need help with?",
                    "assignment": "Here are some tips for assignments:\n1. Start early and break it down\n2. Research thoroughly\n3. Create an outline\n4. Write and revise\n5. Use citations properly",
                    "exam": "Exam preparation strategy:\n• Create a study schedule\n• Practice previous papers\n• Make concise notes\n• Teach concepts to others\n• Take regular breaks",
                    "math": "For mathematics:\n• Practice daily\n• Understand formulas, don't just memorize\n• Solve varied problems\n• Review mistakes",
                    "physics": "Physics tips:\n• Understand concepts visually\n• Relate to real-world examples\n• Practice numerical problems\n• Draw diagrams",
                    "chemistry": "Chemistry study tips:\n• Learn periodic trends\n• Practice reaction mechanisms\n• Use mnemonics\n• Understand rather than memorize",
                    "programming": "Programming tips:\n• Code daily\n• Build projects\n• Debug systematically\n• Read others' code\n• Learn data structures",
                    "default": "That's a great question! Let me help you understand this better. Could you provide more details?"
                },
                "counselor": {
                    "hello": "Hello! How are you feeling today? 😊",
                    "hi": "Hi there! I'm here to support you.",
                    "stress": "It's completely normal to feel stressed. Here's what helps:\n• Deep breathing exercises\n• Break tasks into smaller chunks\n• Take regular breaks\n• Talk to someone you trust\n• Get enough sleep",
                    "anxiety": "When feeling anxious:\n1. Breathe deeply for 4-7-8 counts\n2. Ground yourself (5-4-3-2-1 technique)\n3. Challenge negative thoughts\n4. Focus on what you can control",
                    "motivation": "You're doing great! Remember:\n• Progress, not perfection\n• Celebrate small wins\n• Your journey is unique\n• Every expert was once a beginner",
                    "career": "Career planning tips:\n1. Explore your interests\n2. Research career paths\n3. Gain relevant skills\n4. Network with professionals\n5. Seek internships",
                    "default": "I'm here to listen and support you. What would you like to talk about?"
                },
                "friend": {
                    "hello": "Hey! What's up? 😊",
                    "hi": "Hey there! How's your day going?",
                    "study": "Want to study together? We can quiz each other and share notes!",
                    "bored": "Take a break! Maybe:\n• Grab a snack 🍪\n• Listen to music 🎵\n• Take a short walk 🚶\n• Watch a funny video 😄",
                    "tired": "I feel you! Remember to:\n• Take a power nap\n• Stay hydrated\n• Stretch a bit\n• You've got this! 💪",
                    "default": "I'm here for you! Tell me what's on your mind."
                },
                "mentor": {
                    "hello": "Welcome! Ready to plan your career journey? 🚀",
                    "hi": "Hello! Let's work on your professional growth.",
                    "career": "Career development roadmap:\n1. Define your goals\n2. Assess current skills\n3. Identify skill gaps\n4. Create learning plan\n5. Build projects\n6. Network and apply",
                    "skills": "In-demand tech skills 2025:\n• AI/ML\n• Full Stack Development\n• Cloud Computing\n• Cybersecurity\n• Data Science\n\nFocus on fundamentals + one specialization",
                    "resume": "Resume tips:\n• Quantify achievements\n• Use action verbs\n• Tailor for each job\n• Include projects\n• Keep it concise (1-2 pages)",
                    "interview": "Interview preparation:\n1. Research the company\n2. Practice DSA problems\n3. Prepare stories (STAR method)\n4. Ask thoughtful questions\n5. Follow up afterwards",
                    "default": "Let's discuss your career goals. What would you like to focus on?"
                }
            }

            # Get appropriate response
            category_responses = responses.get(professional, responses["teacher"])
            reply = category_responses["default"]

            for key, value in category_responses.items():
                if key in user_message:
                    reply = value
                    break

            return JsonResponse({"reply": reply})

        except Exception as e:
            return JsonResponse({"reply": "I'm here to help! Could you please rephrase that?"})

    return JsonResponse({"error": "Only POST method allowed"}, status=405)

# Chatbot UI
def chatbot_ui(request):
    return render(request, 'chat.html')

# Student Dashboard
@login_required
def student_dashboard(request):
    # Get user's data (will have dummy data automatically)
    certificates = Certificate.objects.filter(user=request.user)
    projects = Project.objects.filter(user=request.user)
    competitive_exams = CompetitiveExam.objects.filter(user=request.user)
    performances = Performance.objects.filter(user=request.user)[:5]

    context = {
        'certificates': certificates,
        'projects': projects,
        'competitive_exams': competitive_exams,
        'performances': performances,
        'user': request.user,
    }
    return render(request, 'student_dashboard.html', context)

# Get certificates API
@login_required
def get_certificates(request):
    certificates = Certificate.objects.filter(user=request.user).values()
    return JsonResponse({'certificates': list(certificates)})

# Get projects API
@login_required
def get_projects(request):
    projects = Project.objects.filter(user=request.user).values()
    return JsonResponse({'projects': list(projects)})

# Get exams API
@login_required
def get_exams(request):
    exams = CompetitiveExam.objects.filter(user=request.user).values()
    return JsonResponse({'exams': list(exams)})