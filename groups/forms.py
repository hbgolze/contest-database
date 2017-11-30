from django import forms
from django.contrib.auth.models import User
from randomtest.models import UserProfile,Test,ProblemGroup



class GroupModelForm(forms.ModelForm):
    class Meta:
        model = ProblemGroup
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={"class":"form-control"}),
        }
