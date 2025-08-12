from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import json
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegistrationForm  # If you have a custom form for registration
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import csv
from .models import Marksheet, ExamType, Performance
import pdfplumber
import csv
from .forms import CertificateForm, ProjectForm, CompetitiveExamForm
from .models import Certificate, Project, CompetitiveExam
from io import StringIO
from .models import Semester, Subject
from .utils.pdf_processor import extract_data_from_pdf, save_data_to_csv
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')
import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json
import requests
from dotenv import load_dotenv
from django.http import JsonResponse
load_dotenv()

API_KEY = os.getenv("API_KEY")


# Home view redirects to login page for unauthenticated users or to dashboard if authenticated
def home(request):
    print(request)
    print("line no 14",request.user)

    if not request.user.is_authenticated:
        return redirect('login')
    return redirect('dashboard') 

# Registration view for creating new users
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the user to the database
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')  # Redirect to login page after registration
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# Login view for existing users
def user_login(request):
    print(request)
    print("line no 14",request)
    # If the user is already authenticated, redirect them to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate the user with the provided credentials
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)  # Log the user in
            return redirect('dashboard')  # Redirect to the dashboard or home page
        else:
            messages.error(request, 'Invalid credentials. Please try again or register.')
    
    return render(request, 'login.html') 

# Logout view
def user_logout(request):
    logout(request)
    return redirect('login')

# Dashboard view for authenticated users

@login_required
def dashboard(request): 
    # Ensure the user is logged in
    print("started")
    if not request.user.is_authenticated:
        return redirect('login')

    # Fetch all semesters and print the data to debug
    semesters = Semester.objects.all()
    
    print("Semesters: ", semesters)  # Debug: List all semesters

    performance_data = []
    for sem in semesters:
        # Fetch all subjects for the current semester and print them for debugging
        subjects = sem.subjects.all()
        print(f"Subjects for Semester {sem.semester_number}: ", subjects)

        # Identify weak subjects based on grade and print for debugging
        weak_subjects = [sub.name for sub in subjects if sub.grade in ('C', 'D')]
        print(f"Weak subjects for Semester {sem.semester_number}: ", weak_subjects)

        performance_data.append({
            'semester': sem.semester_number,
            'sgpa': sem.sgpa,
            'weak_subjects': weak_subjects,
        })
    
    # Print the performance data being built to debug
    print("Performance Data: ", performance_data)

    # Generate a performance trend plot and print related data
    sgpas = [sem.sgpa for sem in semesters]
    semesters_labels = [f"Sem {sem.semester_number}" for sem in semesters]
    print("SGPA Values: ", sgpas)
    print("Semester Labels: ", semesters_labels)

    # Plot the SGPA trend
    plt.figure(figsize=(10, 5))
    plt.plot(semesters_labels, sgpas, marker='o')
    plt.title('SGPA Trend')
    plt.xlabel('Semester')
    plt.ylabel('SGPA')
    plt.grid()
    plt.tight_layout()

    # Save plot to buffer and prepare for base64 encoding
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    buffer.close()

    # Print the base64 encoded image (debugging)
    print("Base64 Encoded SGPA Plot: ", image_base64[:100])  # Print first 100 characters for brevity

    return render(request, 'dashboard.html', {
        'performance_data': performance_data,
        'performance_trend': image_base64,
    })

# Generate a report of the user's performance
def generate_report(request):
    # Get the performance data for the logged-in user
    performances = Performance.objects.filter(user=request.user)

    # Collect performance data for graphing
    performance_data = [p.score for p in performances]
    performance_labels = [p.exam_type.name for p in performances]

    # Weak subjects: subjects with a score below 40
    weak_subjects = performances.filter(score__lt=40)

    context = {
        'performance_data': json.dumps(performance_data),
        'performance_labels': json.dumps(performance_labels),
        'weak_subjects': weak_subjects,
    }

    return render(request, 'performance_report.html', context)

