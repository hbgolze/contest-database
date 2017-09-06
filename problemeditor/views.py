from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.template import loader,RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.contrib.admin.models import LogEntry, ADDITION,CHANGE,DELETION
from django.contrib.contenttypes.models import ContentType
from django.views.generic import UpdateView

from formtools.wizard.views import SessionWizardView

from randomtest.models import Problem, Tag, Type, Test, UserProfile, Solution,Comment,QuestionType,ProblemApproval,TestCollection
from .forms import ProblemForm,SolutionForm,ProblemTextForm,AddProblemForm,DetailedProblemForm,CommentForm,ApprovalForm,AddContestForm,SAAnswerForm,MCAnswerForm,DuplicateProblemForm,UploadContestForm
from randomtest.utils import goodtag,goodurl,newtexcode,newsoltexcode,compileasy



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
        prob.readable_label = t.label+' '+str(t.top_index)
        prob.top_solution_number = 1
        prob.save()

        compileasy(prob.mc_problem_text,prob.label)
        compileasy(prob.problem_text,prob.label)

        prob.display_problem_text=newtexcode(prob.problem_text,prob.label,'')
        prob.display_mc_problem_text=newtexcode(prob.mc_problem_text,prob.label,prob.answers())

        sol=Solution(solution_text = D['solution_text'])
        sol.save()
        sol.solution_number=1
        sol.authors.add(self.request.user)
        sol.problem_label=prob.label
        sol.display_solution_text = newsoltexcode(sol.solution_text,prob.label+'sol'+str(sol.solution_number))
        sol.save()
        prob.solutions.add(sol)
        prob.save()
        compileasy(sol.solution_text,prob.label,sol="sol1")
        LogEntry.objects.log_action(
            user_id = self.request.user.id,
            content_type_id = ContentType.objects.get_for_model(prob).pk,
            object_id = prob.id,
            object_repr = prob.label,
            action_flag = ADDITION,
            change_message = "problemeditor/CM/bytopic/"+prob.type_new.type+'/'+str(prob.pk)+'/',
            )
        return redirectproblem(self.request,prob.pk)
#        return redirect('/problemeditor/detailedview/'+str(prob.pk)+'/')

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
        if self.instance.question_type_new.question_type == "multiple choice":
            self.instance.problem_text = self.instance.mc_problem_text
            self.instance.display_problem_text=newtexcode(self.instance.mc_problem_text,prob.label,'')
        if self.instance.question_type_new.question_type in ["short answer", "proof"]:
            self.instance.mc_problem_text = self.instance.problem_text
            self.instance.display_mc_problem_text=newtexcode(prob.problem_text,prob.label,prob.answers())

        self.instance.save()
        compileasy(self.instance.mc_problem_text,self.instance.label)
        compileasy(self.instance.problem_text,self.instance.label)
        return redirect('.')
#        return redirect('/problemeditor/detailedview/'+str(self.instance.pk)+'/')



# Create your views here.
@login_required
def typeview(request):
    userprofile,boolcreated = UserProfile.objects.get_or_create(user=request.user)
    obj=list(Type.objects.all().exclude(is_contest=False))
    obj=sorted(obj,key=lambda x:x.type)
    rows=[]
    if userprofile.user_type == 'member' or userprofile.user_type == 'super':
        for i in range(0,len(obj)):
#        P = Problem.objects.filter(types__in=[obj[i]])
            P = Problem.objects.filter(type_new=obj[i])
            num_problems = P.count()
            untagged = P.filter(tags__isnull=True)
            num_untagged = untagged.count()
            nosolutions = P.filter(solutions__isnull=True)
            num_nosolutions = nosolutions.count()
            rows.append((obj[i].type,obj[i].label,num_untagged,num_nosolutions,num_problems))
    obj2=list(Type.objects.filter(is_contest=False))
    obj2=sorted(obj2,key=lambda x:x.type)
    rows2=[]
    if userprofile.user_type == 'manager' or userprofile.user_type == 'super':
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
    context= {'rows': rows, 'nbar': 'problemeditor','rows2':rows2,'user_type' : userprofile.user_type}
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
        problems=list(Problem.objects.filter(type_new=typ).filter(tags__in=[ttag]))
    else:
        problems=list(Problem.objects.filter(type_new=typ).filter(tags__isnull=True))
    problems=sorted(problems, key=lambda x:(x.year,x.problem_number))
    template=loader.get_template('problemeditor/typetagview.html')
    paginator=Paginator(problems,50)
    page = request.GET.get('page')
    try:
        prows=paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        prows = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        prows = paginator.page(paginator.num_pages)
    context= {'rows' : prows, 'type' : typ.type, 'nbar': 'problemeditor','tag':tag,'typelabel':typ.label}
    return HttpResponse(template.render(context,request))

