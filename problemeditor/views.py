from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.template import loader,RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from formtools.wizard.views import SessionWizardView

from randomtest.models import Problem, Tag, Type, Test, UserProfile, Solution,Dropboxurl,Comment,QuestionType,ProblemApproval
from .forms import ProblemForm,SolutionForm,ProblemTextForm,AddProblemForm,DetailedProblemForm,CommentForm,ApprovalForm
from randomtest.utils import goodtag,goodurl,newtexcode



def show_mc_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type')==QuestionType.objects.get(question_type='multiple choice')

def show_sa_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type')==QuestionType.objects.get(question_type='short answer')

def show_pf_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type')==QuestionType.objects.get(question_type='proof')

def show_mcsa_form_condition(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type')==QuestionType.objects.get(question_type='multiple choice short answer')

def show_mc_form_condition2(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type_new')==QuestionType.objects.get(question_type='multiple choice')

def show_sa_form_condition2(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type_new')==QuestionType.objects.get(question_type='short answer')

def show_pf_form_condition2(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type_new')==QuestionType.objects.get(question_type='proof')

def show_mcsa_form_condition2(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    return cleaned_data.get('question_type_new')==QuestionType.objects.get(question_type='multiple choice short answer')

class AddProblemWizard(SessionWizardView):
    template_name='problemeditor/addviewwizard.html'
    def get_context_data(self, **kwargs):
        ctx = super(AddProblemWizard, self).get_context_data(**kwargs)
        ctx['ctx'] = ctx
        ctx['nbar']= 'problemeditor'
        if self.storage.current_step=='5':
            qt=QuestionType.objects.get(pk=self.storage.get_step_data('0').get('0-question_type')) 
            if qt.question_type=='multiple choice':
                ctx['mc']=True
            if qt.question_type=='short answer':
                ctx['sa']=True
            if qt.question_type=='proof':
                ctx['pf']=True
            if qt.question_type=='multiple choice short answer':
                ctx['mcsa']=True
        if 'problem_text' in self.get_form_initial('1'):
            ctx['problem_text']=self.get_form_initial('1')['problem_text']
        if 'mc_problem_text' in self.get_form_initial('1'):
            ctx['mc_problem_text']=self.get_form_initial('1')['mc_problem_text']
        return ctx
    def get_form_initial(self, step):
        # steps are named 'step1', 'step2', 'step3'
        current_step = self.storage.current_step
        
        # get the data for step 1 on step 3
        if current_step == '5':#CHANGE THIS
            init_data = self.storage.get_step_data('0')
            qtype = init_data.get('0-question_type')
            q=QuestionType.objects.get(pk=qtype)
            if q.question_type=='multiple choice':
                prev_data = self.storage.get_step_data('1')
                some_var = prev_data.get('1-mc_problem_text','')+'\n\n'+'$\\textbf{(A) }'+prev_data.get('1-answer_A','')+'\\qquad \\textbf{(B) }'+prev_data.get('1-answer_B','')+'\\qquad \\textbf{(C) }'+prev_data.get('1-answer_C','')+'\\qquad \\textbf{(D) }'+prev_data.get('1-answer_D','')+'\\qquad \\textbf{(E) }'+prev_data.get('1-answer_E','')+'$\n\n'
                return self.initial_dict.get(step, {'mc_problem_text': some_var})
            elif q.question_type=='short answer':
                prev_data = self.storage.get_step_data('2')
                some_var = prev_data.get('2-problem_text','')
                return self.initial_dict.get(step, {'problem_text': some_var})
            elif q.question_type=='proof':
                prev_data = self.storage.get_step_data('3')
                some_var = prev_data.get('3-problem_text','')
                return self.initial_dict.get(step, {'problem_text': some_var})
            elif q.question_type=='multiple choice short answer':
                prev_data = self.storage.get_step_data('4')
                some_var = prev_data.get('4-mc_problem_text','')
                some_var1 = prev_data.get('4-problem_text','')
                return self.initial_dict.get(step, {'mc_problem_text': some_var,'problem_text': some_var1})
        return self.initial_dict.get(step, {})
    def done(self,form_list,**kwargs):
        D={}
        for form in form_list:
            x=form.cleaned_data
            for i in x:
                D[i]=x[i]
        if D['question_type'].question_type == 'short answer':
            prob = Problem(
                problem_text=D['problem_text'],
                author_name=D['author_name'],
                answer=D['correct_short_answer_answer'],
                sa_answer=D['correct_short_answer_answer'],
                type_new=D['type'],
                question_type_new=D['question_type'],
                )
        elif D['question_type'].question_type == 'proof':
            prob = Problem(
                problem_text=D['problem_text'],
                author_name=D['author_name'],
                type_new=D['type'],
                question_type_new=D['question_type'],
                )
        elif D['question_type'].question_type == 'multiple choice':
            prob = Problem(
                mc_problem_text=D['mc_problem_text'],
                author_name=D['author_name'],
                answer=D['correct_multiple_choice_answer'],
                mc_answer=D['correct_multiple_choice_answer'],
                answer_choices='$\\textbf{(A) }'+D['answer_A']+'\\qquad\\textbf{(B) }'+D['answer_B']+'\\qquad\\textbf{(C) }'+D['answer_C']+'\\qquad\\textbf{(D) }'+D['answer_D']+'\\qquad\\textbf{(E) }'+D['answer_E']+'$',
                answer_A=D['answer_A'],
                answer_B=D['answer_B'],
                answer_C=D['answer_C'],
                answer_D=D['answer_D'],
                answer_E=D['answer_E'],
                type_new=D['type'],
                question_type_new=D['question_type'],
                )
        elif D['question_type'].question_type == 'multiple choice short answer':
            prob = Problem(
                problem_text=D['problem_text'],
                mc_problem_text=D['mc_problem_text'],
                author_name=D['author_name'],
                answer=D['correct_multiple_choice_answer'],
                mc_answer=D['correct_multiple_choice_answer'],
                answer_choices='$\\textbf{(A) }'+D['answer_A']+'\\qquad\\textbf{(B) }'+D['answer_B']+'\\qquad\\textbf{(C) }'+D['answer_C']+'\\qquad\\textbf{(D) }'+D['answer_D']+'\\qquad\\textbf{(E) }'+D['answer_E']+'$',
                answer_A=D['answer_A'],
                answer_B=D['answer_B'],
                answer_C=D['answer_C'],
                answer_D=D['answer_D'],
                answer_E=D['answer_E'],
                type_new=D['type'],
                question_type_new=D['question_type'],
                )
        prob.save()
        prob.question_type.add(D['question_type'])
        prob.types.add(D['type'])
        prob.author=self.request.user
        t=prob.type_new
        t.top_index+=1
        t.save()
        prob.label = t.type+str(t.top_index)
        prob.readable_label = t.type+' '+str(t.top_index)
        prob.save()
        sol=Solution(solution_text = D['solution_text'])
        sol.save()
        sol.solution_number=1
        sol.authors.add(self.request.user)
        sol.problem_label=prob.label
        sol.save()
        prob.solutions.add(sol)
        prob.save()
        return redirect('/problemeditor/detailedview/'+str(prob.pk)+'/')

#{'1':show_mc_form_condition2,'2':show_sa_form_condition2,'3':show_pf\
#_form_condition2,'4':show_mcsa_form_condition2,})),

CQTTEMPLATES = {
    "0": "problemeditor/changequestiontypewizard.html",
    "1": "problemeditor/changequestiontypewizardmc.html",
    "2": "problemeditor/changequestiontypewizardsa.html",
    "3": "problemeditor/changequestiontypewizardpf.html",
    "4": "problemeditor/changequestiontypewizardmcsa.html",
    }
class ChangeQuestionTypeWizard(SessionWizardView):
#    template_name='problemeditor/changequestiontypewizard.html'
    instance=None
    def get_context_data(self, **kwargs):
        ctx = super(ChangeQuestionTypeWizard, self).get_context_data(**kwargs)
        ctx['ctx'] = ctx
        ctx['nbar']= 'problemeditor'
        breadcrumbs=[]
        prob=get_object_or_404(Problem,pk=self.kwargs['pk'])
        if 'tagstatus' in self.kwargs:
            if self.kwargs['tagstatus']=='untagged':
                breadcrumbs=[
                    ('../../',prob.type_new.label),
                    ('../','untagged'),
                    ('.',str(prob.readable_label)),
                    ]
            else:
                raise Http404("Bad URL")
        elif 'type' in self.kwargs:
            breadcrumbs=[('../',prob.type_new.label+' Problems'),('.',str(prob.readable_label))]
        ctx['breadcrumbs']=breadcrumbs
        return ctx
    def get_template_names(self):
        return [CQTTEMPLATES[self.steps.current]]
    def get_form_initial(self, step):
        if 'pk' in self.kwargs:
            return {}
        return self.initial_dict.get(step, {})
    def get_form_instance(self, step):
        if self.instance is None:
            if 'pk' in self.kwargs:
                pk = self.kwargs['pk']
                self.instance = get_object_or_404(Problem,pk=pk)
            else:
                self.instance = Problem()
        return self.instance
    def get_form(self, step=None, data=None, files=None):
#        print('get_form')
        form = super(ChangeQuestionTypeWizard, self).get_form(step, data, files)
        if step == '1' or step == '2' or step == '3' or step == '4':
            prev_data = self.storage.get_step_data('0')
            question_type = prev_data.get('0-question_type_new', '')
            form.fields['question_type_new'].initial = question_type
        return form
    def done(self,form_list,**kwargs):
        self.instance.question_type_new = QuestionType.objects.get(pk=self.storage.get_step_data('0').get('0-question_type_new', ''))
        self.instance.save()
        return redirect('.')
#        return redirect('/problemeditor/detailedview/'+str(self.instance.pk)+'/')



# Create your views here.
@login_required
def typeview(request):
    obj=list(Type.objects.all().exclude(type__startswith="CM"))
    obj=sorted(obj,key=lambda x:x.type)
    rows=[]
    for i in range(0,len(obj)):
#        P = Problem.objects.filter(types__in=[obj[i]])
        P = Problem.objects.filter(type_new=obj[i])
        num_problems = P.count()
        untagged = P.filter(tags__isnull=True)
        num_untagged = untagged.count()
        nosolutions = P.filter(solutions__isnull=True)
        num_nosolutions = nosolutions.count()
        rows.append((obj[i].type,obj[i].label,num_untagged,num_nosolutions,num_problems))
    obj2=list(Type.objects.filter(type__startswith="CM"))
    obj2=sorted(obj2,key=lambda x:x.type)
    rows2=[]
    for i in range(0,len(obj2)):
#        P = Problem.objects.filter(types__in=[obj2[i]])
        P = Problem.objects.filter(type_new=obj2[i])
        num_problems = P.count()
        untagged = P.filter(tags__isnull=True)
        num_untagged = untagged.count()
        nosolutions = P.filter(solutions__isnull=True)
        num_nosolutions = nosolutions.count()
        rows2.append((obj2[i].type,obj2[i].label,num_untagged,num_nosolutions,num_problems))
    template=loader.get_template('problemeditor/typeview.html')
#    tests=list(UserProfile.objects.get(user=request.user).tests.all())
    context= {'rows': rows, 'nbar': 'problemeditor','rows2':rows2}
    return HttpResponse(template.render(context,request))

@login_required
def tagview(request,type):
    typ=get_object_or_404(Type, type=type)
    obj=list(Tag.objects.all())
    obj=sorted(obj,key=lambda x:x.tag)
    rows=[]
#    probsoftype=Problem.objects.filter(types__in=[typ])
    probsoftype=Problem.objects.filter(type_new=typ)
    untagged=probsoftype.filter(tags__isnull=True)
    num_untagged = untagged.count()
    testlabels=[]
    pot=list(probsoftype)
    for i in range(0,len(pot)):
        testlabels.append(pot[i].test_label)
    testlabels=list(set(testlabels))
    testlabels.sort()
    for i in range(0,len(obj)):
        T = probsoftype.filter(tags__in=[obj[i]])
        num_problems=T.count()
        nosolutions = T.filter(solutions__isnull=True)
        num_nosolutions = nosolutions.count()
        if num_problems>0:
            rows.append((goodurl(str(obj[i])),str(obj[i]),num_nosolutions,num_problems))
    template=loader.get_template('problemeditor/tagview.html')
    context= {'rows': rows, 'type' : typ.type, 'typelabel':typ.label,'num_untagged': num_untagged, 'nbar': 'problemeditor','prefix':'bytag'}
    return HttpResponse(template.render(context,request))

@login_required
def CMtagview(request,type):
    typ=get_object_or_404(Type, type=type)
    obj=list(Tag.objects.all())
    obj=sorted(obj,key=lambda x:x.tag)
    rows=[]
#    probsoftype=Problem.objects.filter(types__in=[typ])
    probsoftype=Problem.objects.filter(type_new=typ)
    untagged=probsoftype.filter(tags__isnull=True)
    num_untagged = untagged.count()
    testlabels=[]
    pot=list(probsoftype)
    for i in range(0,len(pot)):
        testlabels.append(pot[i].test_label)
    testlabels=list(set(testlabels))
    testlabels.sort()
    for i in range(0,len(obj)):
        T = probsoftype.filter(tags__in=[obj[i]])
        num_problems=T.count()
        nosolutions = T.filter(solutions__isnull=True)
        num_nosolutions = nosolutions.count()
        if num_problems>0:
            rows.append((goodurl(str(obj[i])),str(obj[i]),num_nosolutions,num_problems))
    template=loader.get_template('problemeditor/CMtagview.html')
    context= {'rows': rows, 'type' : typ.type, 'typelabel':typ.label,'num_untagged': num_untagged, 'nbar': 'problemeditor','prefix':'CMbytag'}
    return HttpResponse(template.render(context,request))

@login_required
def testview(request,type):
    typ=get_object_or_404(Type, type=type)
#    probsoftype=Problem.objects.filter(types__in=[typ])
    probsoftype=Problem.objects.filter(type_new=typ)
    untagged=probsoftype.filter(tags__isnull=True)
    num_untagged = untagged.count()
    testlabels=[]
    pot=list(probsoftype)
    for i in range(0,len(pot)):
        testlabels.append(pot[i].test_label)
    testlabels=list(set(testlabels))
    testlabels.sort()
    rows2=[]
    for i in range(0,len(testlabels)):
        rows2.append((testlabels[i],probsoftype.filter(test_label=testlabels[i]).filter(tags__isnull=True).count(),probsoftype.filter(test_label=testlabels[i]).filter(solutions__isnull=True).count(),probsoftype.filter(test_label=testlabels[i]).count()))
    template=loader.get_template('problemeditor/testview.html')
    context= { 'type' : typ.type, 'typelabel':typ.label,'num_untagged': num_untagged, 'nbar': 'problemeditor','rows2':rows2,'prefix':'bytest'}
    return HttpResponse(template.render(context,request))

@login_required
def typetagview(request,type,tag):
    tag=goodtag(tag)
    typ=get_object_or_404(Type, type=type)
    rows=[]
    if tag!='untagged':
        ttag=get_object_or_404(Tag, tag=tag)
#        problems=list(Problem.objects.filter(types__in=[typ]).filter(tags__in=[ttag]))
        problems=list(Problem.objects.filter(type_new=typ).filter(tags__in=[ttag]))
    else:
#        problems=list(Problem.objects.filter(types__in=[typ]).filter(tags__isnull=True))
        problems=list(Problem.objects.filter(type_new=typ).filter(tags__isnull=True))
    problems=sorted(problems, key=lambda x:(x.year,x.problem_number))
    for i in range(0,len(problems)):
        num_solutions=problems[i].solutions.count()
        rows.append((problems[i].label,problems[i].print_tags(),num_solutions))
    template=loader.get_template('problemeditor/typetagview.html')
    context= {'rows' : rows, 'type' : typ.type, 'nbar': 'problemeditor','tag':tag,'typelabel':typ.label}
    return HttpResponse(template.render(context,request))

@login_required
def CMtypetagview(request,type,tag):
    tag=goodtag(tag)
    typ=get_object_or_404(Type, type=type)
    rows=[]
    if tag!='untagged':
        ttag=get_object_or_404(Tag, tag=tag)
#        problems=list(Problem.objects.filter(types__in=[typ]).filter(tags__in=[ttag]))
        problems=list(Problem.objects.filter(type_new=typ).filter(tags__in=[ttag]))
    else:
#        problems=list(Problem.objects.filter(types__in=[typ]).filter(tags__isnull=True))
        problems=list(Problem.objects.filter(type_new=typ).filter(tags__isnull=True))
    problems=sorted(problems, key=lambda x:x.pk)
    for i in range(0,len(problems)):
        num_solutions=problems[i].solutions.count()
        rows.append((problems[i].label,problems[i].print_tags(),num_solutions,problems[i].pk))
    template=loader.get_template('problemeditor/CMtypetagview.html')
    context= {'rows' : rows, 'type' : typ.type, 'nbar': 'problemeditor','tag':tag,'typelabel':typ.label}
    return HttpResponse(template.render(context,request))

@login_required
def testlabelview(request,type,testlabel):
    typ=get_object_or_404(Type, type=type)
    rows=[]
    if testlabel!='untagged':
        problems=list(Problem.objects.filter(test_label=testlabel))
    else:
#        problems=list(Problem.objects.filter(types__in=[typ]).filter(tags__isnull=True))
        problems=list(Problem.objects.filter(type_new=typ).filter(tags__isnull=True))
    problems=sorted(problems, key=lambda x:(x.year,x.problem_number))
    for i in range(0,len(problems)):
        num_solutions=problems[i].solutions.count()
        rows.append((problems[i].label,problems[i].print_tags(),num_solutions))
    template=loader.get_template('problemeditor/typetagview.html')
    context= {'rows' : rows, 'type': typ.type, 'nbar': 'problemeditor','type':typ.type,'typelabel':typ.label,'tag':testlabel}
    return HttpResponse(template.render(context,request))

@login_required
def CMtopicview(request,type):#unapprovedview
    typ=get_object_or_404(Type, type=type)
    rows=[]
#    problems=list(Problem.objects.filter(types__in=[typ]).filter(approval_status=False))
#    problems=list(Problem.objects.filter(type_new=typ).filter(approval_status=False))
    problems=list(Problem.objects.filter(type_new=typ))
    problems=sorted(problems, key=lambda x:(x.pk))
    for i in range(0,len(problems)):
        num_solutions=problems[i].solutions.count()
        rows.append((problems[i].label,problems[i].print_tags(),num_solutions,problems[i].pk,problems[i].approvals.all()))
    template=loader.get_template('problemeditor/CMtopicview.html')#unapproved
    context= {'rows' : rows, 'type' : typ.type, 'nbar': 'problemeditor','typelabel':typ.label}
    return HttpResponse(template.render(context,request))

@login_required
def problemview(request,type,tag,label):
    tag=goodtag(tag)
    typ=get_object_or_404(Type, type=type)
    prob=get_object_or_404(Problem, label=label)
    tags=Tag.objects.all()
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        form = ProblemForm(request.POST, instance=prob)
        if form.is_valid():
            problem = form.save()
            problem.save()
    else:
        form = ProblemForm(instance=prob)
    texcode=newtexcode(form.instance.problem_text,dropboxpath,label,prob.answer_choices)
    readablelabel=form.instance.readable_label.replace('\\#','#')

    context={}
    if prob.question_type_new.question_type=='multiple choice':
        mc_texcode=newtexcode(prob.mc_problem_text,dropboxpath,prob.label,prob.answers())
        context['mc_prob_latex']=mc_texcode
        context['mc']=True
    elif prob.question_type_new.question_type=='short answer':
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['sa']=True
    elif prob.question_type_new.question_type=='proof':
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['pf']=True
    elif prob.question_type_new.question_type=='multiple choice short answer':
        mc_texcode=newtexcode(prob.mc_problem_text,dropboxpath,prob.label,prob.answers())
        context['mc_prob_latex']=mc_texcode
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['mcsa']=True
#    context['rows']=rows
    context['form']=form
    context['nbar']='problemeditor'
    context['dropboxpath']=dropboxpath
    context['typelabel']= typ.label
    context['label'] = label
    context['tag'] = tag
    context['readablelabel']=readablelabel

    return render(request, 'problemeditor/view.html', context)

@login_required
def editproblemtextview(request,type,tag,label):
    tag=goodtag(tag)
    typ=get_object_or_404(Type, type=type)
    prob=get_object_or_404(Problem, label=label)
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        form = ProblemTextForm(request.POST, instance=prob)
        if form.is_valid():
            problem = form.save()
            problem.save()
        return redirect('../')
    else:
        form = ProblemTextForm(instance=prob)
    texcode=newtexcode(form.instance.problem_text,dropboxpath,label,prob.answer_choices)
    readablelabel=form.instance.readable_label.replace('\\#','#')
    breadcrumbs=[('/problemeditor/','Select Type'),('../../../',typ.label),('../../',tag),('../',readablelabel),]

    context={}
    if prob.question_type_new.question_type=='multiple choice':
        mc_texcode=newtexcode(prob.mc_problem_text,dropboxpath,prob.label,prob.answers())
        context['mc_prob_latex']=mc_texcode
        context['mc']=True
    elif prob.question_type_new.question_type=='short answer':
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['sa']=True
    elif prob.question_type_new.question_type=='proof':
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['pf']=True
    elif prob.question_type_new.question_type=='multiple choice short answer':
        mc_texcode=newtexcode(prob.mc_problem_text,dropboxpath,prob.label,prob.answers())
        context['mc_prob_latex']=mc_texcode
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['mcsa']=True
#    context['rows']=rows
    context['nbar']='problemeditor'
    context['dropboxpath']=dropboxpath
    context['readablelabel']=readablelabel
    context['form']=form
    context['breadcrumbs']=breadcrumbs
    context['typelabel']= typ.label
    context['label'] = label
    context['tag'] = tag
    return render(request, 'problemeditor/editproblemtext.html', context)

@login_required
def editproblemtextpkview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('/problemeditor/','Select Type'),('../../../',typ.label),('../../',kwargs['tag']),('../',str(prob.readable_label))]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('/problemeditor/','Select Type'),('../../',typ.label+' Problems'),('../',str(prob.readable_label))]
    else:
        breadcrumbs=[('/problemeditor/','Select Type'),('../',str(prob.readable_label)),]
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        form = ProblemTextForm(request.POST, instance=prob)
        if form.is_valid():
            problem = form.save()
            problem.save()
        return redirect('../')
    else:
        form = ProblemTextForm(instance=prob)
    print(prob.answer_choices)
    texcode=newtexcode(form.instance.problem_text,dropboxpath,prob.label,prob.answer_choices)
    readablelabel=form.instance.readable_label.replace('\\#','#')
    context={}
    if prob.question_type_new.question_type=='multiple choice':
        mc_texcode=newtexcode(prob.mc_problem_text,dropboxpath,prob.label,prob.answers())
        context['mc_prob_latex']=mc_texcode
        context['mc']=True
    elif prob.question_type_new.question_type=='short answer':
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['sa']=True
    elif prob.question_type_new.question_type=='proof':
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['pf']=True
    elif prob.question_type_new.question_type=='multiple choice short answer':
        mc_texcode=newtexcode(prob.mc_problem_text,dropboxpath,prob.label,prob.answers())
        context['mc_prob_latex']=mc_texcode
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['mcsa']=True
    context['nbar']='problemeditor'
    context['dropboxpath']=dropboxpath
    context['readablelabel']=readablelabel
    context['form']=form
    context['breadcrumbs']=breadcrumbs

    return render(request, 'problemeditor/editproblemtext.html', context)


@login_required
def solutionview(request,type,tag,label):
    tag=goodtag(tag)
    typ=get_object_or_404(Type, type=type)
    prob=get_object_or_404(Problem, label=label)
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    sols=list(prob.solutions.all())
    sollist=[]
    rows=[]
    for sol in sols:
        rows.append((sol.solution_text,sol.pk))
#    texcode=newtexcode(prob.problem_text,dropboxpath,label,prob.answer_choices)
    readablelabel=prob.readable_label.replace('\\#','#')

    context={}
    if prob.question_type_new.question_type=='multiple choice':
        mc_texcode=newtexcode(prob.mc_problem_text,dropboxpath,prob.label,prob.answers())
        context['mc_prob_latex']=mc_texcode
        context['mc']=True
        context['mc_answer']=prob.mc_answer
    elif prob.question_type_new.question_type=='short answer':
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['sa']=True
        context['sa_answer']=prob.sa_answer
    elif prob.question_type_new.question_type=='proof':
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['pf']=True
    elif prob.question_type_new.question_type=='multiple choice short answer':
        mc_texcode=newtexcode(prob.mc_problem_text,dropboxpath,prob.label,prob.answers())
        context['mc_prob_latex']=mc_texcode
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['mcsa']=True
        context['mc_answer']=prob.mc_answer
        context['sa_answer']=prob.sa_answer
    context['rows']=rows
    context['label'] = label
    context['nbar']='problemeditor'
    context['dropboxpath']=dropboxpath
    context['typelabel']= typ.label
    context['tag'] = tag
    context['readablelabel']=readablelabel

    return render(request, 'problemeditor/solview.html', context)

@login_required
def newsolutionview(request,type,tag,label):
    tag=goodtag(tag)
    typ=get_object_or_404(Type, type=type)
    prob=get_object_or_404(Problem, label=label)
    sol_num=prob.solutions.count()+1
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        sol_form = SolutionForm(request.POST)
        if sol_form.is_valid():
            sol = sol_form.save()
            sol.solution_number=sol_num
            sol.authors.add(request.user)
            sol.problem_label=label
            sol.save()
            prob.solutions.add(sol)
            prob.save()
        return redirect('../')#solutionview,type=type,tag=tag,label=label)
    else:
        sol=Solution(solution_text='', solution_number=sol_num, problem_label=label)
        form = SolutionForm(instance=sol)
    readablelabel=prob.readable_label.replace('\\#','#')
    breadcrumbs=[('../../../../',typ.label),('../../../',tag),('../','Solutions to '+readablelabel),]

    context={}
    if prob.question_type_new.question_type=='multiple choice':
        mc_texcode=newtexcode(prob.mc_problem_text,dropboxpath,prob.label,prob.answers())
        context['mc_prob_latex']=mc_texcode
        context['mc']=True
        context['mc_answer']=prob.mc_answer
    elif prob.question_type_new.question_type=='short answer':
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['sa']=True
        context['sa_answer']=prob.sa_answer
    elif prob.question_type_new.question_type=='proof':
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['pf']=True
    elif prob.question_type_new.question_type=='multiple choice short answer':
        mc_texcode=newtexcode(prob.mc_problem_text,dropboxpath,prob.label,prob.answers())
        context['mc_prob_latex']=mc_texcode
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['mcsa']=True
        context['mc_answer']=prob.mc_answer
        context['sa_answer']=prob.sa_answer
    context['form']=form
    context['label'] = label
    context['nbar']='problemeditor'
    context['dropboxpath']=dropboxpath
    context['typelabel']= typ.label
    context['tag'] = tag
    context['readablelabel']=readablelabel
    context['breadcrumbs']=breadcrumbs

    return render(request, 'problemeditor/newsol.html', context)

@login_required
def newsolutionpkview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../../',typ.label),('../../',kwargs['tag']),('../',str(prob.readable_label))]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../',typ.label+' Problems'),('../',prob.readable_label)]
    else:
        breadcrumbs=[('../',prob.readable_label),]
    sol_num=prob.solutions.count()+1
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        sol_form = SolutionForm(request.POST)
        if sol_form.is_valid():
            sol = sol_form.save()
            sol.solution_number=sol_num
            sol.authors.add(request.user)
            sol.problem_label=prob.label
            sol.save()
            prob.solutions.add(sol)
            prob.save()
        return redirect('../')#detailedproblemview,pk=pk)
    else:
        sol=Solution(solution_text='', solution_number=sol_num, problem_label=prob.label)
        form = SolutionForm(instance=sol)

    texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
    readablelabel=prob.readable_label.replace('\\#','#')
#    breadcrumbs=[('../',prob.label),]
    return render(request, 'problemeditor/newsol.html', {'form': form, 'nbar': 'problemeditor','dropboxpath':dropboxpath,'answer':prob.answer, 'prob_latex':texcode,'readablelabel':readablelabel,'breadcrumbs':breadcrumbs})

@login_required
def editsolutionview(request,type,tag,label,spk):
    tag=goodtag(tag)
    typ=get_object_or_404(Type, type=type)
    prob=get_object_or_404(Problem, label=label)
    sol=Solution.objects.get(pk=spk)
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        if request.POST.get("save"):
            sollist=request.POST.getlist('solution_text')
            sol.solution_text=sollist[0]
            sol.authors.add(request.user)
            sol.save()
            return redirect(solutionview,type=type,tag=tag,label=label)
    form = SolutionForm(instance=sol)

    texcode=newtexcode(prob.problem_text,dropboxpath,label,prob.answer_choices)
    readablelabel=prob.readable_label.replace('\\#','#')
    breadcrumbs=[('../../../../../',typ.label),('../../../../',tag),('../../','Solutions to '+readablelabel),]
    return render(request, 'problemeditor/editsol.html', {'form': form, 'nbar': 'problemeditor','dropboxpath':dropboxpath,'typelabel':typ.label,'tag':tag,'label':label,'answer':prob.answer, 'solution_text':sol.solution_text, 'prob_latex':texcode,'readablelabel':readablelabel,'breadcrumbs':breadcrumbs})

@login_required
def editsolutionpkview(request,**kwargs):
    pk=kwargs['pk']
    spk=kwargs['spk']
    prob=get_object_or_404(Problem, pk=pk)
    sol=Solution.objects.get(pk=spk)
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../../../',typ.label),('../../../',kwargs['tag']),('../../',str(prob.readable_label))]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../../',typ.label+' Problems'),('../../',prob.readable_label),]
    else:
        breadcrumbs=[('../../','Solutions to '+prob.readable_label),]
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        if request.POST.get("save"):
            sollist=request.POST.getlist('solution_text')
            sol.solution_text=sollist[0]
            sol.authors.add(request.user)
            sol.save()
            return redirect('../../')#detailedproblemview,pk=pk)
    form = SolutionForm(instance=sol)

    texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
    readablelabel=prob.readable_label.replace('\\#','#')
    return render(request, 'problemeditor/editsol.html', {'form': form, 'nbar': 'problemeditor','dropboxpath':dropboxpath,'answer':prob.answer, 'solution_text':sol.solution_text, 'prob_latex':texcode,'readablelabel':readablelabel,'breadcrumbs':breadcrumbs})

