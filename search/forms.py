from django import forms
#from django.contrib.auth.models import User
from randomtest.models import Problem,Tag,Type,Solution,QuestionType,Comment,ProblemApproval,NewTag

class ProblemGroupForm(forms.ModelForm):
#    newtags=forms.ModelMultipleChoiceField(widget = FilteredSelectMultiple('newtags',is_stacked=False), queryset = NewTag.objects.all().exclude(label='root'),required=False,label="Tags")
    class Meta:
        model = Problem
        fields = ( 'newtags',)
    def __init__(self, *args, **kwargs):
        super(ProblemGroupForm, self).__init__(*args, **kwargs)   
        self.fields['newtags'].queryset = NewTag.objects.order_by('tag').exclude(label='root')