@login_required
def CMtypetagview(request,type,tag):
    tag=goodtag(tag)
    typ=get_object_or_404(Type, type=type)
    rows=[]
    if tag!='untagged':
        ttag=get_object_or_404(Tag, tag=tag)
        problems=list(Problem.objects.filter(type_new=typ).filter(tags__in=[ttag]))
    else:
        problems=list(Problem.objects.filter(type_new=typ).filter(tags__isnull=True))
    problems=sorted(problems, key=lambda x:x.pk)
    template=loader.get_template('problemeditor/CMtypetagview.html')

    paginator=Paginator(problems,50)
    page = request.GET.get('page')
    try:
        prows=paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        prows = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        prows = paginator.page(paginator.num_pages)

    context= {'rows' : prows, 'type' : typ.type, 'nbar': 'problemeditor','tag':tag,'typelabel':typ.label}
    return HttpResponse(template.render(context,request))

@login_required
def testlabelview(request,type,testlabel):
    typ=get_object_or_404(Type, type=type)
    rows=[]
    if testlabel!='untagged':
        problems=list(Problem.objects.filter(test_label=testlabel))
    else:
        problems=list(Problem.objects.filter(type_new=typ).filter(tags__isnull=True))
    problems=sorted(problems, key=lambda x:(x.year,x.problem_number))
    template=loader.get_template('problemeditor/typetagview.html')
    context= {'rows' : problems, 'type': typ.type, 'nbar': 'problemeditor','type':typ.type,'typelabel':typ.label,'tag':testlabel}
    return HttpResponse(template.render(context,request))

@login_required
def CMtopicview(request,type):#unapprovedview
    typ=get_object_or_404(Type, type=type)
    rows=[]
    problems=list(Problem.objects.filter(type_new=typ))
    problems=sorted(problems, key=lambda x:(x.pk))
    template=loader.get_template('problemeditor/CMtopicview.html')#unapproved

    paginator=Paginator(problems,50)
    page = request.GET.get('page')
    try:
        prows=paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        prows = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        prows = paginator.page(paginator.num_pages)

    context= {'rows' : prows, 'type' : typ.type, 'nbar': 'problemeditor','typelabel':typ.label}
    return HttpResponse(template.render(context,request))

@login_required
def problemview(request,type,tag,label):
    tag=goodtag(tag)
    typ=get_object_or_404(Type, type=type)
    prob=get_object_or_404(Problem, label=label)
    tags=Tag.objects.all()
    if request.method == "POST":
        formpost=request.POST
        if "addsolution" in formpost:
            sol_text=formpost.get("new_solution_text","")
            sol_num=prob.top_solution_number+1
            prob.top_solution_number=sol_num
            prob.save()
            sol = Solution(solution_text=sol_text,solution_number=sol_num,problem_label=prob.label)
            sol.save()
            sol.authors.add(request.user)
            sol.save()
            compileasy(sol.solution_text,prob.label,sol='sol'+str(sol_num))
            sol.display_solution_text = newsoltexcode(sol.solution_text,prob.label+'sol'+str(sol.solution_number))
            sol.save()
            prob.solutions.add(sol)
            prob.save()
            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(sol).pk,
                object_id = sol.id,
                object_repr = prob.label+' sol '+str(sol.solution_number),
                action_flag=ADDITION,
                change_message="problemeditor/contest/bytest/"+prob.type_new.type+'/'+prob.test_label+'/'+prob.label+'/editsolution/'+str(sol.pk)+'/',
                )
            form = ProblemForm(instance=prob)
        elif "addlink" in formpost:
            form = request.POST
            linked_problem_label = form.get("linked_problem_label","")
            if Problem.objects.filter(label=linked_problem_label).exists():
                q=Problem.objects.get(label=linked_problem_label)
                prob.duplicate_problems.add(q)
                prob.save()
            form = ProblemForm(instance=prob)
        else:
            form = ProblemForm(request.POST, instance=prob)
            if form.is_valid():
                problem = form.save()
                problem.save()
                LogEntry.objects.log_action(
                    user_id = request.user.id,
                    content_type_id = ContentType.objects.get_for_model(problem).pk,
                    object_id = problem.id,
                    object_repr = problem.label,
                    action_flag = CHANGE,
                    change_message = "problemeditor/contest/bytest/"+problem.type_new.type+'/'+problem.test_label+'/'+problem.label+'/',
                    )

    else:
        form = ProblemForm(instance=prob)
    context={}
    context['rows']=prob.solutions.all()
    context['prob']=prob
    context['form']=form
    context['nbar']='problemeditor'
    context['typelabel']= typ.label
    context['label'] = label
    context['tag'] = tag
    userprofile,boolcreated = UserProfile.objects.get_or_create(user=request.user)
    context['user_type'] =  userprofile.user_type
    return render(request, 'problemeditor/view.html', context)

