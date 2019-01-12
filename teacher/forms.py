from django import forms
#from django.contrib.auth.models import User
from teacher.models import ProblemObject,TextBlock,Theorem,Proof,ExampleProblem,ProblemSet,Class,Unit,SlideGroup,Test,Slide,SolutionObject
from randomtest.utils import newtexcode,newsoltexcode,compileasy
from randomtest.models import NewTag

from django.contrib.admin.widgets import AdminDateWidget 

ANSWER_CHOICES = (
    ('A','Answer A'),
    ('B','Answer B'),
    ('C','Answer C'),
    ('D','Answer D'),
    ('E','Answer E'),
    )

THEOREMS = (
    ('Theorem','Theorem'),
    ('Corollary','Corollary'),
    ('Proposition','Proposition'),
    ('Lemma','Lemma'),
    ('Definition','Definition'),
    ('Example','Example'),
    ('Exercise','Exercise'),
    )

PROOFS = (
    ('Proof','Proof'),
    ('Solution','Solution'),
    )


class NewProblemObjectMCForm(forms.ModelForm):
    problem_id = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = ProblemObject
        fields = ('problem_code','answer_A','answer_B','answer_C','answer_D','answer_E','mc_answer',)
        widgets = {
            'problem_code': forms.Textarea(attrs={'style':'min-width: 100%', 'rows': 15,'id' : 'codetext','class':'form-control'}),
            'mc_answer': forms.RadioSelect(choices=ANSWER_CHOICES),
            'answer_A': forms.TextInput(attrs={'class':'form-control'}),
            'answer_B': forms.TextInput(attrs={'class':'form-control'}),
            'answer_C': forms.TextInput(attrs={'class':'form-control'}),
            'answer_D': forms.TextInput(attrs={'class':'form-control'}),
            'answer_E': forms.TextInput(attrs={'class':'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(NewProblemObjectMCForm, self).__init__(*args, **kwargs)
        self.fields['problem_code'].required = True
        self.fields['answer_A'].required = True
        self.fields['answer_B'].required = True
        self.fields['answer_C'].required = True
        self.fields['answer_D'].required = True
        self.fields['answer_E'].required = True
        self.fields['mc_answer'].required = True
        self.fields['mc_answer'].label = 'Answer'
        self.fields['problem_id'].initial = str(self.instance.pk)

class NewProblemObjectSAForm(forms.ModelForm):
    problem_id = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = ProblemObject
        fields = ('problem_code','sa_answer',)
        widgets = {
            'problem_code': forms.Textarea(attrs={'style':'min-width: 100%', 'rows': 15,'id' : 'codetext','class':'form-control'}),
            'sa_answer': forms.TextInput(attrs={'class':'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(NewProblemObjectSAForm, self).__init__(*args, **kwargs)
        self.fields['problem_code'].required = True
        self.fields['sa_answer'].required = True
        self.fields['sa_answer'].label = 'Answer'
        self.fields['problem_id'].initial = str(self.instance.pk)

class NewProblemObjectPFForm(forms.ModelForm):
    problem_id = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = ProblemObject
        fields = ('problem_code',)
        widgets = {
            'problem_code': forms.Textarea(attrs={'style':'min-width: 100%', 'rows': 15,'id' : 'codetext','class':'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(NewProblemObjectPFForm, self).__init__(*args, **kwargs)
        self.fields['problem_code'].required = True
        self.fields['problem_id'].initial = str(self.instance.pk)



class NewExampleProblemMCForm(forms.ModelForm):
    problem_id = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = ExampleProblem
        fields = ('problem_code','answer_A','answer_B','answer_C','answer_D','answer_E','mc_answer',)
        widgets = {
            'problem_code': forms.Textarea(attrs={'style':'min-width: 100%', 'rows': 15,'id' : 'codetext','class':'form-control'}),
            'mc_answer': forms.RadioSelect(choices=ANSWER_CHOICES),
            'answer_A': forms.TextInput(attrs={'class':'form-control'}),
            'answer_B': forms.TextInput(attrs={'class':'form-control'}),
            'answer_C': forms.TextInput(attrs={'class':'form-control'}),
            'answer_D': forms.TextInput(attrs={'class':'form-control'}),
            'answer_E': forms.TextInput(attrs={'class':'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(NewExampleProblemMCForm, self).__init__(*args, **kwargs)
        self.fields['problem_code'].required = True
        self.fields['answer_A'].required = True
        self.fields['answer_B'].required = True
        self.fields['answer_C'].required = True
        self.fields['answer_D'].required = True
        self.fields['answer_E'].required = True
        self.fields['mc_answer'].required = True
        self.fields['mc_answer'].label = 'Answer'
        self.fields['problem_id'].initial = str(self.instance.pk)

class NewExampleProblemSAForm(forms.ModelForm):
    problem_id = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = ExampleProblem
        fields = ('problem_code','sa_answer',)
        widgets = {
            'problem_code': forms.Textarea(attrs={'style':'min-width: 100%', 'rows': 15,'id' : 'codetext','class':'form-control'}),
            'sa_answer': forms.TextInput(attrs={'class':'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(NewExampleProblemSAForm, self).__init__(*args, **kwargs)
        self.fields['problem_code'].required = True
        self.fields['sa_answer'].required = True
        self.fields['sa_answer'].label = 'Answer'
        self.fields['problem_id'].initial = str(self.instance.pk)

class NewExampleProblemPFForm(forms.ModelForm):
    problem_id = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = ExampleProblem
        fields = ('problem_code',)
        widgets = {
            'problem_code': forms.Textarea(attrs={'style':'min-width: 100%', 'rows': 15,'id' : 'codetext','class':'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(NewExampleProblemPFForm, self).__init__(*args, **kwargs)
        self.fields['problem_code'].required = True
        self.fields['problem_id'].initial = str(self.instance.pk)




class PointValueForm(forms.ModelForm):
    class Meta:
        model = ProblemObject
        fields = ('point_value',)
        widgets = {
            'point_value': forms.NumberInput(attrs={'class' : 'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(PointValueForm, self).__init__(*args, **kwargs)
        self.fields['point_value'].required = True

class BlankPointValueForm(forms.ModelForm):
    class Meta:
        model = ProblemObject
        fields = ('blank_point_value',)
        widgets = {
            'blank_point_value': forms.NumberInput(attrs={'class' : 'form-control','step':'0.5'}),
            }
    def __init__(self, *args, **kwargs):
        super(BlankPointValueForm, self).__init__(*args, **kwargs)
        self.fields['blank_point_value'].required = True

class SearchForm(forms.Form):
    keywords = forms.CharField(max_length=128)
    contest_type = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}))
    desired_tag = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}))
    num_problems = forms.IntegerField()
    prob_num_low = forms.IntegerField()
    prob_num_high = forms.IntegerField()
    year_low = forms.IntegerField()
    year_high = forms.IntegerField()
    def __init__(self, userprofile=None, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['contest_type'].required = True
        user_choices = []
        for type in userprofile.user_type_new.allowed_types.all():
            user_choices.append((type.type,type.label))
        self.fields['desired_tag'].choices = user_choices

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


class TextBlockForm(forms.ModelForm):
    class Meta:
        model = TextBlock
        fields = ('text_code',)
        widgets = {
            'text_code': forms.Textarea(attrs={'style':'min-width: 100%', 'rows': 15,'id' : 'codetext','class':'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(TextBlockForm, self).__init__(*args, **kwargs)
    def save(self,commit=True):
        instance = super(TextBlockForm, self).save(commit=False)
        instance.text_display = newtexcode(instance.text_code,'textblock_'+str(instance.pk),"")
        if commit:
            instance.save()
        return instance

class TheoremForm(forms.ModelForm):
    class Meta:
        model = Theorem
        fields = ('prefix','name','theorem_code',)
        widgets = {
            'theorem_code': forms.Textarea(attrs={'style':'min-width: 100%', 'rows': 15,'id' : 'codetext','class':'form-control'}),
            'prefix': forms.Select(choices=THEOREMS, attrs={'class':'form-control'}),
            'name': forms.TextInput(attrs={'class':'form-control'}),
            }
    def __init__(self, *args, **kwargs):
        super(TheoremForm, self).__init__(*args, **kwargs)
        self.fields['name'].required=False
    def save(self,commit=True):
        instance = super(TheoremForm, self).save(commit=False)
        instance.theorem_display = newtexcode(instance.theorem_code,'theoremblock_'+str(instance.pk),"")
        if commit:
            instance.save()
        return instance

class ProofForm(forms.ModelForm):
    class Meta:
        model = Proof
        fields = ('prefix','proof_code',)
        widgets = {
            'proof_code': forms.Textarea(attrs={'style':'min-width: 100%', 'rows': 15,'id' : 'codetext','class':'form-control'}),
            'prefix': forms.Select(choices=PROOFS,attrs={'class':'form-control'})
            }
    def __init__(self, *args, **kwargs):
        super(ProofForm, self).__init__(*args, **kwargs)
    def save(self,commit=True):
        instance = super(ProofForm, self).save(commit=False)
        instance.proof_display = newtexcode(instance.proof_code,'proofblock_'+str(instance.pk),"")
        if commit:
            instance.save()
        return instance

class ImageForm(forms.Form):
    image = forms.ImageField()

class LabelForm(forms.Form):
    label = forms.CharField(max_length=50);


class EditClassNameForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            }
class EditUnitNameForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            }

class EditProblemSetNameForm(forms.ModelForm):
    class Meta:
        model = ProblemSet
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            }

class EditTestNameForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            }

class EditSlideGroupNameForm(forms.ModelForm):
    class Meta:
        model = SlideGroup
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            }


class EditSlideTitleForm(forms.ModelForm):
    class Meta:
        model = Slide
        fields = ('title',)
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            }


class NewSolutionObjectForm(forms.ModelForm):
    class Meta:
        model = SolutionObject
        fields = ('solution_code',)
        widgets = {
            'solution_code': forms.Textarea(attrs={"class":"form-control","min-width":"100%", 'rows': 15,'id' : 'codetext'})
        }
    def __init__(self,  *args, **kwargs):
        super(NewSolutionObjectForm, self).__init__(*args, **kwargs)
        self.fields['solution_code'].required = True
    def save(self,commit=True):
        instance = super(SolutionObjectForm, self).save(commit=False)
        instance.solution_display = newsoltexcode(instance.solution_code, 'publishedoriginalsolution_'+str(instance.pk))
        compileasy(instance.solution_code,'publishedoriginalsolution_'+str(instance.pk))
        if commit:
            instance.save()
        return instance

class EditSolutionObjectForm(forms.ModelForm):
    class Meta:
        model = SolutionObject
        fields = ('solution_code',)
        widgets = {
            'solution_code': forms.Textarea(attrs={"class":"form-control","min-width":"100%", 'rows': 15,'id' : 'codetext'})
        }
    def save(self,commit=True):
        instance = super(EditSolutionObjectForm, self).save(commit=False)
        instance.solution_display = newsoltexcode(instance.solution_code,'publishedoriginalsolution_'+str(instance.pk))
        compileasy(instance.solution_code,'publishedoriginalsolution_'+str(instance.pk))
        if commit:
            instance.save()
        return instance