# Marksheet upload view
def upload_marksheet(request):
    if request.method == 'POST' and request.FILES['marksheet']:
        marksheet_file = request.FILES['marksheet']
        
        # Process the uploaded PDF file
        extracted_data = process_marksheet(marksheet_file)

        # Save the marksheet file
        Marksheet.objects.create(user=request.user, file=marksheet_file)

        # Save the extracted data to the Performance model
        for entry in extracted_data:
            exam_type, _ = ExamType.objects.get_or_create(name=entry['subject_name'])
            Performance.objects.create(
                user=request.user,
                exam_type=exam_type,
                score=entry['total_marks'],
                semester=entry['semester']
            )

        messages.success(request, "Marksheet uploaded and processed successfully!")
        return redirect('dashboard')

    return render(request, 'upload_marksheet.html') # Return the template for uploading marksheet

# Process marksheet (dummy implementation for extracting data)


import pdfplumber 
import pdfplumber

def process_marksheet(file):
    with pdfplumber.open(file) as pdf:
        data = []
        semester = None

        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split("\n")

            for line in lines:
                # Check for semester header
                if "Semester :" in line:
                    semester = line.split(":")[1].strip()
                    continue

                # Skip header lines
                if "Code" in line and "Name" in line and "Type" in line:
                    continue

                # Parse subject details
                if "Theory" in line or "Practical" in line:
                    parts = line.split()
                    if len(parts) < 5:
                        continue  # Skip lines that don't have enough parts

                    try:
                        subject_code = parts[0]
                        subject_name = " ".join(parts[1:-3])
                        subject_type = parts[-3]

                        # Handle non-numeric placeholders (e.g., '--')
                        internal_marks = parts[-2]
                        external_marks = parts[-1]

                        internal_marks = int(internal_marks) if internal_marks.isdigit() else 0
                        external_marks = int(external_marks) if external_marks.isdigit() else 0
                        total_marks = internal_marks + external_marks

                        data.append({
                            "semester": semester,
                            "subject_code": subject_code,
                            "subject_name": subject_name,
                            "subject_type": subject_type,
                            "internal_marks": internal_marks,
                            "external_marks": external_marks,
                            "total_marks": total_marks,
                        })
                    except ValueError as e:
                        # Log or handle lines that cannot be parsed
                        print(f"Skipping line due to error: {line} -> {e}")
                        continue

        return data





# Upload and process marksheet
from io import StringIO
import csv

def upload_marksheet(request):
    if request.method == 'POST' and request.FILES['marksheet']:
        marksheet_file = request.FILES['marksheet']
        
        # Process the uploaded PDF file
        extracted_data = process_marksheet(marksheet_file)

        # Save the marksheet file
        Marksheet.objects.create(user=request.user, file=marksheet_file)

        # Save the extracted data to the Performance model
        for entry in extracted_data:
            exam_type, _ = ExamType.objects.get_or_create(name=entry['subject_name'])
            print(f"Creating performance record for {entry['subject_name']} with score {entry['total_marks']}")  # Debug log
            Performance.objects.create(
                user=request.user,
                exam_type=exam_type,
                score=entry['total_marks'],
                semester=entry['semester']  # Ensure semester is passed
            )

        messages.success(request, "Marksheet uploaded and processed successfully!")
        return redirect('dashboard')

    return render(request, 'upload_marksheet.html')



# View full performance report
# View full performance report
def view_full_report(request):
    performances = Performance.objects.filter(user=request.user).order_by('semester')
    semesters = performances.values('semester').distinct()

    # Organize data by semester and subject
    report_data = {
        semester['semester']: performances.filter(semester=semester['semester'])
        for semester in semesters
    }

    # Prepare data for the graph
    semester_labels = []
    performance_data = []
    subject_labels = {}

    for semester, performance in report_data.items():
        semester_labels.append(semester)
        semester_scores = []
        for entry in performance:
            if entry.exam_type.name not in subject_labels:
                subject_labels[entry.exam_type.name] = []
            subject_labels[entry.exam_type.name].append(entry.score)
            semester_scores.append(entry.score)
        performance_data.append(semester_scores)

    context = {
        'report_data': report_data,
        'semester_labels': json.dumps(semester_labels),
        'performance_data': json.dumps(performance_data),
        'subject_labels': json.dumps(list(subject_labels.keys())),
    }

    return render(request, 'report.html', context)