@login_required
def editproblemtextview(request,type,tag,label):
    tag=goodtag(tag)
    typ=get_object_or_404(Type, type=type)
    prob=get_object_or_404(Problem, label=label)
    if request.method == "POST":
        form = ProblemTextForm(request.POST, instance=prob)
        if form.is_valid():
            problem = form.save()
            problem.display_problem_text = newtexcode(problem.problem_text,problem.label,'')
            problem.display_mc_problem_text = newtexcode(problem.mc_problem_text,problem.label,problem.answers())
            problem.save()
            compileasy(problem.mc_problem_text,problem.label)
            compileasy(problem.problem_text,problem.label)
            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(problem).pk,
                object_id = problem.id,
                object_repr = problem.label,
                action_flag = CHANGE,
                change_message = "problemeditor/contest/bytest/"+problem.type_new.type+'/'+problem.test_label+'/'+problem.label+'/',
                )
        return redirect('../')
    else:
        form = ProblemTextForm(instance=prob)
    breadcrumbs=[('/problemeditor/','Select Type'),('../../../',typ.label),('../../',tag),('../',prob.readable_label),]

    context={}
    context['nbar']='problemeditor'
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
        breadcrumbs=[('/problemeditor/','Select Type'),('../../../',typ.label),('../../',goodtag(kwargs['tag'])),('../',str(prob.readable_label))]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('/problemeditor/','Select Type'),('../../',typ.label+' Problems'),('../',str(prob.readable_label))]
    else:
        breadcrumbs=[('/problemeditor/','Select Type'),('../',str(prob.readable_label)),]
    if request.method == "POST":
        form = ProblemTextForm(request.POST, instance=prob)
        if form.is_valid():
            problem = form.save()
            problem.display_problem_text = newtexcode(problem.problem_text,problem.label,'')
            problem.display_mc_problem_text = newtexcode(problem.mc_problem_text,problem.label,problem.answers())

            problem.save()
            compileasy(problem.mc_problem_text,problem.label)
            compileasy(problem.problem_text,problem.label)
            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(problem).pk,
                object_id = problem.id,
                object_repr = problem.label,
                action_flag = CHANGE,
                change_message = "problemeditor/CM/bytopic/"+problem.type_new.type+'/'+str(problem.pk)+'/',
                )

        return redirect('../')
    else:
        form = ProblemTextForm(instance=prob)
    context={}
    context['nbar']='problemeditor'
    context['form']=form
    context['breadcrumbs']=breadcrumbs
    return render(request, 'problemeditor/editproblemtext.html', context)

@login_required
def newsolutionview(request,type,tag,label):
    tag=goodtag(tag)
    typ=get_object_or_404(Type, type=type)
    prob=get_object_or_404(Problem, label=label)
    if request.method == "POST":
        sol_form = SolutionForm(request.POST)
        if sol_form.is_valid():
            sol_num=prob.top_solution_number+1
            prob.top_solution_number=sol_num
            prob.save()
            sol = sol_form.save()
            sol.solution_number=sol_num
            sol.authors.add(request.user)
            sol.problem_label=label
            sol.save()
            compileasy(sol.solution_text,prob.label,sol='sol'+str(sol_num))
            sol.display_solution_text = newsoltexcode(sol.solution_text,prob.label+'sol'+str(sol.solution_number))
            sol.save()
            prob.solutions.add(sol)
            prob.save()
            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(sol).pk,
                object_id = sol.id,
                object_repr = prob.label+' sol '+str(sol.solution_number),
                action_flag=ADDITION,
                change_message="problemeditor/contest/bytest/"+prob.type_new.type+'/'+prob.test_label+'/'+prob.label+'/editsolution/'+str(sol.pk)+'/',
                )
        return redirect('../')
    else:
        sol_num=prob.top_solution_number+1
        sol = Solution(solution_text='', solution_number=sol_num, problem_label=label)
        form = SolutionForm(instance=sol)
    breadcrumbs=[('../../../',typ.label),('../../',tag),('../',prob.readable_label),]

    context={}
    context['prob']=prob
    context['form']=form
    context['label'] = label
    context['nbar']='problemeditor'
    context['typelabel']= typ.label
    context['tag'] = tag
    context['breadcrumbs']=breadcrumbs

    return render(request, 'problemeditor/newsol.html', context)

@login_required
def newsolutionpkview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../../',typ.label),('../../',goodtag(kwargs['tag'])),('../',str(prob.readable_label))]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../',typ.label+' Problems'),('../',prob.readable_label)]
    else:
        breadcrumbs=[('../',prob.readable_label),]
    if request.method == "POST":
        sol_form = SolutionForm(request.POST)
        if sol_form.is_valid():
            sol_num=prob.top_solution_number+1
            prob.top_solution_number=sol_num
            prob.save()
            sol = sol_form.save()
            sol.solution_number=sol_num
            sol.authors.add(request.user)
            sol.problem_label=prob.label
            sol.save()
            compileasy(sol.solution_text,prob.label,sol='sol'+str(sol_num))
            sol.display_solution_text = newsoltexcode(sol.solution_text,prob.label+'sol'+str(sol.solution_number))
            sol.save()
            prob.solutions.add(sol)
            prob.save()
            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(sol).pk,
                object_id = sol.id,
                object_repr = prob.label+' sol '+str(sol.solution_number),
                action_flag=ADDITION,
                change_message="problemeditor/CM/bytopic/"+prob.type_new.type+'/'+str(prob.pk)+'/editsolution/'+str(sol.pk)+'/',
                )

        return redirect('../')#detailedproblemview,pk=pk)
    else:
        sol_num=prob.top_solution_number+1
        sol=Solution(solution_text='', solution_number=sol_num, problem_label=prob.label)
        form = SolutionForm(instance=sol)

    return render(request, 'problemeditor/newsol.html',{'form': form, 'nbar': 'problemeditor', 'prob':prob, 'breadcrumbs':breadcrumbs})

