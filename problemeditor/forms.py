from django import forms
#from django.contrib.auth.models import User
from randomtest.models import Problem,Tag,Type,Solution,QuestionType,Comment,ProblemApproval
from django.contrib.admin.widgets import FilteredSelectMultiple
from randomtest.utils import newsoltexcode

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
class ProblemForm(forms.ModelForm):
#    widgets = {
#        'tags': forms.ModelMultipleChoiceField(widget=FilteredSelectMultiple(('tags'),False),queryset=Tag.objects.all(),required=False)
#            'tags': forms.SelectMultiple(attrs={'size': 30})
#    }
    tags=forms.ModelMultipleChoiceField(widget = FilteredSelectMultiple('tags',is_stacked=False), queryset = Tag.objects.all(),required=False)
    class Meta:
        model = Problem
        fields = ( 'tags',)
    def __init__(self, *args, **kwargs):
        super(ProblemForm, self).__init__(*args, **kwargs)   
        self.fields['tags'].queryset = Tag.objects.order_by('tag')


class DetailedProblemForm(forms.ModelForm):
    tags=forms.ModelMultipleChoiceField(widget = FilteredSelectMultiple('tags',is_stacked=False), queryset = Tag.objects.all(),required=False)
    class Meta:
        model = Problem
        fields = ('tags','mc_answer','sa_answer','difficulty')
        widgets = {
            'mc_answer': forms.RadioSelect(choices=ANSWER_CHOICES)
        }
    def __init__(self, *args, **kwargs):
        super(DetailedProblemForm, self).__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tag.objects.order_by('tag')

class ProblemTextForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('problem_text','mc_problem_text','answer_A','answer_B','answer_C','answer_D','answer_E')
        widgets = {
            'problem_text': forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}),
            'mc_problem_text': forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}),
            }
    def __init__(self, *args, **kwargs):
        super(ProblemTextForm, self).__init__(*args, **kwargs)   
#        self.fields['answer_choices'].help_text = '<br/><div class="tex2jax_ignore">Should be in the form<br/>$\\textbf{(A) } Ans A\\qquad \\textbf{(B) } Ans B\\qquad \\textbf{(C) } Ans C\\qquad \\textbf{(D) } Ans D\\qquad \\textbf{(E) } Ans E$</div>'

class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ('solution_text',)
        widgets = {
            'solution_text': forms.Textarea(attrs={"class":"form-control","min-width":"100%", 'rows': 15,'id' : 'codetext'})
        }
    def save(self,commit=True):
        instance = super(SolutionForm, self).save(commit=False)
        instance.display_solution_text = newsoltexcode(instance.solution_text,instance.problem_label+str(instance.solution_number))
        if commit:
            instance.save()
        return instance

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('author_name','comment_text',)
        widgets = {
            'comment_text': forms.Textarea(attrs={'cols': 100, 'rows': 15,'id' : 'codetext'})
        }
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)   
        self.fields['author_name'].required = True

class ApprovalForm(forms.ModelForm):
    class Meta:
        model = ProblemApproval
        fields = ('author_name','approval_status',)
    def __init__(self, *args, **kwargs):
        super(ApprovalForm, self).__init__(*args, **kwargs)   
        self.fields['author_name'].required = True
        self.fields['approval_status'].required = True

class MCAnswerForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('mc_answer',)
        widgets = {
            'mc_answer': forms.RadioSelect(choices=ANSWER_CHOICES)
        }

class SAAnswerForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('sa_answer',)


class AddProblemForm(forms.ModelForm):
    tags=forms.ModelMultipleChoiceField(widget = FilteredSelectMultiple('tags',is_stacked=False), queryset = Tag.objects.all(),required=False)
    question_type=forms.ModelMultipleChoiceField(widget = forms.CheckboxSelectMultiple(), queryset = QuestionType.objects.all(),required=True)
    types=forms.ModelChoiceField(widget = forms.RadioSelect(),queryset=Type.objects.filter(type__startswith="CM"),label="Type",empty_label=None)
    class Meta:
        model = Problem
        fields = ('problem_text','answer_choices','difficulty','question_type','types', 'tags','answer','latexanswer','author_name')
        widgets = { 'problem_text': forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}),
                    'answer_choices': forms.Textarea(attrs={'cols': 120, 'rows': 3,'id' : 'codetext'}),
                    }
    def __init__(self, *args, **kwargs):
        super(AddProblemForm, self).__init__(*args, **kwargs)   
        self.fields['tags'].queryset = Tag.objects.order_by('tag')
        self.fields['answer_choices'].help_text = '<br/><div class="tex2jax_ignore">Should be in the form<br/>$\\textbf{(A) } Ans A\\qquad \\textbf{(B) } Ans B\\qquad \\textbf{(C) } Ans C\\qquad \\textbf{(D) } Ans D\\qquad \\textbf{(E) } Ans E$</div>'
        self.fields['problem_text'].label = 'Problem LaTeX'
        self.fields['latexanswer'].label = 'LaTeX Answer'
        self.fields['author_name'].required = True
        self.fields['types'].required = True
    def clean_types(self):
        data = self.cleaned_data['types']
        return [data]

