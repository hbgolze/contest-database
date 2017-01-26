from django import forms
#from django.contrib.auth.models import User
from randomtest.models import Problem,Tag,Type,Solution,QuestionType,Comment,ProblemApproval
from django.contrib.admin.widgets import FilteredSelectMultiple


class AsyForm(forms.Form):
    filename = forms.CharField(max_length=100)
    asy_code = forms.CharField(widget=forms.Textarea)