@login_required
def editsolutionview(request,type,tag,label,spk):
    tag=goodtag(tag)
    typ=get_object_or_404(Type, type=type)
    prob=get_object_or_404(Problem, label=label)
    sol=Solution.objects.get(pk=spk)
    if request.method == "POST":
        if request.POST.get("save"):
            sollist=request.POST.getlist('solution_text')
            sol.solution_text = sollist[0]
            sol.modified_date = timezone.now()
            sol.authors.add(request.user)
            sol.save()
            compileasy(sol.solution_text,prob.label,sol='sol'+str(sol.solution_number))
            sol.display_solution_text = newsoltexcode(sol.solution_text,prob.label+'sol'+str(sol.solution_number))
            sol.save()
            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(sol).pk,
                object_id = sol.id,
                object_repr = prob.label+' sol '+str(sol.solution_number),
                action_flag = CHANGE,
                change_message = "problemeditor/contest/bytest/"+prob.type_new.type+'/'+prob.test_label+'/'+prob.label+'/editsolution/'+str(sol.pk),
                )
            return redirect('../../')
#            return redirect(problemview,type=type,tag=tag,label=label)
    form = SolutionForm(instance=sol)

    breadcrumbs=[('../../../../',typ.label),('../../../',tag),('../../',prob.readable_label),]
    return render(request, 'problemeditor/editsol.html', {'form': form, 'nbar': 'problemeditor','typelabel':typ.label,'tag':tag,'label':label, 'prob':prob,'breadcrumbs':breadcrumbs})

@login_required
def editsolutionpkview(request,**kwargs):
    pk=kwargs['pk']
    spk=kwargs['spk']
    prob=get_object_or_404(Problem, pk=pk)
    sol=Solution.objects.get(pk=spk)
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../../../',typ.label),('../../../',goodtag(kwargs['tag'])),('../../',str(prob.readable_label))]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../../',typ.label+' Problems'),('../../',prob.readable_label),]
    else:
        breadcrumbs=[('../../','Solutions to '+prob.readable_label),]
    if request.method == "POST":
        if request.POST.get("save"):
            sollist=request.POST.getlist('solution_text')
            sol.solution_text=sollist[0]
            sol.modified_date = timezone.now()
            sol.authors.add(request.user)
            sol.save()
            compileasy(sol.solution_text,prob.label,sol='sol'+str(sol.solution_number))
            sol.display_solution_text = newsoltexcode(sol.solution_text,prob.label+'sol'+str(sol.solution_number))
            sol.save()
            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(sol).pk,
                object_id = sol.id,
                object_repr = prob.label+' sol '+str(sol.solution_number),
                action_flag = CHANGE,
                change_message = "problemeditor/CM/bytopic/"+prob.type_new.type+'/'+str(prob.pk)+'/editsolution/'+str(sol.pk),
                )
            return redirect('../../')#detailedproblemview,pk=pk)
    form = SolutionForm(instance=sol)
    return render(request, 'problemeditor/editsol.html', {'form': form, 'nbar': 'problemeditor', 'prob':prob,'breadcrumbs':breadcrumbs})

@login_required
def editanswerview(request,type,tag,label):
    tag=goodtag(tag)
    typ=get_object_or_404(Type, type=type)
    prob=get_object_or_404(Problem, label=label)
    if request.method == "POST":
        if request.POST.get("save"):
            if request.POST.get("qt")=='multiple choice':
                ans_form = MCAnswerForm(request.POST,instance=prob)
                if ans_form.is_valid():
                    prob2 = ans_form.save()
                    prob2.save()
                    prob.answer=prob.mc_answer
                    prob.save()
            else:
                ans_form = SAAnswerForm(request.POST,instance=prob)
                if ans_form.is_valid():
                    prob2 = ans_form.save()
                    prob2.save()
                    prob.answer=prob.sa_answer
                    prob.save()
            return redirect('../')
    breadcrumbs=[('../../../',typ.label),('../../',tag),('../',prob.readable_label),]
    ans=''
    if prob.question_type_new.question_type=='multiple choice':
        form = MCAnswerForm(instance=prob)
        ans=prob.mc_answer
    elif prob.question_type_new.question_type=='short answer':
        form = SAAnswerForm(instance=prob)
        ans=prob.sa_answer
#    elif prob.question_type_new.question_type=='multiple choice short answer':
#        ans=prob.mc_answer+' and '+prob.sa_answer
    return render(request, 'problemeditor/editanswer.html', {'form': form, 'nbar': 'problemeditor','typelabel':typ.label,'tag':tag,'label':label,'answer':ans,'breadcrumbs':breadcrumbs,'prob':prob})

@login_required
def editreviewpkview(request,**kwargs):
    pk=kwargs['pk']
    apk=kwargs['apk']
    prob=get_object_or_404(Problem, pk=pk)
    appr=ProblemApproval.objects.get(pk=apk)
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../../../',typ.label),('../../../',goodtag(kwargs['tag'])),('../../',str(prob.readable_label))]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../../',typ.label+' Problems'),('../../',prob.readable_label),]
    else:
        breadcrumbs=[('../../','Solutions to '+prob.readable_label),]
    if request.method == "POST":
        if request.POST.get("save"):
            appr_form = ApprovalForm(request.POST,instance=appr)
            if appr_form.is_valid():
                appr2 = appr_form.save()
                appr2.save()
