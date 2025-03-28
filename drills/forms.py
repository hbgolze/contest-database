from django import forms

from drills.models import DrillProblemSolution

from randomtest.utils import compileasy,newsoltexcode

class SolutionForm(forms.ModelForm):
    class Meta:
        model = DrillProblemSolution
        fields = ('solution_text',)
        widgets = {
            'solution_text': forms.Textarea(attrs={"class":"form-control","min-width":"100%", 'rows': 15,'id' : 'codetext'})
        }
    def save(self,commit=True):
        instance = super(SolutionForm, self).save(commit=False)
        instance.display_solution_text = newsoltexcode(instance.solution_text,instance.drill_problem.label+'drillsol'+str(instance.order))
        compileasy(instance.solution_text,instance.drill_problem.label,sol='drillsol'+str(instance.order))
        if commit:
            instance.save()
        return instance