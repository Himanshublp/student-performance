import datetime
from django.db import models
from django.contrib.auth.models import User

# Model to store the marksheet file

class Semester(models.Model):
    semester_number = models.IntegerField()
    sgpa = models.FloatField()
    total_marks = models.IntegerField()
    result_status = models.CharField(max_length=50)

    def __str__(self):
        return f"Semester {self.semester_number}"

class Subject(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    internal_marks = models.IntegerField()
    external_marks = models.IntegerField()
    grade = models.CharField(max_length=2)

    def __str__(self):
        return self.name
class Marksheet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='marksheets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Marksheet of {self.user.username}'

# Model for different types of exams
class ExamType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Model to store performance of users in exams
class Performance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    semester = models.CharField(max_length=10, default="Unknown")
    date = models.DateField(default=datetime.date.today)  # Default to today's date

    def __str__(self):
        return f'{self.user.username} - {self.exam_type.name} - {self.score}'
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
    date_completed = models.DateField()

    def __str__(self):
        return self.title

class CompetitiveExam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=200)
    score = models.FloatField()
    date_taken = models.DateField()

    def __str__(self):
        return self.exam_name
    
class Document(models.Model):
    title = models.CharField(max_length=200)
    pdf_file = models.FileField(upload_to='pdfs/')  # The 'pdfs/' directory will store the uploaded files

    def __str__(self):
        return self.title