#                appr.approval_user = request.user
#                appr.author_name=appr_form.author_name
#                appr.approval_status=request.POST.get('approval_status')#appr_form.approval_status
#                appr.save()
                LogEntry.objects.log_action(
                    user_id = request.user.id,
                    content_type_id = ContentType.objects.get_for_model(appr2).pk,
                    object_id = appr2.id,
                    object_repr = prob.label,
                    action_flag = CHANGE,
                    change_message = "problemeditor/CM/bytopic/"+prob.type_new.type+'/'+str(prob.pk)+'/',
                    )
            return redirect('../../')#detailedproblemview,pk=pk)
    form = ApprovalForm(instance=appr)
    return render(request, 'problemeditor/editappr.html', {'form': form, 'nbar': 'problemeditor','prob':prob,'breadcrumbs':breadcrumbs})


@login_required
def deletesolutionview(request,type,tag,label,spk):#If solution_number is kept, this must be modified to adjust.
    sol = get_object_or_404(Solution, pk=spk)
    prob = get_object_or_404(Problem,label=label)
    LogEntry.objects.log_action(
        user_id = request.user.id,
        content_type_id = ContentType.objects.get_for_model(sol).pk,
        object_id = sol.id,
        object_repr = prob.label+' sol '+str(sol.solution_number),
        action_flag = DELETION,
        change_message = "problemeditor/contest/bytest/"+prob.type_new.type+'/'+prob.test_label+'/'+prob.label+'/editsolution/'+str(sol.pk),
        )
    sol.delete()
    return redirect('../../')

@login_required
def deletesolutionpkview(request,**kwargs):#If solution_number is kept, this must be modified to adjust.
    pk=kwargs['pk']
    spk=kwargs['spk']
    sol = get_object_or_404(Solution, pk=spk)
    prob = get_object_or_404(Problem,pk=pk)
    LogEntry.objects.log_action(
        user_id = request.user.id,
        content_type_id = ContentType.objects.get_for_model(sol).pk,
        object_id = sol.id,
        object_repr = prob.label+' sol '+str(sol.solution_number),
        action_flag = DELETION,
        change_message = "problemeditor/CM/bytopic/"+prob.type_new.type+'/'+str(prob.pk)+'/editsolution/'+str(sol.pk),
        )
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
    problems=list(Problem.objects.filter(type_new=typ).filter(tags__isnull=True))
    problems=sorted(problems, key=lambda x:(x.year,x.problem_number))
    template=loader.get_template('problemeditor/typetagview.html')
    context= {'rows' : problems, 'type' : typ.type, 'nbar': 'problemeditor'}
    return HttpResponse(template.render(context,request))

@login_required
def newcommentpkview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../../',typ.label),('../../',goodtag(kwargs['tag'])),('../',str(prob.readable_label))]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../',typ.label+' Problems'),('../',prob.readable_label),]
    else:
        breadcrumbs=[('../',prob.readable_label),]

    com_num=prob.comments.count()+1
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

    return render(request, 'problemeditor/newcom.html', {'form': com_form, 'nbar': 'problemeditor','breadcrumbs':breadcrumbs,'label':prob.readable_label})

@login_required
def newreviewpkview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../../',typ.label),('../../',goodtag(kwargs['tag'])),('../',str(prob.readable_label))]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../',typ.label+' Problems'),('../',prob.readable_label),]
    else:
        breadcrumbs=[('../',prob.readable_label),]

    if request.method == "POST":
        appr_form = ApprovalForm(request.POST)
        if appr_form.is_valid():
            appr = appr_form.save(commit=False)
            appr.approval_user = request.user
            appr.save()
            prob.approvals.add(appr)
            prob.save()

            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(appr).pk,
                object_id = appr.id,
                object_repr = prob.label,
                action_flag = ADDITION,
                change_message = "problemeditor/CM/bytopic/"+prob.type_new.type+'/'+str(prob.pk)+'/',
                )

            return redirect('../')
    else:
        appr=ProblemApproval()
        appr_form = ApprovalForm(instance=appr)

    return render(request, 'problemeditor/newappr.html', {'form': appr_form, 'nbar': 'problemeditor','breadcrumbs':breadcrumbs,'prob':prob})


