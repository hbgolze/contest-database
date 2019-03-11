from django import forms
from django.contrib.auth.models import User
from randomtest.models import UserProfile,Test,ProblemGroup,NewTag



class GroupModelForm(forms.ModelForm):
    class Meta:
        model = ProblemGroup
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={"class":"form-control"}),
        }
class AddProblemsForm(forms.Form):
    contest_type = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}))
    desired_tag = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}))
    num_problems = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control','style':'width:75px;'}),required=False)
    prob_num_low = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control','style':'width:75px;'}),required=False)
    prob_num_high = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control','style':'width:75px;'}),required=False)
    year_low = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control','style':'width:105px;'}),required=False)
    year_high = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control','style':'width:105px;'}),required=False)
    def __init__(self, userprofile=None, *args, **kwargs):
        super(AddProblemsForm, self).__init__(*args, **kwargs)
        user_choices = []
        for type in userprofile.user_type_new.allowed_types.all():
            user_choices.append((type.type,type.label))
        self.fields['contest_type'].choices = user_choices
        tags = [('Unspecified','Unspecified')]
        for tag in NewTag.objects.exclude(tag='root'):
            tags.append((tag.tag,tag))
        self.fields['desired_tag'].choices = tags