@login_required
def editreviewpkview(request,**kwargs):
    pk=kwargs['pk']
    apk=kwargs['apk']
    prob=get_object_or_404(Problem, pk=pk)
    appr=ProblemApproval.objects.get(pk=apk)
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../../../',typ.label),('../../../',kwargs['tag']),('../../',str(prob.readable_label))]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../../',typ.label+' Problems'),('../../',prob.readable_label),]
    else:
        breadcrumbs=[('../../','Solutions to '+prob.readable_label),]
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        if request.POST.get("save"):
            appr_form = ApprovalForm(request.POST,instance=appr)
#            print(appr_form)
            if appr_form.is_valid():
                appr2 = appr_form.save()
                appr2.save()
#                appr.approval_user = request.user
#                appr.author_name=appr_form.author_name
#                print(appr_form)
#                appr.approval_status=request.POST.get('approval_status')#appr_form.approval_status
#                appr.save()
            return redirect('../../')#detailedproblemview,pk=pk)
    form = ApprovalForm(instance=appr)
    texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
    readablelabel=prob.readable_label.replace('\\#','#')
    return render(request, 'problemeditor/editappr.html', {'form': form, 'nbar': 'problemeditor','dropboxpath':dropboxpath, 'prob_latex':texcode,'readablelabel':readablelabel,'breadcrumbs':breadcrumbs})