@login_required
def detailedproblemview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    context={}
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../',typ.label),('../',goodtag(kwargs['tag'])),]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../',typ.label+' Problems'),]
    else:
        breadcrumbs=[]
    if request.method == "POST":#need more (was previously disabled)
        formpost=request.POST
        if "addsolution" in formpost:
            sol_text=formpost.get("new_solution_text","")
            sol_num=prob.top_solution_number+1
            prob.top_solution_number=sol_num
            prob.save()
            sol = Solution(solution_text=sol_text,solution_number=sol_num,problem_label=prob.label)
            sol.save()
            sol.authors.add(request.user)
            sol.save()
            compileasy(sol.solution_text,prob.label,sol='sol'+str(sol_num))
            sol.display_solution_text = newsoltexcode(sol.solution_text,prob.label+'sol'+str(sol.solution_number))
            sol.save()
            prob.solutions.add(sol)
            prob.save()
            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(sol).pk,
                object_id = sol.id,
                object_repr = prob.label+' sol '+str(sol.solution_number),
                action_flag=ADDITION,
                change_message="problemeditor/CM/bytopic/"+prob.type_new.type+'/'+str(prob.pk)+'/',
                )
            form = DetailedProblemForm(instance=prob)
        elif "addcomment" in formpost:
            com_num = prob.comments.count()+1
            com_text = formpost.get("new_comment_text","")
            author_name = formpost.get("author_name","")
            com = Comment(comment_text=com_text,comment_number=com_num,author_name=author_name,author=request.user,problem_label=prob.label)
            com.save()
            prob.comments.add(com)
            prob.save()
            form = DetailedProblemForm(instance=prob)
        else:
            form=DetailedProblemForm(request.POST,instance=prob)
            if form.is_valid():
                problem = form.save()
                problem.display_problem_text = newtexcode(problem.problem_text,problem.label,'')
                problem.display_mc_problem_text = newtexcode(problem.mc_problem_text,problem.label,problem.answers())
                problem.save()
                LogEntry.objects.log_action(
                    user_id = request.user.id,
                    content_type_id = ContentType.objects.get_for_model(problem).pk,
                    object_id = problem.id,
                    object_repr = problem.label,
                    action_flag = CHANGE,
                    change_message = "problemeditor/CM/bytopic/"+problem.type_new.type+'/'+str(problem.pk)+'/',
                    )
    else:
        form=DetailedProblemForm(instance=prob)
    context['prob']=prob
    context['nbar']='problemeditor'
    context['form']=form
    context['breadcrumbs']=breadcrumbs
    return render(request, 'problemeditor/detailedview.html', context)


@login_required
def addcontestview(request,type,num):
    typ=get_object_or_404(Type, type=type)
    num=int(num)
    if request.method == "POST":
        form=request.POST
        F=form#.cleaned_data
        label = F['year']+type+F['formletter']
        readablelabel = F['year'] + ' ' + typ.readable_label_pre_form + F['formletter']
        readablelabel = readablelabel.rstrip()
        if typ.default_question_type=='mc':
            for i in range(1,num+1):
                p=Problem(mc_problem_text = F['problem_text'+str(i)],
                          problem_text = F['problem_text'+str(i)],
                          answer = F['answer'+str(i)],
                          mc_answer = F['answer'+str(i)],
                          answer_choices = '$\\textbf{(A) }'+F['answer_A'+str(i)]+'\\qquad\\textbf{(B) }'+F['answer_B'+str(i)]+'\\qquad\\textbf{(C) }'+F['answer_C'+str(i)]+'\\qquad\\textbf{(D) }'+F['answer_D'+str(i)]+'\\qquad\\textbf{(E) }'+F['answer_E'+str(i)]+'$',
                          answer_A = F['answer_A'+str(i)],
                          answer_B = F['answer_B'+str(i)],
                          answer_C = F['answer_C'+str(i)],
                          answer_D = F['answer_D'+str(i)],
                          answer_E = F['answer_E'+str(i)],
                          label = label+str(i),
                          readable_label = readablelabel+typ.readable_label_post_form+str(i),
                          type_new = typ,
                          question_type_new = QuestionType.objects.get(question_type='multiple choice'),
                          problem_number = i,
                          year = F['year'],
                          form_letter=F['formletter'],
                          test_label=label,
                          top_solution_number=0,
                          )
                p.save()
                p.types.add(typ)
                p.question_type.add(QuestionType.objects.get(question_type='multiple choice'))
                p.save()
                compileasy(p.mc_problem_text,p.label)
                compileasy(p.problem_text,p.label)
                p.display_problem_text = newtexcode(p.problem_text,p.label,'')
                p.display_mc_problem_text = newtexcode(p.mc_problem_text,p.label,p.answers())
                p.save()
        if typ.default_question_type=='sa':
            for i in range(1,num+1):
                p=Problem(problem_text=F['problem_text'+str(i)],
                          answer=F['answer'+str(i)],
                          sa_answer=F['answer'+str(i)],
                          label=label+str(i),
                          readable_label=readablelabel+typ.readable_label_post_form+str(i),
                          type_new=typ,
                          question_type_new=QuestionType.objects.get(question_type='short answer'),
                          problem_number=i,
                          year=F['year'],
                          form_letter=F['formletter'],
                          test_label=label,
                          top_solution_number=0,
                          )
                p.save()
                p.types.add(typ)
                p.question_type.add(QuestionType.objects.get(question_type='short answer'))
                p.save()
                compileasy(p.mc_problem_text,p.label)
                compileasy(p.problem_text,p.label)
                p.display_problem_text = newtexcode(p.problem_text,p.label,'')
                p.display_mc_problem_text = newtexcode(p.mc_problem_text,p.label,p.answers())
                p.save()
        if typ.default_question_type=='pf':
            for i in range(1,num+1):
                p=Problem(problem_text=F['problem_text'+str(i)],
                          label=label+str(i),
                          readable_label=readablelabel+typ.readable_label_post_form+str(i),
                          type_new=typ,
                          question_type_new=QuestionType.objects.get(question_type='proof'),
                          problem_number=i,
                          year=F['year'],
                          form_letter=F['formletter'],
                          test_label=label,
                          top_solution_number=0,
                          )
                p.save()
                p.types.add(typ)
                p.question_type.add(QuestionType.objects.get(question_type='proof'))
                p.save()
                compileasy(p.mc_problem_text,p.label)
                compileasy(p.problem_text,p.label)
                p.display_problem_text = newtexcode(p.problem_text,p.label,'')
                p.display_mc_problem_text = newtexcode(p.mc_problem_text,p.label,p.answers())
                p.save()
        P=Problem.objects.filter(test_label=label)
        if len(P)>0:
            t=Test(name=readablelabel)
            t.save()
        for i in P:
            t.problems.add(i)
            t.types.add(i.type_new)
        t.save()
        tc,boolcreated=TestCollection.objects.get_or_create(name=typ.label)
        tc.tests.add(t)
        tc.save()
        return redirect('/problemeditor/')
    form=AddContestForm(request.POST or None,num_probs=num,type=type)
    context={'nbar': 'problemeditor','num': num,'typ':typ,'nums':[i for i in range(1,num+1)]}
    if typ.default_question_type=='mc':
        context['mc']=True
    elif typ.default_question_type=='sa':
        context['sa']=True
    elif typ.default_question_type=='mcsa':
        context['mc']=True
        context['sa']=True
    else:
        context['pf']=True
    context['form']=form
    return render(request, 'problemeditor/addcontestform.html', context=context)


