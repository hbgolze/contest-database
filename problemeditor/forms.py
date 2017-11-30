from django import forms
#from django.contrib.auth.models import User
from randomtest.models import Problem,Tag,Type,Solution,QuestionType,Comment,ProblemApproval,NewTag
from django.contrib.admin.widgets import FilteredSelectMultiple
from randomtest.utils import newsoltexcode,compileasy

from django.forms.widgets import HiddenInput
ANSWER_CHOICES = (
    ('A','Answer A'),
    ('B','Answer B'),
    ('C','Answer C'),
    ('D','Answer D'),
    ('E','Answer E'),
    )
APPROVAL_CHOICES = (
    ('AP', 'Approved'),
    ('MN', 'Approved Subject to Minor Revision'),
    ('MJ', 'Needs Major Revision'),
    ('DE', 'Propose For Deletion'),
    )

class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ('solution_text',)
        widgets = {
            'solution_text': forms.Textarea(attrs={"class":"form-control","min-width":"100%", 'rows': 15,'id' : 'codetext'})
        }
    def save(self,commit=True):
        instance = super(SolutionForm, self).save(commit=False)
        instance.display_solution_text = newsoltexcode(instance.solution_text,instance.problem_label+'sol'+str(instance.solution_number))
        compileasy(instance.solution_text,instance.problem_label,sol='sol'+str(instance.solution_number))
        if commit:
            instance.save()
        return instance

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('author_name','comment_text',)
        widgets = {
            'comment_text': forms.Textarea(attrs={"class":"form-control","min-width":"100%", 'rows': 15,'id' : 'codetext'}),
            'author_name': forms.TextInput(attrs={"class":"form-control"}),
        }
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)   
        self.fields['author_name'].required = True

class ApprovalForm(forms.ModelForm):
    class Meta:
        model = ProblemApproval
        fields = ('author_name','approval_status',)
        widgets = {
            'author_name': forms.TextInput(attrs={"class":"form-control"}),
            'approval_status': forms.Select(attrs={"class":"form-control"})
            }
    def __init__(self, *args, **kwargs):
        super(ApprovalForm, self).__init__(*args, **kwargs)   
        self.fields['author_name'].required = True
        self.fields['approval_status'].required = True



class AddProblemForm1(forms.Form):
    question_type = forms.ModelChoiceField(widget = forms.RadioSelect(), queryset = QuestionType.objects.all(),required=True,empty_label=None)
    type = forms.ModelChoiceField(widget = forms.RadioSelect(),queryset=Type.objects.filter(type__startswith="CM"),required=True,empty_label=None)
    author_name = forms.CharField()
    def __init__(self, *args, **kwargs):
        super(AddProblemForm1, self).__init__(*args, **kwargs)
        self.fields['author_name'].widget.attrs['class'] = 'form-control col-md-6'

class AddProblemForm2MC(forms.Form):
    mc_problem_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext','class':'form-control'}))
    answer_A = forms.CharField()
    answer_B = forms.CharField()
    answer_C = forms.CharField()
    answer_D = forms.CharField()
    answer_E = forms.CharField()
    correct_multiple_choice_answer = forms.ChoiceField(widget = forms.RadioSelect(),choices=ANSWER_CHOICES)
    mc = forms.CharField(required=False)
    def __init__(self, *args, **kwargs):
        super(AddProblemForm2MC, self).__init__(*args, **kwargs)
        self.fields['answer_A'].widget.attrs['class'] = 'form-control col-md-6'
        self.fields['answer_B'].widget.attrs['class'] = 'form-control col-md-6'
        self.fields['answer_C'].widget.attrs['class'] = 'form-control col-md-6'
        self.fields['answer_D'].widget.attrs['class'] = 'form-control col-md-6'
        self.fields['answer_E'].widget.attrs['class'] = 'form-control col-md-6'

class AddProblemForm2SA(forms.Form):
    problem_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext','class':'form-control'}))
    correct_short_answer_answer = forms.CharField()
    sa = forms.CharField(required=False)
    def __init__(self, *args, **kwargs):
        super(AddProblemForm2SA, self).__init__(*args, **kwargs)
        self.fields['correct_short_answer_answer'].widget.attrs['class'] = 'form-control col-md-6'


class AddProblemForm2PF(forms.Form):
    problem_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext','class':'form-control'}))
    pf = forms.CharField(required=False)

class AddProblemForm2MCSA(forms.Form):
    problem_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext','class':'form-control'}))
    correct_short_answer_answer = forms.CharField()    
    mc_problem_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext','class':'form-control'}))
    answer_A = forms.CharField()
    answer_B = forms.CharField()
    answer_C = forms.CharField()
    answer_D = forms.CharField()
    answer_E = forms.CharField()
    correct_multiple_choice_answer = forms.ChoiceField(widget = forms.RadioSelect(),choices=ANSWER_CHOICES)
    mcsa = forms.CharField(required=False)
    def __init__(self, *args, **kwargs):
        super(AddProblemForm2MCSA, self).__init__(*args, **kwargs)
        self.fields['answer_A'].widget.attrs['class'] = 'form-control col-md-6'
        self.fields['answer_B'].widget.attrs['class'] = 'form-control col-md-6'
        self.fields['answer_C'].widget.attrs['class'] = 'form-control col-md-6'
        self.fields['answer_D'].widget.attrs['class'] = 'form-control col-md-6'
        self.fields['answer_E'].widget.attrs['class'] = 'form-control col-md-6'
        self.fields['correct_short_answer_answer'].widget.attrs['class'] = 'form-control col-md-6'