@login_required
def deletesolutionview(request,type,tag,label,spk):#If solution_number is kept, this must be modified to adjust.
    sol = get_object_or_404(Solution, pk=spk)
    sol.delete()
    return redirect('../../')

@login_required
def deletesolutionpkview(request,**kwargs):#If solution_number is kept, this must be modified to adjust.
    pk=kwargs['pk']
    spk=kwargs['spk']
    sol = get_object_or_404(Solution, pk=spk)
    sol.delete()
    return redirect('../../')

@login_required
def deletecommentpkview(request,**kwargs):#If solution_number is kept, this must be modified to adjust.
    pk=kwargs['pk']
    cpk=kwargs['cpk']
    com = get_object_or_404(Comment, pk=cpk)
    com.delete()
    return redirect('../../')

@login_required
def untaggedview(request,type):
    typ=get_object_or_404(Type, type=type)
    rows=[]
#    problems=list(Problem.objects.filter(types__in=[typ]).filter(tags__isnull=True))
    problems=list(Problem.objects.filter(type_new=typ).filter(tags__isnull=True))
    problems=sorted(problems, key=lambda x:(x.year,x.problem_number))
    for i in range(0,len(problems)):
        num_solutions=problems[i].solutions.count()
        rows.append((problems[i].label,problems[i].print_tags(),num_solutions))
    template=loader.get_template('problemeditor/typetagview.html')
    context= {'rows' : rows, 'type' : typ.type, 'nbar': 'problemeditor'}
    return HttpResponse(template.render(context,request))