@login_required
def my_activity(request):
    log = LogEntry.objects.filter(user_id = request.user.id).filter(change_message__contains="problemeditor")
    linkedlog=[]
    for i in log:
        if i.content_type.name=='problem':
            if Problem.objects.filter(pk=i.object_id).exists():
                linkedlog.append((i,True))
            else:
                linkedlog.append((i,False))
        if i.content_type.name=='solution':
            if Solution.objects.filter(pk=i.object_id).exists():
                linkedlog.append((i,True))
            else:
                linkedlog.append((i,False))
        if i.content_type.name=='problem approval':
            if ProblemApproval.objects.filter(pk=i.object_id).exists():
                linkedlog.append((i,True))
            else:
                linkedlog.append((i,False))
    paginator=Paginator(linkedlog,50)
    page = request.GET.get('page')
    try:
        plog=paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        plog = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        plog = paginator.page(paginator.num_pages)
    return render(request,'problemeditor/activity_log.html',{'log':plog,'nbar':'problemeditor'})

@login_required
def redirectproblem(request,pk):
    p=get_object_or_404(Problem,pk=pk)
    if p.type_new.is_contest==True:
        return redirect('/problemeditor/contest/bytest/'+p.type_new.type+'/'+p.test_label+'/'+p.label+'/')
    else:
        return redirect('/problemeditor/CM/bytopic/'+p.type_new.type+'/'+str(p.pk)+'/')