class AddProblemForm3(forms.Form):
    solution_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext','class':'form-control'}))
    
class ChangeQuestionTypeForm1(forms.ModelForm):
#    question_type_new = forms.ModelChoiceField(widget = forms.RadioSelect(), queryset = QuestionType.objects.all(),required=True,empty_label=None)
    question_type_new = forms.ModelChoiceField(widget = forms.Select(attrs={'class':'form-control'}), queryset = QuestionType.objects.all(),required=True,empty_label=None)
    class Meta:
        model = Problem
        fields = ('question_type_new',)
    def __init__(self, *args, **kwargs):
        super(ChangeQuestionTypeForm1, self).__init__(*args, **kwargs)   
        self.fields['question_type_new'].label = "Question Type:"

class ChangeQuestionTypeForm2MC(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('mc_problem_text',
                  'answer_A',
                  'answer_B',
                  'answer_C',
                  'answer_D',
                  'answer_E',
                  'mc_answer',
                  )
        widgets = {
            'mc_problem_text': forms.Textarea(attrs={'style': 'min-width: 100%', 'rows': 15,'id' : 'codetext'}),
            'mc_answer': forms.RadioSelect(choices=ANSWER_CHOICES),
            'answer_A': forms.TextInput(attrs={'class':'form-control'}),
            'answer_B': forms.TextInput(attrs={'class':'form-control'}),
            'answer_C': forms.TextInput(attrs={'class':'form-control'}),
            'answer_D': forms.TextInput(attrs={'class':'form-control'}),
            'answer_E': forms.TextInput(attrs={'class':'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(ChangeQuestionTypeForm2MC, self).__init__(*args, **kwargs)   
        self.fields['mc_problem_text'].required = True
        self.fields['answer_A'].required = True
        self.fields['answer_B'].required = True
        self.fields['answer_C'].required = True
        self.fields['answer_D'].required = True
        self.fields['answer_E'].required = True
        self.fields['mc_answer'].required = True
        self.fields['mc_answer'].label = 'Answer:'

class ChangeQuestionTypeForm2SA(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('problem_text',
                  'sa_answer',
                  )
        widgets = {
            'problem_text': forms.Textarea(attrs={'style': 'min-width: 100%', 'rows': 15,'id' : 'codetext'}),
            'sa_answer': forms.TextInput(attrs={'class':'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(ChangeQuestionTypeForm2SA, self).__init__(*args, **kwargs)   
        self.fields['problem_text'].required = True
        self.fields['sa_answer'].required = True
        self.fields['sa_answer'].label = 'Answer:'

class ChangeQuestionTypeForm2PF(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('problem_text',
                  )
        widgets = {
            'problem_text': forms.Textarea(attrs={'style': 'min-width: 100%', 'rows': 15,'id' : 'codetext'}),
            }
    def __init__(self, *args, **kwargs):
        super(ChangeQuestionTypeForm2PF, self).__init__(*args, **kwargs)   
        self.fields['problem_text'].required = True

class ChangeQuestionTypeForm2MCSA(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('mc_problem_text',
                  'answer_A',
                  'answer_B',
                  'answer_C',
                  'answer_D',
                  'answer_E',
                  'mc_answer',
                  'problem_text',
                  'sa_answer',
                  )
        widgets = {
            'mc_problem_text': forms.Textarea(attrs={'style': 'min-width: 100%', 'rows': 15,'id' : 'codetext'}),
            'problem_text': forms.Textarea(attrs={'style': 'min-width: 100%', 'rows': 15,'id' : 'codetext'}),
            'mc_answer': forms.RadioSelect(choices=ANSWER_CHOICES),
            'answer_A': forms.TextInput(attrs={'class':'form-control'}),
            'answer_B': forms.TextInput(attrs={'class':'form-control'}),
            'answer_C': forms.TextInput(attrs={'class':'form-control'}),
            'answer_D': forms.TextInput(attrs={'class':'form-control'}),
            'answer_E': forms.TextInput(attrs={'class':'form-control'}),
            'sa_answer': forms.TextInput(attrs={'class':'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(ChangeQuestionTypeForm2MCSA, self).__init__(*args, **kwargs)   
        self.fields['mc_problem_text'].required = True
        self.fields['problem_text'].required = True
        self.fields['answer_A'].required = True
        self.fields['answer_B'].required = True
        self.fields['answer_C'].required = True
        self.fields['answer_D'].required = True
        self.fields['answer_E'].required = True
        self.fields['mc_answer'].required = True
        self.fields['sa_answer'].required = True
        self.fields['mc_answer'].label = 'Answer (Multiple Choice):'
        self.fields['sa_answer'].label = 'Answer (Short Answer):'

class AddContestForm(forms.Form):
#    type = forms.ModelChoiceField( queryset = Type.objects.exclude(type__startswith='CM'),required=True)
    year = forms.CharField(max_length=4,label='Year',required=True)
    formletter = forms.CharField(max_length=2,label='Form',required=False)
    def __init__(self, *args, **kwargs):
        num_probs = kwargs.pop('num_probs')
        typ = Type.objects.get(type=kwargs.pop('type'))
        super(AddContestForm,self).__init__(*args,**kwargs)
        for i in range(1,num_probs+1):
            self.fields['problem_text%s' % i] = forms.CharField(widget=forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}),label='Problem %s' % i)
            if typ.default_question_type=='mc':
                self.fields['answer_A%s' % i] = forms.CharField(max_length=255,label='Answer A')
                self.fields['answer_B%s' % i] = forms.CharField(max_length=255,label='Answer B')
                self.fields['answer_C%s' % i] = forms.CharField(max_length=255,label='Answer C')
                self.fields['answer_D%s' % i] = forms.CharField(max_length=255,label='Answer D')
                self.fields['answer_E%s' % i] = forms.CharField(max_length=255,label='Answer E')
                self.fields['answer%s' % i] = forms.ChoiceField(label='Answer',widget =forms.RadioSelect, choices=(('A','A'),('B','B'),('C','C'),('D','D'),('E','E')))
            elif typ.default_question_type=='sa':
                self.fields['answer%s' % i] = forms.CharField(max_length=50,label = 'Answer')


class DuplicateProblemForm(forms.Form):
    duplicate_problem_label=forms.CharField(max_length=30,required=True)
    def clean_label(self):
        data = self.cleaned_data['duplicate_problem_label']
        if Problem.objects.get(label=data).exists() == False:
            raise forms.ValidationError("Not a Valid Problem!")

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return data



class UploadContestForm(forms.Form):
    T=Type.objects.filter(is_contest=1)
    CONTEST_CHOICES=tuple((i.type,i.label) for i in T)
    year = forms.CharField(max_length=4,label='Year',required=True)
    formletter = forms.CharField(max_length=2,label='Form',required=False)
    typ = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}), choices = CONTEST_CHOICES,label="Contest Type",required=True)
    contestfile=forms.FileField()

class NewTagForm(forms.ModelForm):
    class Meta:
        model = NewTag
        fields = ('label','description',)
        widgets = {
            'label': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'style': 'min-width: 100%', 'rows': 5,'class':'form-control'}),
            }
class AddNewTagForm(forms.ModelForm):
    class Meta:
        model = NewTag
        fields = ('label','parent','description',)
        widgets = {
            'label': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'style': 'min-width: 100%', 'rows': 5,'class':'form-control'}),
            }
    def __init__(self,*args, **kwargs):
        super(AddNewTagForm, self).__init__(*args, **kwargs)
        self.fields['parent'].widget = HiddenInput()
        self.fields['description'].required = True
#    def clean(self):
#        cleaned_data = super(AddNewTagForm,self).clean()
#        label_clean = cleaned_data.get('label')
#        parent_clean = cleaned_data.get('parent')
#        if parent_clean.children.filter(label=label_clean).exists() == True:
#            raise forms.ValidationError("Tag already exists!")

class EditMCAnswer(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('mc_answer',)
        widgets = {
            'mc_answer': forms.RadioSelect(choices=ANSWER_CHOICES)
            }
    def __init__(self, *args, **kwargs):
        super(EditMCAnswer,self).__init__(*args,**kwargs)
        self.fields['mc_answer'].label = "Answer"

class EditSAAnswer(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('sa_answer',)
        widgets = {
            'sa_answer': forms.TextInput(attrs={'class':'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(EditSAAnswer,self).__init__(*args,**kwargs)
        self.fields['sa_answer'].label = "Answer"


class MCProblemTextForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('mc_problem_text','answer_A','answer_B','answer_C','answer_D','answer_E',)
        widgets = {
            'mc_problem_text': forms.Textarea(attrs={'style': 'min-width: 100%', 'rows': 15,'id' : 'codetext'}),
            }
    def __init__(self, *args, **kwargs):
        super(MCProblemTextForm, self).__init__(*args, **kwargs)
        self.fields['mc_problem_text'].label = 'Problem Text'

class SAProblemTextForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('problem_text',)
        widgets = {
            'problem_text': forms.Textarea(attrs={'style': 'min-width: 100%', 'rows': 15,'id' : 'codetext'}),
            }
    def __init__(self, *args, **kwargs):
        super(SAProblemTextForm, self).__init__(*args, **kwargs)   

class DifficultyForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('difficulty',)
        widgets = {
            'difficulty': forms.TextInput(attrs={"class":"form-control"})
            }
    def __init__(self, *args, **kwargs):
        super(DifficultyForm, self).__init__(*args, **kwargs)
