from django import forms
from django.contrib.auth.models import User
from .models import Certificate, Project, CompetitiveExam

class MarksheetUploadForm(forms.Form):
    marksheet = forms.FileField(label="Upload Marksheet")




class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        # Check if both passwords match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 != password2:
            raise forms.ValidationError("Passwords don't match")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data['password1']
        user.set_password(password)  # Hash the password before saving
        if commit:
            user.save()  # Save the user to the database
        return user

users = User.objects.all()
for user in users:
    print(user.username)

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['name', 'issued_by', 'date_issued']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'date_started', 'date_completed']

class CompetitiveExamForm(forms.ModelForm):
    class Meta:
        model = CompetitiveExam
        fields = ['exam_name', 'score', 'date_taken']
