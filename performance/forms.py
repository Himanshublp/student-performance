from django import forms
from django.contrib.auth.models import User
from .models import Certificate, Project, CompetitiveExam

class MarksheetUploadForm(forms.Form):
    marksheet = forms.FileField(label="Upload Marksheet")

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['name', 'issued_by', 'date_issued']
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date'}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'date_started', 'date_completed']
        widgets = {
            'date_started': forms.DateInput(attrs={'type': 'date'}),
            'date_completed': forms.DateInput(attrs={'type': 'date'}),
        }

class CompetitiveExamForm(forms.ModelForm):
    class Meta:
        model = CompetitiveExam
        fields = ['exam_name', 'score', 'date_taken']
        widgets = {
            'date_taken': forms.DateInput(attrs={'type': 'date'}),
        }