class AddProblemForm1(forms.Form):
    question_type = forms.ModelChoiceField(widget = forms.RadioSelect(), queryset = QuestionType.objects.all(),required=True,empty_label=None)
    type=forms.ModelChoiceField(widget = forms.RadioSelect(),queryset=Type.objects.filter(type__startswith="CM"),required=True,empty_label=None)
    author_name = forms.CharField()

class AddProblemForm2MC(forms.Form):
    mc_problem_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}))
    answer_A = forms.CharField()
    answer_B = forms.CharField()
    answer_C = forms.CharField()
    answer_D = forms.CharField()
    answer_E = forms.CharField()
    correct_multiple_choice_answer = forms.ChoiceField(widget = forms.RadioSelect(),choices=ANSWER_CHOICES)
    mc = forms.CharField(required=False)

class AddProblemForm2SA(forms.Form):
    problem_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}))
    correct_short_answer_answer = forms.CharField()
    sa = forms.CharField(required=False)

class AddProblemForm2PF(forms.Form):
    problem_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}))
    pf = forms.CharField(required=False)

class AddProblemForm2MCSA(forms.Form):
    problem_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}))
    correct_short_answer_answer = forms.CharField()    
    mc_problem_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}))
    answer_A = forms.CharField()
    answer_B = forms.CharField()
    answer_C = forms.CharField()
    answer_D = forms.CharField()
    answer_E = forms.CharField()
    correct_multiple_choice_answer = forms.ChoiceField(widget = forms.RadioSelect(),choices=ANSWER_CHOICES)
    mcsa = forms.CharField(required=False)

class AddProblemForm3(forms.Form):
    solution_text = forms.CharField(widget=forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}))
    
class ChangeQuestionTypeForm1(forms.ModelForm):
#    question_type = forms.ModelChoiceField(widget = forms.RadioSelect(), queryset = QuestionType.objects.all(),required=True,empty_label=None)
    question_type_new = forms.ModelChoiceField(widget = forms.RadioSelect(), queryset = QuestionType.objects.all(),required=True,empty_label=None)
    class Meta:
        model = Problem
        fields = ('question_type_new',)

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
                  'question_type_new',
                  )
        widgets = {
            'mc_problem_text': forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}),
            'mc_answer': forms.RadioSelect(choices=ANSWER_CHOICES),
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

class ChangeQuestionTypeForm2SA(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('problem_text',
                  'sa_answer',
                  'question_type_new',
                  )
        widgets = {
            'problem_text': forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}),
            }
    def __init__(self, *args, **kwargs):
        super(ChangeQuestionTypeForm2SA, self).__init__(*args, **kwargs)   
        self.fields['problem_text'].required = True
        self.fields['sa_answer'].required = True

class ChangeQuestionTypeForm2PF(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('problem_text',
                  'question_type_new',
                  )
        widgets = {
            'problem_text': forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}),
            }
    def __init__(self, *args, **kwargs):
        super(ChangeQuestionTypeForm2PF, self).__init__(*args, **kwargs)   
        self.fields['problem_text'].required = True

class ChangeQuestionTypeForm2MCSA(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ('mc_problem_text',
                  'problem_text',
                  'answer_A',
                  'answer_B',
                  'answer_C',
                  'answer_D',
                  'answer_E',
                  'mc_answer',
                  'sa_answer',
                  'question_type_new',
                  )
        widgets = {
            'mc_problem_text': forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}),
            'problem_text': forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}),
            'mc_answer': forms.RadioSelect(choices=ANSWER_CHOICES),
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


#forms.Textarea(
#                attrs={'cols': 120, 'rows': 15,'id' : 'codetext'},
#                label='problem_%s' %i,
#                )
'''
class ProblemForm(forms.Form):
    class Media:
        # Django also includes a few javascript files necessary
        # for the operation of this form element. You need to
        # include <script src="/admin/jsi18n"></script>
        # in the template.
        css = {
            'all': ('admin/css/widgets.css',)
            }
        js = ('/admin/jsi18n',)
    def __init__(self, *args, **kwargs):
        prob=kwargs.pop('instance')
        r=super(ProblemForm,self).__init__(*args, **kwargs)
#        prob=Problem.objects.get(label=prob_label)
        qs = Tag.objects.exclude(tag__in=[t.tag for t in prob.tags.all()])
        fields=('label')
        self.fields['trags'] = forms.ModelMultipleChoiceField(queryset=qs,widget=FilteredSelectMultiple('tags',is_stacked=False),label='')
        return r
#        fields = ('username', 'email', 'password')


'''

