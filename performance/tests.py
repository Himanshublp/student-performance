# performance/forms.py

from django import forms

class MarksheetUploadForm(forms.Form):
    marksheet = forms.FileField()