@login_required
def newcommentpkview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../../',typ.label),('../../',kwargs['tag']),('../',str(prob.readable_label))]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../',typ.label+' Problems'),('../',prob.readable_label),]
    else:
        breadcrumbs=[('../',prob.readable_label),]

    com_num=prob.comments.count()+1
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        com_form = CommentForm(request.POST)
        if com_form.is_valid():
            com = com_form.save(commit=False)
            com.comment_number=com_num
            com.author = request.user
            com.problem_label=prob.label
            com.save()
            prob.comments.add(com)
            prob.save()
            return redirect('../')
    else:
        com=Comment(comment_text='', comment_number=com_num, problem_label=prob.label)
        com_form = CommentForm(instance=com)

    return render(request, 'problemeditor/newcom.html', {'form': com_form, 'nbar': 'problemeditor','dropboxpath':dropboxpath,'breadcrumbs':breadcrumbs,'label':prob.readable_label})

@login_required
def newreviewpkview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../../',typ.label),('../../',kwargs['tag']),('../',str(prob.readable_label))]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../',typ.label+' Problems'),('../',prob.readable_label),]
    else:
        breadcrumbs=[('../',prob.readable_label),]

    dropboxpath=list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        appr_form = ApprovalForm(request.POST)
        if appr_form.is_valid():
            appr = appr_form.save(commit=False)
            appr.approval_user = request.user
