from django import forms
#from django.contrib.auth.models import User
from randomtest.models import Problem,Tag,Type,Solution
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

class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ('solution_text',)
        widgets = {
            'solution_text': forms.Textarea(attrs={'cols': 120, 'rows': 15,'id' : 'codetext'})
        }



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


'''
class ProjectPersonnelForm(forms.Form):
    class Media:
        # Django also includes a few javascript files necessary
        # for the operation of this form element. You need to
        # include <script src="/admin/jsi18n"></script>
        # in the template.
        css = {
            'all': ('admin/css/widgets.css',)
        }

    def __init__(self, *args, **kwargs):
        pid = kwargs.pop('pid')

        r = super(ProjectPersonnelForm, self).__init__(
            *args, **kwargs)

        p = Project.objects.get(pk=pid)
        qs = UserProfile.objects.filter(
            pk__in=[u.pk for u in p.all_users_not_in_project()]
        ).order_by(
            Lower('fullname')
        ).order_by(
            Lower('username'))

        self.fields['personnel'] = \
            forms.ModelMultipleChoiceField(
                queryset=qs,
                widget=FilteredSelectMultiple(
                    'Personnel', is_stacked=False),
                label='')

        return r
'''
