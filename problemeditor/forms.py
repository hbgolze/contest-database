from django import forms
#from django.contrib.auth.models import User
from randomtest.models import Problem,Tag,Type,Solution,QuestionType,Comment
from django.contrib.admin.widgets import FilteredSelectMultiple

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
    question_type=forms.ModelMultipleChoiceField(widget = forms.CheckboxSelectMultiple(), queryset = QuestionType.objects.all(),required=True)
    class Meta:
        model = Problem
        fields = ('tags','answer','latexanswer','difficulty','approval_status','question_type',)
    def __init__(self, *args, **kwargs):
        super(DetailedProblemForm, self).__init__(*args, **kwargs)   
        self.fields['tags'].queryset = Tag.objects.order_by('tag')

class ProblemTextForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ( 'problem_text','answer_choices',)
        widgets = { 'problem_text': forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'}),'answer_choices': forms.Textarea(attrs={'cols': 120, 'rows': 3,'id' : 'codetext'})}
    def __init__(self, *args, **kwargs):
        super(ProblemTextForm, self).__init__(*args, **kwargs)   
        self.fields['answer_choices'].help_text = '<br/><div class="tex2jax_ignore">Should be in the form<br/>$\\textbf{(A) } Ans A\\qquad \\textbf{(B) } Ans B\\qquad \\textbf{(C) } Ans C\\qquad \\textbf{(D) } Ans D\\qquad \\textbf{(E) } Ans E$</div>'

class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ('solution_text',)
        widgets = {
            'solution_text': forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'})
        }
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