class SolutionUpdateView(UpdateView):
    model = Solution
    form_class = SolutionForm
    template_name = 'problemeditor/solution_edit_form.html'
    def dispatch(self, *args, **kwargs):
        self.solution_id = kwargs['spk']
        self.problem_label = kwargs['label']
        self.type = kwargs['type']
        self.tag = kwargs['tag']
        return super(SolutionUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        solution = Solution.objects.get(id=self.solution_id)
        return redirect('../../')



    def get_object(self, queryset=None):
        return get_object_or_404(Solution, pk=self.solution_id)
    def get_context_data(self, *args, **kwargs):
        context = super(SolutionUpdateView, self).get_context_data(*args, **kwargs)
        context['prob'] = get_object_or_404(Problem,label=self.problem_label)
        context['type'] = self.type
        context['tag'] = self.tag
        context['label'] = self.problem_label
        context['suffix'] = ''
        if Tag.objects.filter(tag=goodtag(self.tag)).exists() == True:
            context['suffix'] = '_bytag'
        return context

class CMSolutionUpdateView(UpdateView):
    model = Solution
    form_class = SolutionForm
    template_name = 'problemeditor/solution_edit_form.html'
    def dispatch(self, *args, **kwargs):
        self.solution_id = kwargs['spk']
        self.type = kwargs['type']
        if 'tag' in kwargs:
            self.tag = kwargs['tag']
        self.prob_pk = kwargs['pk']
        return super(CMSolutionUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        solution = Solution.objects.get(id=self.solution_id)
        return redirect('../../')



    def get_object(self, queryset=None):
        return get_object_or_404(Solution, pk=self.solution_id)
    def get_context_data(self, *args, **kwargs):
        context = super(CMSolutionUpdateView, self).get_context_data(*args, **kwargs)
        context['prob'] = get_object_or_404(Problem,pk=self.prob_pk)
        context['type'] = self.type
        context['suffix'] = ''
        if hasattr(self,'tag'):
            context['tag'] = self.tag
            context['suffix'] = '_bytag'
        context['prefix'] = 'CM_'
        return context

@login_required
def remove_duplicate(request,type,tag,label,pk):
    if request.user.userprofile.user_type == 'super':
        prob=get_object_or_404(Problem,label=label)
        if prob.duplicate_problems.filter(pk=pk).exists():
            prob.duplicate_problems.remove(Problem.objects.get(pk=pk))
            prob.save()
    return redirect("../../")

@login_required
def uploadcontestview(request):
    if request.POST and request.FILES:
        form = UploadContestForm(request.POST, request.FILES)
        if form.is_valid():
            contestfile = form.cleaned_data["contestfile"]
            year=form.cleaned_data['year']
            formletter=form.cleaned_data['formletter']
            typ=form.cleaned_data['typ']
            type2=Type.objects.get(type=typ)
            if contestfile.multiple_chunks()== True:
                pass
            else:
                f=contestfile.read().decode('utf-8')
#                print(f.decode("utf-8"))
                problemtexts = str(f).split('=========')


                label = year+type2.type+formletter
                readablelabel = year + ' ' + type2.readable_label_pre_form + formletter
                readablelabel = readablelabel.rstrip()
#                if type.default_question_type=='mc':
#                    for i in range(1,num+1):
#                p=Problem(mc_problem_text = F['problem_text'+str(i)],
#                          problem_text = F['problem_text'+str(i)],
#                          answer = F['answer'+str(i)],
#                          mc_answer = F['answer'+str(i)],
#                          answer_choices = '$\\textbf{(A) }'+F['answer_A'+str(i)]+'\\qquad\\textbf{(B) }'+F['answer_B'+str(i)]+'\\qquad\\textbf{(C) }'+F['answer_C'+str(i)]+'\\qquad\\textbf{(D) }'+F['answer_D'+str(i)]+'\\qquad\\textbf{(E) }'+F['answer_E'+str(i)]+'$',
#                          answer_A = F['answer_A'+str(i)],
#                          answer_B = F['answer_B'+str(i)],
#                          answer_C = F['answer_C'+str(i)],
#                          answer_D = F['answer_D'+str(i)],
#                          answer_E = F['answer_E'+str(i)],
#                          label = label+str(i),
#                          readable_label = readablelabel+typ.readable_label_post_form+str(i),
#                          type_new = typ,
#                          question_type_new = QuestionType.objects.get(question_type='multiple choice'),
#                          problem_number = i,
#                          year = F['year'],
#                          form_letter=F['formletter'],
#                          test_label=label,
#                          top_solution_number=0,
#                          )
#                p.save()
#                p.types.add(typ)
#                p.question_type.add(QuestionType.objects.get(question_type='multiple choice'))
#                p.save()
#                compileasy(p.mc_problem_text,p.label)
#                compileasy(p.problem_text,p.label)
#                p.display_problem_text = newtexcode(p.problem_text,p.label,'')
#                p.display_mc_problem_text = newtexcode(p.mc_problem_text,p.label,p.answers())
#                p.save()
                if type2.default_question_type=='sa':
                    for i in range(1,len(problemtexts)):
                        p=Problem(problem_text = problemtexts[i],
                                  answer='',
                                  sa_answer='',
                                  label=label+str(i),
                                  readable_label=readablelabel+type2.readable_label_post_form+str(i),
                                  type_new=type2,
                                  question_type_new=QuestionType.objects.get(question_type='short answer'),
                                  problem_number=i,
                                  year=year,
                                  form_letter=formletter,
                                  test_label=label,
                                  top_solution_number=0,
                                  )
                        p.save()
                        p.types.add(type2)
                        p.question_type.add(QuestionType.objects.get(question_type='short answer'))
                        p.save()
                        compileasy(p.mc_problem_text,p.label)
                        compileasy(p.problem_text,p.label)
                        p.display_problem_text = newtexcode(p.problem_text,p.label,'')
                        p.display_mc_problem_text = newtexcode(p.mc_problem_text,p.label,p.answers())
                        p.save()
                if type2.default_question_type=='pf':
                    for i in range(0,len(problemtexts)):
                        p=Problem(problem_text=problemtexts[i],
                                  label=label+str(i),
                                  readable_label=readablelabel+type2.readable_label_post_form+str(i),
                                  type_new=type2,
                                  question_type_new=QuestionType.objects.get(question_type='proof'),
                                  problem_number=i,
                                  year=year,
                                  form_letter=formletter,
                                  test_label=label,
                                  top_solution_number=0,
                                  )
                        p.save()
                        p.types.add(type2)
                        p.question_type.add(QuestionType.objects.get(question_type='proof'))
                        p.save()
                        compileasy(p.mc_problem_text,p.label)
                        compileasy(p.problem_text,p.label)
                        p.display_problem_text = newtexcode(p.problem_text,p.label,'')
                        p.display_mc_problem_text = newtexcode(p.mc_problem_text,p.label,p.answers())
                        p.save()
                P=Problem.objects.filter(test_label=label)
                if len(P)>0:
                    t=Test(name=readablelabel)
                    t.save()
                for i in P:
                    t.problems.add(i)
                    t.types.add(i.type_new)
                t.save()
                tc,boolcreated=TestCollection.objects.get_or_create(name=type2.label)
                tc.tests.add(t)
                tc.save()
                return redirect('/problemeditor/')
    form=UploadContestForm()
    return render(request, 'problemeditor/addcontestfileform.html', context={'form':form})
