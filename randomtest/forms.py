from django import forms
from django.contrib.auth.models import User
from randomtest.models import UserProfile,Test

from django.contrib.auth.forms import AuthenticationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Field

from django.contrib.auth import REDIRECT_FIELD_NAME

#This form does not work yet...it does not redirect properly...
class LoginForm(AuthenticationForm):
    redirect_field_name = REDIRECT_FIELD_NAME
    redirect_field_value = ''
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        if ('redirect_field_name' in kwargs['initial'] and 'redirect_field_value' in kwargs['initial']):
            self.has_redirection = True
            self.redirect_field_name = kwargs['initial'].get('redirect_field_name')
            self.redirect_field_value = kwargs['initial'].get('redirect_field_value')

      ## dynamically add a field into form
            hidden_field = forms.CharField(widget=forms.HiddenInput())
            self.fields.update({
                    self.redirect_field_name: hidden_field
                    })

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            ButtonHolder(
                Submit('login', 'Login', css_class='btn-primary')
            ),
            Field(
                self.redirect_field_name,
                type='hidden',
                value=redirect_field_value
                )
        )



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
        fields = ('time_zone',)
        widgets = {
            'time_zone': forms.Select(attrs={"class":"form-control"})
            }
