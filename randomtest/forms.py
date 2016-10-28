from django import forms
from django.contrib.auth.models import User
from randomtest.models import UserProfile,Test


class TestForm(forms.Form):
#    testchoices=(('AMC8','AMC 8 Problems'),('AMC10','AMC 10 Problems'),('AMC12','AMC 12 Problems'),('AIME','AIME Problems'),('USAMO','USAMO Problems'),('IMO','IMO Problems'),('Putnam','Putnam Problems'),('VTRMC','VTRMC Problems'))
#    testtype=forms.MultipleChoiceField(choices=testchoices,widget=forms.RadioSelect)
    tag=forms.CharField(label='Desired Tag',max_length=200)
    numproblems=forms.IntegerField(label='Number of Problems')
    probbegin=forms.IntegerField()
    probend=forms.IntegerField()
    yearbegin=forms.IntegerField()
    yearend=forms.IntegerField()

class TestModelForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ()

'''

class Test(models.Model):
    name = models.CharField(max_length=50)#Perhaps use a default naming scheme                                                                                                                              
    problems = models.ManyToManyField(Problem)
    answers = models.ManyToManyField(Answer,blank=True)
    num_problems_correct = models.IntegerField()
    types = models.ManyToManyField(Type)
    created_date = models.DateTimeField(default = timezone.now)
    last_attempted_date = models.DateTimeField(default = timezone.now)
    def __str__(self):
        return self.name
    def print_types(self):
        s = ''
        L = list(self.types.all())
        if len(L)>0:
            s = L[0].type
        for i in range(1,len(L)):
            s += ', '+L[i].type
        return s

'''

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ()