def progress_report(request):
    performance = Performance.objects.filter(user=request.user)
    return render(request, 'progress_report.html', {'performance': performance})

def add_certificate(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.user = request.user  # Associate with the logged-in user
            certificate.save()
            return render(request, 'certificate.html', {'certificate': certificate})  # show the data
    else:
        form = CertificateForm()
    return render(request, 'certificate_form.html', {'form': form})  # separate form page if needed
@csrf_exempt
def chatbot_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_msg = data.get("message", "").lower()

        # Simple rule-based bot logic
        if "hello" in user_msg or "hi" in user_msg:
            response = "Hello! How can I help you with your performance?"
        elif "performance" in user_msg:
            response = "Your average score is 82%. You are doing well!"
        elif "math" in user_msg:
            response = "You scored 88 in Math. Great job!"
        elif "improve" in user_msg:
            response = "You should focus more on Science and English."
        else:
            response = "I'm not sure about that. Try asking about your subjects or scores."

        return JsonResponse({"response": response})
    return JsonResponse({"response": "Invalid request"}, status=400)

def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect('student_dashboard')
    else:
        form = ProjectForm()
    return render(request, 'project.html', {'form': form})

def add_competitive_exam(request):
    if request.method == 'POST':
        form = CompetitiveExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.user = request.user
            exam.save()
            return redirect('student_dashboard')
    else:
        form = CompetitiveExamForm()
    return render(request, 'competitive_exam.html', {'form': form})
from django.shortcuts import render
from .utils.pdf_processor import extract_data_from_pdf

def upload_pdf(request):
    if request.method == 'POST':
        pdf_file = request.FILES['pdf_file']
        data = extract_data_from_pdf(pdf_file)
        print(data)

        # Save data to session
        request.session['pdf_data'] = data  # Store in session

        return render(request, 'upload_success.html')

    return render(request, 'upload_pdf.html')

def dashboard(request):
    semesters = Semester.objects.all()
    performance_data = []
    for sem in semesters:
        subjects = sem.subjects.all()
        weak_subjects = [sub.name for sub in subjects if sub.grade in ('C', 'D')]
        performance_data.append({
            'semester': sem.semester_number,
            'sgpa': sem.sgpa,
            'weak_subjects': weak_subjects,
        })

    # Generate a performance trend plot
    sgpas = [sem.sgpa for sem in semesters]
    semesters_labels = [f"Sem {sem.semester_number}" for sem in semesters]

    plt.figure(figsize=(10, 5))
    plt.plot(semesters_labels, sgpas, marker='o')
    plt.title('SGPA Trend')
    plt.xlabel('Semester')
    plt.ylabel('SGPA')
    plt.grid()
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    buffer.close()

    return render(request, 'dashboard.html', {
        'performance_data': performance_data,
        'performance_trend': image_base64,
    })
def guided_plan(request):
    # Example data for context
    context = {
        'title': 'Guided Plan',
        'content': 'Welcome to the Guided Plan Page!',
    }

    # Return an HttpResponse using render
    return render(request, 'guided_plan.html', context)
@csrf_exempt
# views.py

@csrf_exempt
# Replace with your actual OpenRouter API key


def ai_chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://yourdomain.com",  # Optional for ranking
                "X-Title": "AgriConnect Chatbot"           # Optional for project name
            }
            payload = {
                "model": "openai/gpt-3.5-turbo",  # or use a free model like meta-llama/llama-3-8b-instruct
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            }

            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()

            if "choices" in response_data and len(response_data["choices"]) > 0:
                reply = response_data["choices"][0]["message"]["content"]
                return JsonResponse({"reply": reply})
            elif "error" in response_data:
                return JsonResponse({"error": response_data["error"].get("message", "API error")}, status=500)
            else:
                return JsonResponse({"error": "Unexpected API response format."}, status=500)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST method allowed"}, status=405)


def chatbot_ui(request):
    return render(request, 'chat.html')


def student_dashboard(request):
    return render(request, 'student_dashboard.html')