#            com.problem_label=prob.label
            appr.save()
            prob.approvals.add(appr)
            prob.save()
            return redirect('../')
    else:
        appr=ProblemApproval()
        appr_form = ApprovalForm(instance=appr)

    return render(request, 'problemeditor/newappr.html', {'form': appr_form, 'nbar': 'problemeditor','dropboxpath':dropboxpath,'breadcrumbs':breadcrumbs,'label':prob.readable_label})


@login_required
def detailedproblemview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    context={}
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../',typ.label),('../',kwargs['tag']),]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../',typ.label+' Problems'),]
    else:
        breadcrumbs=[]
    dropboxpath=list(Dropboxurl.objects.all())[0].url
 #   is_approved=prob.approval_status
    if request.method == "POST":#need more (was previously disabled)
        form=DetailedProblemForm(request.POST,instance=prob)
        if form.is_valid():
            problem = form.save()
            problem.save()
#            if is_approved==False and problem.approval_status==True:
#                problem.approval_user=request.user
#                problem.save()
    else:
        form=DetailedProblemForm(instance=prob)
    #readablelabel
    readablelabel=prob.readable_label.replace('\\#','#')
    #sols...
    sols=list(prob.solutions.all())
    sollist=[]
    rows=[]
    for sol in sols:
        rows.append((sol.solution_text,sol.pk))
    #comments
    coms=list(prob.comments.all())
    crows=[]
    for com in coms:
        crows.append((com.author_name,com.created_date,com.comment_text,com.pk))
    #approvals
    apprs=list(prob.approvals.all())
    arows=[]
    for a in apprs:
        arows.append((a.author_name,a.get_approval_status_display,a.pk))
    #other
    if prob.question_type_new.question_type=='multiple choice':
        mc_texcode=newtexcode(prob.mc_problem_text,dropboxpath,prob.label,prob.answers())
        context['mc_prob_latex']=mc_texcode
        context['mc_answer']=prob.mc_answer
        context['mc']=True
    elif prob.question_type_new.question_type=='short answer':
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['sa_answer']=prob.sa_answer
        context['sa']=True
    elif prob.question_type_new.question_type=='proof':
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
        context['prob_latex']=texcode
        context['pf']=True
    elif prob.question_type_new.question_type=='multiple choice short answer':
        mc_texcode=newtexcode(prob.mc_problem_text,dropboxpath,prob.label,prob.answers())
        context['mc_prob_latex']=mc_texcode
        context['mc_answer']=prob.mc_answer
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,'')
        context['prob_latex']=texcode
        context['sa_answer']=prob.sa_answer
        context['mcsa']=True
    context['rows']=rows
    context['nbar']='problemeditor'
    context['dropboxpath']=dropboxpath
    context['readablelabel']=readablelabel
    context['form']=form
    context['crows']=crows
    context['arows']=arows
    context['breadcrumbs']=breadcrumbs
    return render(request, 'problemeditor/detailedview.html', context)

@login_required
def addproblemview(request):
    prob=Problem()
    if request.method == "POST":
        form = AddProblemForm(request.POST, instance=prob)
        if form.is_valid():
            problem = form.save()
            problem.save()
            problem.author=request.user
            t=list(problem.types.all())[0]
            t.top_index+=1
            t.save()
            problem.label = t.type+str(t.top_index)
            problem.readable_label = t.type+' '+str(t.top_index)
            problem.save()
            return redirect('../detailedview/'+str(problem.pk)+'/')
    else:
        form = AddProblemForm(instance=prob)
    return render(request, 'problemeditor/addview.html', {'form': form, 'nbar': 'problemeditor'})

