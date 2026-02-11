import datetime
from django.db import models
from django.contrib.auth.models import User

class Semester(models.Model):
    semester_number = models.IntegerField()
    sgpa = models.FloatField(default=0.0)
    total_marks = models.IntegerField(default=0)
    result_status = models.CharField(max_length=50, default="PASS")

    def __str__(self):
        return f"Semester {self.semester_number}"

class Subject(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')
    code = models.CharField(max_length=20, default="CS101")
    name = models.CharField(max_length=100)
    internal_marks = models.IntegerField(default=0)
    external_marks = models.IntegerField(default=0)
    grade = models.CharField(max_length=2, default="A")

    def __str__(self):
        return self.name

class Marksheet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='marksheets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Marksheet of {self.user.username}'

class ExamType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Performance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, null=True, blank=True)
    semester = models.CharField(max_length=10, default="Unknown")
    date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return f'{self.user.username} - {self.exam_type.name if self.exam_type else "No Exam"} - {self.score}'

class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    issued_by = models.CharField(max_length=200)
    date_issued = models.DateField()

    def __str__(self):
        return self.name

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_started = models.DateField()
    date_completed = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

class CompetitiveExam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=200)
    score = models.CharField(max_length=100)
    date_taken = models.DateField()

    def __str__(self):
        return self.exam_name

class Document(models.Model):
    title = models.CharField(max_length=200)
    pdf_file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title