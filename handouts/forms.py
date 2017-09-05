from django import forms
#from django.contrib.auth.models import User
from handouts.models import Section,SubSection,TextBlock,Proof,Theorem,Handout
from randomtest.utils import newtexcode


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

class HandoutForm(forms.ModelForm):
    class Meta:
        model = Handout
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            }
class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            }
class SubsectionForm(forms.ModelForm):
    class Meta:
        model = SubSection
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            }
class TextBlockForm(forms.ModelForm):
    class Meta:
        model = TextBlock
        fields = ('text_code',)
        widgets = {
            'text_code': forms.Textarea(attrs={'style':'min-width: 100%', 'rows': 15,'id' : 'codetext'}),
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
            'theorem_code': forms.Textarea(attrs={'style':'min-width: 100%', 'rows': 15,'id' : 'codetext'}),
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
            'proof_code': forms.Textarea(attrs={'style':'min-width: 100%', 'rows': 15,'id' : 'codetext'}),
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


