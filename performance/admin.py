from django.contrib import admin
from .models import (
    Semester, Subject, Marksheet, ExamType, Performance,
    Certificate, Project, CompetitiveExam, Document
)

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ['semester_number', 'sgpa', 'total_marks', 'result_status']
    search_fields = ['semester_number']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'semester', 'grade']
    list_filter = ['semester', 'grade']
    search_fields = ['name', 'code']

@admin.register(Marksheet)
class MarksheetAdmin(admin.ModelAdmin):
    list_display = ['user', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['user__username']

@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'exam_type', 'score', 'semester', 'date']
    list_filter = ['semester', 'date']
    search_fields = ['user__username', 'exam_type__name']

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'issued_by', 'date_issued']
    list_filter = ['date_issued']
    search_fields = ['name', 'user__username']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'date_started', 'date_completed']
    list_filter = ['date_started']
    search_fields = ['title', 'user__username']

@admin.register(CompetitiveExam)
class CompetitiveExamAdmin(admin.ModelAdmin):
    list_display = ['exam_name', 'user', 'score', 'date_taken']
    list_filter = ['date_taken']
    search_fields = ['exam_name', 'user__username']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['title']