from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect,Http404,JsonResponse
from django.template import loader,RequestContext
from django.template.loader import get_template,render_to_string
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.contrib.admin.models import LogEntry, ADDITION,CHANGE,DELETION
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.views.generic import UpdateView,CreateView,DeleteView,ListView,DetailView

from formtools.wizard.views import SessionWizardView

from randomtest.models import Problem, Tag, Type, Test, UserProfile, Solution,Comment,QuestionType,ProblemApproval,TestCollection,NewTag
from .forms import SolutionForm,CommentForm,ApprovalForm,AddContestForm,DuplicateProblemForm,UploadContestForm,NewTagForm,AddNewTagForm,EditMCAnswer,EditSAAnswer,MCProblemTextForm,SAProblemTextForm,ChangeQuestionTypeForm1,ChangeQuestionTypeForm2MC,ChangeQuestionTypeForm2MCSA,ChangeQuestionTypeForm2SA,ChangeQuestionTypeForm2PF,DifficultyForm
from randomtest.utils import goodtag,goodurl,newtexcode,newsoltexcode,compileasy

from django.db.models import Count

from django import forms

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
        D = {}
        for form in form_list:
            x = form.cleaned_data
            for i in x:
                D[i] = x[i]
        if D['question_type'].question_type == 'short answer':
            prob = Problem(
                problem_text = D['problem_text'],
                author_name = D['author_name'],
                answer = D['correct_short_answer_answer'],
                sa_answer = D['correct_short_answer_answer'],
                type_new = D['type'],
                question_type_new = D['question_type'],
                )
        elif D['question_type'].question_type == 'proof':
            prob = Problem(
                problem_text = D['problem_text'],
                author_name = D['author_name'],
                type_new = D['type'],
                question_type_new = D['question_type'],
                )
        elif D['question_type'].question_type == 'multiple choice':
            prob = Problem(
                mc_problem_text = D['mc_problem_text'],
                author_name = D['author_name'],
                answer = D['correct_multiple_choice_answer'],
                mc_answer = D['correct_multiple_choice_answer'],
                answer_choices = '$\\textbf{(A) }'+D['answer_A']+'\\qquad\\textbf{(B) }'+D['answer_B']+'\\qquad\\textbf{(C) }'+D['answer_C']+'\\qquad\\textbf{(D) }'+D['answer_D']+'\\qquad\\textbf{(E) }'+D['answer_E']+'$',
                answer_A = D['answer_A'],
                answer_B = D['answer_B'],
                answer_C = D['answer_C'],
                answer_D = D['answer_D'],
                answer_E = D['answer_E'],
                type_new = D['type'],
                question_type_new = D['question_type'],
                )
        elif D['question_type'].question_type == 'multiple choice short answer':
            prob = Problem(
                problem_text = D['problem_text'],
                mc_problem_text = D['mc_problem_text'],
                author_name = D['author_name'],
                answer = D['correct_multiple_choice_answer'],
                mc_answer = D['correct_multiple_choice_answer'],
                answer_choices = '$\\textbf{(A) }'+D['answer_A']+'\\qquad\\textbf{(B) }'+D['answer_B']+'\\qquad\\textbf{(C) }'+D['answer_C']+'\\qquad\\textbf{(D) }'+D['answer_D']+'\\qquad\\textbf{(E) }'+D['answer_E']+'$',
                answer_A = D['answer_A'],
                answer_B = D['answer_B'],
                answer_C = D['answer_C'],
                answer_D = D['answer_D'],
                answer_E = D['answer_E'],
                type_new = D['type'],
                question_type_new = D['question_type'],
                )
        prob.save()
        prob.question_type.add(D['question_type'])
        prob.types.add(D['type'])
        prob.author = self.request.user
        t = prob.type_new
        t.top_index += 1
        t.save()
        prob.label = t.type+str(t.top_index)
        prob.readable_label = t.label+' '+str(t.top_index)
        prob.top_solution_number = 1
        prob.save()

        compileasy(prob.mc_problem_text,prob.label)
        compileasy(prob.problem_text,prob.label)

        prob.display_problem_text=newtexcode(prob.problem_text,prob.label,'')
        prob.display_mc_problem_text=newtexcode(prob.mc_problem_text,prob.label,prob.answers())

        sol = Solution(solution_text = D['solution_text'],parent_problem = prob)
        sol.save()
        sol.solution_number = 1
        sol.authors.add(self.request.user)
        sol.problem_label = prob.label
        sol.display_solution_text = newsoltexcode(sol.solution_text,prob.label+'sol'+str(sol.solution_number))
        sol.save()
        prob.solutions.add(sol)
        prob.save()
        compileasy(sol.solution_text,prob.label,sol = "sol1")
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


# Create your views here.
@login_required
def typeview(request):
    userprofile,boolcreated = UserProfile.objects.get_or_create(user=request.user)
    allowed_types = list(userprofile.user_type_new.allowed_types.all())
    allowed_types = sorted(allowed_types,key=lambda x:(-x.is_contest,x.label))
    rows = []
    for i in allowed_types:
        P = i.problems.all()
        num_problems = P.count()
        num_untagged = P.filter(newtags__isnull = True).count()#
        num_nosolutions = P.filter(solutions__isnull = True).count()
        rows.append((i,num_untagged,num_nosolutions))
    template = loader.get_template('problemeditor/typeview.html')
    context = {'rows': rows, 'nbar': 'problemeditor'}
    return HttpResponse(template.render(context,request))

@login_required
def tagview(request,type):
    typ = get_object_or_404(Type, type = type)
    newtags = NewTag.objects.all().exclude(label = 'root').order_by('tag')
    rows = []
    probsoftype = Problem.objects.filter(type_new = typ)
    untagged = probsoftype.filter(newtags__isnull = True)
    num_untagged = untagged.count()
    for tag in newtags:#i
        T = tag.problems.filter(type_new = typ)#probsoftype.filter(newtags__in=[tag])
        num_problems = T.count()
        num_nosolutions = T.filter(solutions__isnull=True).count()
        if num_problems > 0:
            rows.append((goodurl(str(tag)),str(tag),num_nosolutions,num_problems))

    root_tag = NewTag.objects.get(label='root')
    rows1 = []
    for c1 in root_tag.children.all():
        T_startswith = probsoftype.filter(newtags__in = NewTag.objects.filter(tag__startswith = c1.tag))
        T = c1.problems.filter(type_new = typ)
        num_probs_sw = T_startswith.count()
        num_nosolutions_sw = T_startswith.filter(solutions__isnull = True).count()
        num_probs = T.count()
        num_nosolutions = T.filter(solutions__isnull = True).count()
        if num_probs_sw > 0:
            rows2 = []
            for c2 in c1.children.all():
                T_startswith2 = probsoftype.filter(newtags__in = NewTag.objects.filter(tag__startswith = c2.tag))
                T2 = c2.problems.filter(type_new = typ)
                num_probs_sw2 = T_startswith2.count()
                num_nosolutions_sw2 = T_startswith2.filter(solutions__isnull = True).count()
                num_probs2 = T2.count()
                num_nosolutions2 = T2.filter(solutions__isnull = True).count()
                if num_probs_sw2 > 0:
                    rows3 = []
                    for c3 in c2.children.all():
                        T3 = c3.problems.filter(type_new = typ)
                        num_probs3 = T3.count()
                        num_nosolutions3 = T3.filter(solutions__isnull = True).count()
                        if num_probs3 > 0:
                            rows3.append((goodurl(str(c3)),c3,num_nosolutions3,num_probs3))
                    rows2.append((rows3,goodurl(str(c2)),c2,num_nosolutions_sw2,num_probs_sw2,num_nosolutions2,num_probs2))
            rows1.append((rows2,goodurl(str(c1)),c1,num_nosolutions_sw,num_probs_sw,num_nosolutions,num_probs))
    
    template=loader.get_template('problemeditor/tagview.html')
    context= {'rows': rows, 'type' : typ.type, 'typelabel':typ.label,'num_untagged': num_untagged, 'nbar': 'problemeditor','prefix':'bytag','rows1' : rows1}
    return HttpResponse(template.render(context,request))

@login_required
def testview(request,type):
    typ = get_object_or_404(Type, type = type)
    probsoftype = Problem.objects.filter(type_new = typ)
    num_untagged = probsoftype.filter(newtags__isnull = True).count()
    testlabels = []
    pot = list(probsoftype)
    for i in range(0,len(pot)):
        testlabels.append(pot[i].test_label)
    testlabels = list(set(testlabels))
    testlabels.sort()
    rows2 = []
    for i in range(0,len(testlabels)):
        rows2.append((testlabels[i],probsoftype.filter(test_label = testlabels[i]).filter(newtags__isnull = True).count(),probsoftype.filter(test_label = testlabels[i]).filter(solutions__isnull = True).count(),probsoftype.filter(test_label = testlabels[i]).count()))
    template = loader.get_template('problemeditor/testview.html')
    context = { 'type' : typ.type, 'typelabel':typ.label,'num_untagged': num_untagged, 'nbar': 'problemeditor','rows2':rows2,'prefix':'bytest'}
    return HttpResponse(template.render(context,request))

@login_required
def typetagview(request,type,tag):
    oldtag = tag
    tag = goodtag(tag)
    typ = get_object_or_404(Type, type = type)
    rows = []
    if tag != 'untagged':
        ttag = get_object_or_404(NewTag, tag = tag)
        problems = list(ttag.problems.filter(type_new = typ))
    else:
        problems = list(typ.problems.filter(newtags__isnull = True))
    problems = sorted(problems, key = lambda x:(x.problem_number,x.year))

    template = loader.get_template('problemeditor/typetagview.html')

    paginator = Paginator(problems,50)
    page = request.GET.get('page')
    try:
        prows = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        prows = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        prows = paginator.page(paginator.num_pages)
    context = {
        'rows' : prows,
        'type' : typ.type,
        'nbar': 'problemeditor',
        'tag':tag,
        'typelabel':typ.label,
        'tags':NewTag.objects.exclude(tag = 'root'),
        'oldtag': oldtag
        }
    return HttpResponse(template.render(context,request))

@login_required
def CMtypetagview(request,type,tag):
    tag = goodtag(tag)
    typ = get_object_or_404(Type, type = type)
    rows = []
    if tag != 'untagged':
        ttag = get_object_or_404(NewTag, tag = tag)
        problems = list(ttag.problems.filter(type_new = typ))
    else:
        problems = list(typ.problems.filter(newtags__isnull = True))
    problems = sorted(problems, key=lambda x:x.pk)
    template = loader.get_template('problemeditor/CMtypetagview.html')

    paginator = Paginator(problems,50)
    page = request.GET.get('page')
    try:
        prows = paginator.page(page)
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
    typ = get_object_or_404(Type, type=type)
    if testlabel != 'untagged':
        problems = list(Problem.objects.filter(test_label=testlabel))
    else:
        problems = typ.problems.filter(newtags__isnull=True)
    problems = sorted(problems, key=lambda x:(x.year,x.problem_number))

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

    template = loader.get_template('problemeditor/typetagview.html')
    context = {
        'rows' : prows,
        'nbar': 'problemeditor',
        'type':typ.type,
        'typelabel':typ.label,
        'tag':testlabel,
        'tags':NewTag.objects.exclude(tag='root')
        }
    return HttpResponse(template.render(context,request))

@login_required
def CMtopicview(request,type):#unapprovedview
    typ=get_object_or_404(Type, type=type)
    rows=[]
    problems=list(typ.problems.all())
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

    context={}
    context['rows']=prob.solutions.all()
    context['prob']=prob
    context['nbar']='problemeditor'
    context['typelabel']= typ.label
    context['label'] = label
    context['tag'] = tag
    context['tags'] = NewTag.objects.exclude(tag='root')
    userprofile,boolcreated = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'problemeditor/view.html', context)






class SolutionDeleteView(DeleteView):
    model = Solution
    template_name = 'problemeditor/solution_delete_form.html'
    success_url = "../../"

    def dispatch(self, *args, **kwargs):
        self.sol_id = kwargs['spk']
        if 'label' in kwargs:
            self.label = kwargs['label']
        if 'pk' in kwargs:
            self.pk = kwargs['pk']
        return super(SolutionDeleteView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Solution, pk=self.sol_id)
    def get_context_data(self, *args, **kwargs):
        context = super(SolutionDeleteView,self).get_context_data(*args,**kwargs)
        try:
            context['prob'] = get_object_or_404(Problem,label=self.label)
        except AttributeError:
            context['prob'] = get_object_or_404(Problem,pk=self.pk)
        context['solution'] = get_object_or_404(Solution, pk=self.sol_id)
        return context


@login_required
def untaggedview(request,type):
    typ=get_object_or_404(Type, type=type)
    rows=[]
    problems=list(Problem.objects.filter(type_new=typ).filter(newtags__isnull=True))
    problems=sorted(problems, key=lambda x:(x.year,x.problem_number))
    template=loader.get_template('problemeditor/typetagview.html')
    context= {'rows' : problems, 'type' : typ.type, 'nbar': 'problemeditor'}
    return HttpResponse(template.render(context,request))

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
    context['prob'] = prob
    context['nbar'] = 'problemeditor'
    context['breadcrumbs'] = breadcrumbs
    context['tags'] = NewTag.objects.exclude(tag='root')
    return render(request, 'problemeditor/detailedview.html', context)


@login_required
def addcontestview(request,type,num):
    typ=get_object_or_404(Type, type=type)
    num=int(num)
    if request.method == "POST":
        form=request.POST
        F=form#.cleaned_data
        formletter = F['formletter']
        year = F['year']
        label = F['year']+type+F['formletter']
        type2 = typ
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
            if formletter != "":
                t=Test(name=readablelabel)
            else:
                t=Test(name=year+' '+type2.label)
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
    if p.type_new not in request.user.userprofile.user_type_new.allowed_types.all():
        raise Http404("Unauthorized")
    if p.type_new.is_contest==True:
        return redirect('/problemeditor/contest/bytest/'+p.type_new.type+'/'+p.test_label+'/'+p.label+'/')
    else:
        return redirect('/problemeditor/CM/bytopic/'+p.type_new.type+'/'+str(p.pk)+'/')



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
                    num=1
                    prefix_pn=''
                    for i in range(1,len(problemtexts)):
                        ptext=problemtexts[i]
                        if '===' in ptext:
                            prefix_pn=ptext[ptext.index('===')+3]
                            num=1
                        else:
                            p=Problem(problem_text = problemtexts[i],
                                      answer='',
                                      sa_answer='',
                                      label=label+prefix_pn+str(num),
                                      readable_label=readablelabel+type2.readable_label_post_form+prefix_pn+str(num),
                                      type_new=type2,
                                      question_type_new=QuestionType.objects.get(question_type='short answer'),
                                      problem_number=num,
                                      year=year,
                                      form_letter=formletter,
                                      test_label=label,
                                      top_solution_number=0,
                                      problem_number_prefix=prefix_pn,
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
                            num+=1
                if type2.default_question_type=='pf':
                    num=1
                    prefix_pn=''
                    for i in range(1,len(problemtexts)):
                        ptext=problemtexts[i]
                        if '===' in ptext:
                            prefix_pn=ptext[ptext.index('===')+3]
                            num=1
                        else:
                            p=Problem(problem_text=problemtexts[i],
                                      label=label+prefix_pn+str(num),
                                      readable_label=readablelabel+type2.readable_label_post_form+prefix_pn+str(num),
                                      type_new=type2,
                                      question_type_new=QuestionType.objects.get(question_type='proof'),
                                      problem_number=num,
                                      year=year,
                                      form_letter=formletter,
                                      test_label=label,
                                      top_solution_number=0,
                                      problem_number_prefix=prefix_pn,
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
                            num+=1
                P=Problem.objects.filter(test_label=label)
                if len(P)>0:
                    if formletter != "":
                        t=Test(name=readablelabel)
                    else:
                        t=Test(name=year+' '+type2.label)
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

@login_required
def tameupload(request):
    form=UploadContestForm()
    return render(request, 'problemeditor/addcontestfileform.html', context={'form':form})


@login_required
def uploadpreview(request):
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
                problemtexts = str(f).split('=========')
                label = year+type2.type+formletter
                readablelabel = year + ' ' + type2.readable_label_pre_form + formletter
                readablelabel = readablelabel.rstrip()
                rows=[]
                if type2.default_question_type=='sa' or type2.default_question_type=='pf':
                    num=1
                    prefix_pn=''
                    for i in range(1,len(problemtexts)):
                        ptext=problemtexts[i]
                        if '===' in ptext:
                            prefix_pn=ptext[ptext.index('===')+3]
                            num=1
                        else:
                            rows.append((newtexcode(problemtexts[i],label+prefix_pn+str(num),''),
                                         label+prefix_pn+str(num),
                                         readablelabel+type2.readable_label_post_form+prefix_pn+str(num),
                                         ))
                            num+=1
#default_question_type
#testlabel
#prefix
#problem number...
                return render(request,'problemeditor/uploadpreview.html',context={'form':form,'rows':rows})
    return redirect('/problemeditor/')



# this is not working yet...upload preview needs to work better.
@login_required
def uploadsave(request):
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
                problemtexts = str(f).split('=========')
                label = year+type2.type+formletter
                readablelabel = year + ' ' + type2.readable_label_pre_form + formletter
                readablelabel = readablelabel.rstrip()
                if type2.default_question_type=='sa':
                    num=1
                    prefix_pn=''
                    for i in range(1,len(problemtexts)):
                        ptext=problemtexts[i]
                        if '===' in ptext:
                            prefix_pn=ptext[ptext.index('===')+3]
                            num=1
                        else:
                            p=Problem(problem_text = problemtexts[i],
                                      answer='',
                                      sa_answer='',
                                      label=label+prefix_pn+str(num),
                                      readable_label=readablelabel+type2.readable_label_post_form+prefix_pn+str(num),
                                      type_new=type2,
                                      question_type_new=QuestionType.objects.get(question_type='short answer'),
                                      problem_number=num,
                                      year=year,
                                      form_letter=formletter,
                                      test_label=label,
                                      top_solution_number=0,
                                      problem_number_prefix=prefix_pn,
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
                            num+=1
                if type2.default_question_type=='pf':
                    num=1
                    prefix_pn=''
                    for i in range(1,len(problemtexts)):
                        ptext=problemtexts[i]
                        if '===' in ptext:
                            prefix_pn=ptext[ptext.index('===')+3]
                            num=1
                        else:
                            p=Problem(problem_text=problemtexts[i],
                                      label=label+prefix_pn+str(num),
                                      readable_label=readablelabel+type2.readable_label_post_form+prefix_pn+str(num),
                                      type_new=type2,
                                      question_type_new=QuestionType.objects.get(question_type='proof'),
                                      problem_number=num,
                                      year=year,
                                      form_letter=formletter,
                                      test_label=label,
                                      top_solution_number=0,
                                      problem_number_prefix=prefix_pn,
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
                            num+=1
                P=Problem.objects.filter(test_label=label)
                if len(P)>0:
                    if formletter != "":
                        t=Test(name=readablelabel)
                    else:
                        t=Test(name=year+' '+type2.label)
                    t.save()
                for i in P:
                    t.problems.add(i)
                    t.types.add(i.type_new)
                t.save()
                tc,boolcreated=TestCollection.objects.get_or_create(name=type2.label)
                tc.tests.add(t)
                tc.save()
                return redirect('/problemeditor/')

@login_required
def duplicate_view(request,type_name):
    typ=get_object_or_404(Type,type=type_name)
    problems=typ.problem_set.annotate(c=Count('duplicate_problems')).filter(c__gt=0).order_by('year')
    return render(request,'problemeditor/duplicate_view.html',context={'typ':typ,'problems':problems})


#@user_passes_test(lambda u: u.is_superuser)
@login_required
def tageditview(request):
    root_tag=NewTag.objects.get(tag='root')
    context={'nbar': 'problemeditor','root_tag':root_tag}
    return render(request,'problemeditor/tageditview.html',context)


class TagUpdateView(UpdateView):
    model = NewTag
    form_class = NewTagForm##
    template_name = 'problemeditor/tag_edit_form.html'##

    def dispatch(self, *args, **kwargs):
        self.tag_id = kwargs['pk']
        return super(TagUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        form.instance.tag=str(form.instance)
        form.instance.save()
        if form.instance.level<3:
            for child in form.instance.children.all():
                child.tag=str(child)
                child.save()
                if child.level<3:
                    for cchild in child.children.all():
                        cchild.tag=str(cchild)
                        cchild.save()
        tag = NewTag.objects.get(id=self.tag_id)
        return redirect('/problemeditor/tags/')

    def get_object(self, queryset=None):
        return get_object_or_404(NewTag, pk=self.tag_id)

class TagCreateView(CreateView):
    model = NewTag
    form_class = AddNewTagForm
    template_name = 'problemeditor/tag_add_form.html'

    def dispatch(self, *args, **kwargs):
        self.parent_tag_id = kwargs['pk']
        return super(TagCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        parent_tag = NewTag.objects.get(id=self.parent_tag_id)
        if parent_tag.children.filter(label=form.instance.label).exists():
#            form.add_error('label',forms.ValidationError(('Tag already exists'), code='invalid'))

            messages.error(self.request,'Tag already exists')
            return redirect('/problemeditor/tags')

#            return super(TagCreateView,self).form_invalid(form)
        form.save()
        form.instance.parent = parent_tag
        form.instance.level = parent_tag.level + 1
        form.save()
        form.instance.tag = str(form.instance)
        form.instance.save()
        return redirect('/problemeditor/tags/')

#    def get_object(self, queryset=None):
#        return get_object_or_404(NewTag, pk=self.tag_id)
    def get_context_data(self, *args, **kwargs):
        context = super(TagCreateView,self).get_context_data(*args,**kwargs)
        context['parent_tag'] = NewTag.objects.get(id=self.parent_tag_id)
        return context

    def get_initial(self):
        return {'parent': NewTag.objects.get(id=self.parent_tag_id)}
#    def get_form_kwargs(self, **kwargs):
#        form_kwargs = super(TagCreateView, self).get_form_kwargs(**kwargs)
#        form_kwargs['parent'] = NewTag.objects.get(id=self.parent_tag_id)
#        print(form_kwargs)
#        return form_kwargs




class TagDeleteView(DeleteView):
    model = NewTag
    template_name = 'problemeditor/tag_delete_form.html'
    success_url = "/problemeditor/tags/"

    def dispatch(self, *args, **kwargs):
        self.tag_id = kwargs['pk']
        return super(TagDeleteView, self).dispatch(*args, **kwargs)


    def get_object(self, queryset=None):
        return get_object_or_404(NewTag, pk=self.tag_id)
    def get_context_data(self, *args, **kwargs):
        context = super(TagDeleteView,self).get_context_data(*args,**kwargs)
        context['tag'] = NewTag.objects.get(id=self.tag_id)
        return context

@login_required
def taginfoview(request,pk):
    types=request.user.userprofile.user_type_new.allowed_types.all()
    tag=get_object_or_404(NewTag,pk=pk)
    rows=[]
    for typ in types:
        rows.append((typ.label,tag.problems.filter(type_new=typ).count()))
    return render(request,'problemeditor/tag_info_view.html',{'rows':rows,'tag':tag})

class TagProblemList(ListView):
    model = Problem
    template_name = 'problemeditor/tag_problem_list.html'
    paginate_by = 10
    def get_queryset(self):
        self.tag = get_object_or_404(NewTag,pk=self.args[0])
        return self.tag.problems.filter(type_new__in=self.request.user.userprofile.user_type_new.allowed_types.all()).order_by('type_new')
    def get_context_data(self, **kwargs):
        context = super(TagProblemList, self).get_context_data(**kwargs)
        context['tag'] = self.tag
        context['nbar'] = 'problemeditor'
        return context

@login_required
def remove_duplicate_problem(request,**kwargs):
    pk = request.GET.get('pk','')
    dpk = request.GET.get('dpk','')
    prob=get_object_or_404(Problem,pk=pk)
    div_code = ""
    if request.user.userprofile.user_type_new.name == 'super' and  prob.duplicate_problems.filter(pk=dpk).exists():
        prob.duplicate_problems.remove(Problem.objects.get(pk=dpk))
        prob.save()
    return JsonResponse({'duplicate_problems':render_to_string('problemeditor/duplicate_problems.html',{'prob':prob,'request':request})})

@login_required
def add_duplicate_problem(request, **kwargs):
    pk = request.GET.get('original-prob_pk','')
    prob = get_object_or_404(Problem,pk=pk)
    linked_problem_label = request.GET.get("linked_problem_label","")
    if Problem.objects.filter(label=linked_problem_label).exists():
        q=Problem.objects.get(label=linked_problem_label)
        prob.duplicate_problems.add(q)
        prob.save()
        return JsonResponse({'duplicate_problems':render_to_string('problemeditor/duplicate_problems.html',{'prob':prob,'request':request}),'status':1,'prob_pk':pk})
    return JsonResponse({'status':0,'prob_pk':pk})

@login_required
def load_edit_answer(request,**kwargs):
    pk = request.GET.get('pk','')
    qt = request.GET.get('qt','')
    prob = get_object_or_404(Problem,pk=pk)
    if qt == 'mc':
        form = EditMCAnswer(instance = prob)
    else:
        form = EditSAAnswer(instance = prob)
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/modals/modal-edit-answer.html',{'form': form,'qt':qt})})

@login_required
def save_answer(request,**kwargs):
    pk = request.POST.get('ea_prob_pk','')
    prob =  get_object_or_404(Problem,pk=pk)
    qt = request.POST.get('ea_qt','')
    if qt == 'mc':
        form = EditMCAnswer(request.POST,instance = prob)
        form.save()
        return JsonResponse({'qt':qt,'pk':pk,'answer':form.instance.mc_answer})
    elif qt == 'sa':
        form = EditSAAnswer(request.POST,instance = prob)
        form.save()
        return JsonResponse({'qt':qt,'pk':pk,'answer':form.instance.sa_answer})

@login_required
def load_edit_latex(request,**kwargs):
    pk = request.GET.get('pk','')
    qt = request.GET.get('qt','')
    prob = get_object_or_404(Problem,pk=pk)
    if qt == 'mc':
        form = MCProblemTextForm(instance = prob)
    else:
        form = SAProblemTextForm(instance = prob)
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/modals/modal-edit-latex.html',{'form': form,'qt':qt})})


@login_required
def save_latex(request,**kwargs):
    pk = request.POST.get('pt_prob_pk','')
    prob =  get_object_or_404(Problem,pk=pk)
    qt = request.POST.get('pt_qt','')
    if qt == 'mc':
        form = MCProblemTextForm(request.POST,instance = prob)
        form.save()
        prob = form.instance
        prob.display_mc_problem_text = newtexcode(prob.mc_problem_text,prob.label,prob.answers())
        prob.save()
        compileasy(prob.mc_problem_text,prob.label)
        LogEntry.objects.log_action(
            user_id = request.user.id,
            content_type_id = ContentType.objects.get_for_model(prob).pk,
            object_id = prob.id,
            object_repr = prob.label,
            action_flag = CHANGE,
            change_message = "problemeditor/redirectproblem/"+str(prob.pk)+'/',
            )
        return JsonResponse({'qt':qt,'pk':pk,'prob-text':render_to_string('problemeditor/problem-snippets/components/autoescapelinebreaks.html',{'string_text':form.instance.display_mc_problem_text})})
    elif qt == 'sa':
        form = SAProblemTextForm(request.POST,instance = prob)
        form.save()
        prob = form.instance
        prob.display_problem_text = newtexcode(prob.problem_text,prob.label,'')
        prob.save()
        compileasy(prob.problem_text,prob.label)
        LogEntry.objects.log_action(
            user_id = request.user.id,
            content_type_id = ContentType.objects.get_for_model(prob).pk,
            object_id = prob.id,
            object_repr = prob.label,
            action_flag = CHANGE,
            change_message = "problemeditor/redirectproblem/"+str(prob.pk)+'/',
            )
        return JsonResponse({'qt':qt,'pk':pk,'prob-text':render_to_string('problemeditor/problem-snippets/components/autoescapelinebreaks.html',{'string_text':form.instance.display_problem_text})})

class SolutionView(DetailView):
    model = Problem
    template_name = 'problemeditor/problem-snippets/modals/load_sol.html'

    def dispatch(self, *args, **kwargs):
        self.item_id = kwargs['pk']
        return super(SolutionView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Problem, pk=self.item_id)

@login_required
def load_new_solution(request,**kwargs):
    pk = request.GET.get('pk','')
    prob = get_object_or_404(Problem,pk=pk)
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/modals/modal-new-solution.html',{'prob':prob})})

@login_required
def save_new_solution(request,**kwargs):
    pk = request.POST.get('ns-pk','')
    prob =  get_object_or_404(Problem,pk=pk)
    sol_text = request.POST.get("new_solution_text","")
    sol_num = prob.top_solution_number+1
    prob.top_solution_number = sol_num
    prob.save()
    sol = Solution(solution_text = sol_text,solution_number = sol_num,problem_label = prob.label,parent_problem = prob)
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
        action_flag = ADDITION,
        change_message = "problemeditor/redirectproblem/"+str(prob.pk)+'/',
        )
    return JsonResponse({'pk':pk,'sol_count':prob.solutions.count()})

def delete_sol(request,**kwargs):
    pk = request.POST.get('pk','')
    spk = request.POST.get('spk','')
    prob =  get_object_or_404(Problem,pk=pk)
    sol =  get_object_or_404(Solution,pk=spk)
    if request.user.userprofile.user_type_new.name == 'super' or request.user.userprofile.user_type_new.name == 'sitemanager' or request.user.userprofile.user_type_new.name == 'contestmanager':
        if prob.type_new in request.user.userprofile.user_type_new.allowed_types.all():
            LogEntry.objects.log_action(
                user_id = request.user.id,
                content_type_id = ContentType.objects.get_for_model(sol).pk,
                object_id = sol.id,
                object_repr = prob.label+' sol '+str(sol.solution_number),
                action_flag = DELETION,
                change_message = "problemeditor/redirectproblem/"+str(prob.pk)+'/',
                )
            sol.delete()
            return JsonResponse({'deleted':1,'sol_count': prob.solutions.count()})
    return JsonResponse({'deleted':0})

@login_required
def add_tag(request):
    tags = [(d,p) for d, p in request.POST.items() if d.startswith('addtag')]
    for i in tags:
        problem_pk=i[0].split('_')[1]
        prob=get_object_or_404(Problem,pk=problem_pk)
        tag = get_object_or_404(NewTag,pk=i[1])
        if tag.problems.filter(pk=problem_pk).exists():
            return JsonResponse({'prob_pk':problem_pk,'status':1,'tag_count':prob.newtags.count()})
        prob.newtags.add(tag)
        prob.save()
    return JsonResponse({'prob_pk':problem_pk,'status':0,'tag_list':render_to_string("problemeditor/problem-snippets/components/tag_snippet.html",{'prob':prob})})


@login_required
def delete_tag(request):
    delete_tag=request.POST.get('problem_tag_id','')
    del_list=delete_tag.split('_')
    problem_pk=del_list[1]
    prob=get_object_or_404(Problem,pk=problem_pk)
    tag_pk = del_list[2]
    tag = get_object_or_404(NewTag,pk=tag_pk)
    prob.newtags.remove(tag)
    prob.save()
    L= prob.newtags.all()
    response_string = render_to_string("problemeditor/problem-snippets/components/tag_snippet.html",{'prob':prob})
    return JsonResponse({'prob_pk':problem_pk,'tag_list':response_string,'tag_count':prob.newtags.count()})


@login_required
def load_edit_sol(request,**kwargs):
    pk = request.POST.get('pk','')
    spk = request.POST.get('spk','')
    prob =  get_object_or_404(Problem,pk=pk)
    sol =  get_object_or_404(Solution,pk=spk)
    form = SolutionForm(instance=sol)
    return JsonResponse({'sol_form':render_to_string('problemeditor/problem-snippets/modals/edit_sol_form.html',{'form':form,'prob':prob})})

@login_required
def save_sol(request,**kwargs):
    pk = request.POST.get('pk','')
    spk = request.POST.get('spk','')
    prob =  get_object_or_404(Problem,pk=pk)
    sol =  get_object_or_404(Solution,pk=spk)

    sol.solution_text = request.POST.get('solution_text')
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
        change_message = "problemeditor/redirectproblem/"+str(prob.pk)+'/',
        )
    return JsonResponse({'sol_text':render_to_string('problemeditor/problem-snippets/modals/soltext.html',{'solution':sol})})

@login_required
def change_qt(request,**kwargs):
    pk = request.POST.get('pk','')
    prob =  get_object_or_404(Problem,pk=pk)
    form = ChangeQuestionTypeForm1(instance=prob)
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/CMmodals/modal-change-qt.html',{'form':form})})

@login_required
def change_qt_load(request,**kwargs):
    pk = request.POST.get('pk','')
    qt_pk = request.POST.get('qt_pk','')
    prob =  get_object_or_404(Problem,pk=pk)
    qt = get_object_or_404(QuestionType,pk=qt_pk)
    if qt.question_type == "multiple choice":
        form = ChangeQuestionTypeForm2MC(instance=prob)
    elif qt.question_type == "multiple choice short answer":
        form = ChangeQuestionTypeForm2MCSA(instance=prob)
    elif qt.question_type == "short answer":
        form = ChangeQuestionTypeForm2SA(instance=prob)
    elif qt.question_type == "proof":
        form = ChangeQuestionTypeForm2PF(instance=prob)
    return JsonResponse({'cqt-form':render_to_string('problemeditor/problem-snippets/CMmodals/cqt-fields.html',{'form':form})})

@login_required
def save_qt(request,**kwargs):
    print(request.POST)
    qt = get_object_or_404(QuestionType,pk=request.POST.get('question_type_new',''))
    prob = get_object_or_404(Problem,pk=request.POST.get('cqt_prob_pk',''))
    prob.question_type_new = qt
    if qt.question_type == 'proof':
        prob.problem_text = request.POST.get('problem_text')
        prob.save()
        prob.display_problem_text = newtexcode(prob.problem_text,prob.label,'')
        prob.save()
        compileasy(prob.problem_text,prob.label)
    elif qt.question_type == 'short answer':
        prob.problem_text = request.POST.get('problem_text')
        prob.sa_answer = request.POST.get('sa_answer')
        prob.save()
        prob.display_problem_text = newtexcode(prob.problem_text,prob.label,'')
        prob.save()
        compileasy(prob.problem_text,prob.label)
    elif qt.question_type == 'multiple choice':
        prob.problem_text = request.POST.get('mc_problem_text')
        prob.mc_answer = request.POST.get('mc_answer')
        prob.answer_A = request.POST.get('answer_A')
        prob.answer_B = request.POST.get('answer_B')
        prob.answer_C = request.POST.get('answer_C')
        prob.answer_D = request.POST.get('answer_D')
        prob.answer_E = request.POST.get('answer_E')
        prob.save()
        prob.display_mc_problem_text = newtexcode(prob.mc_problem_text,prob.label,prob.answers())
        prob.save()
        compileasy(prob.mc_problem_text,prob.label)
    elif qt.question_type == 'multiple choice short answer':
        prob.problem_text = request.POST.get('mc_problem_text')
        prob.mc_answer = request.POST.get('mc_answer')
        prob.answer_A = request.POST.get('answer_A')
        prob.answer_B = request.POST.get('answer_B')
        prob.answer_C = request.POST.get('answer_C')
        prob.answer_D = request.POST.get('answer_D')
        prob.answer_E = request.POST.get('answer_E')
        prob.save()
        prob.display_mc_problem_text = newtexcode(prob.mc_problem_text,prob.label,prob.answers())
        prob.save()
        compileasy(prob.mc_problem_text,prob.label)
        prob.problem_text = request.POST.get('problem_text')
        prob.sa_answer = request.POST.get('sa_answer')
        prob.save()
        prob.display_problem_text = newtexcode(prob.problem_text,prob.label,'')
        prob.save()
        compileasy(prob.problem_text,prob.label)
    return JsonResponse({'problem-div':render_to_string('problemeditor/problem-snippets/CMcomponents/problemtext.html',{'prob':prob}),'qt':qt.question_type})

@login_required
def load_change_difficulty(request,**kwargs):
    prob = get_object_or_404(Problem,pk=request.POST.get('pk',''))
    form = DifficultyForm(instance = prob)
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/CMmodals/modal-change-difficulty.html',{'form':form})})

@login_required
def save_difficulty(request,**kwargs):
    prob = get_object_or_404(Problem,pk=request.POST.get('diff_prob_pk',''))
    prob.difficulty = request.POST.get('difficulty','')
    prob.save()
    return JsonResponse({'difficulty':prob.difficulty})

@login_required
def load_edit_review(request,**kwargs):
    prob = get_object_or_404(Problem,pk = request.POST.get('pk',''))
    review = get_object_or_404(ProblemApproval,pk = request.POST.get('review_pk',''))
    form = ApprovalForm(instance = review)
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/CMmodals/modal-review.html',{'form':form,'edit_review':1,'prob':prob})})

@login_required
def new_review(request,**kwargs):
    prob = get_object_or_404(Problem,pk = request.POST.get('pk',''))
    form = ApprovalForm()
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/CMmodals/modal-review.html',{'form':form,'prob':prob})})

@login_required
def save_review(request,**kwargs):
    prob = get_object_or_404(Problem,pk = request.POST.get('pk',''))
    review = get_object_or_404(ProblemApproval,pk = request.POST.get('rv_pk',''))
    review.author_name = request.POST.get('author_name','')
    review.approval_status = request.POST.get('approval_status','')
    review.save()
    LogEntry.objects.log_action(
        user_id = request.user.id,
        content_type_id = ContentType.objects.get_for_model(review).pk,
        object_id = review.id,
        object_repr = prob.label,
        action_flag = CHANGE,
        change_message = "problemeditor/redirectproblem/"+str(prob.pk)+'/',
        )
    return JsonResponse({'approvals':render_to_string('problemeditor/problem-snippets/CMcomponents/approval-div.html',{'prob':prob})})

@login_required
def save_new_review(request,**kwargs):
    prob = get_object_or_404(Problem,pk = request.POST.get('pk',''))
    review = ProblemApproval(author_name = request.POST.get('author_name',''),approval_status = request.POST.get('approval_status',''),approval_user=request.user)
    review.save()
    prob.approvals.add(review)
    prob.save()
    LogEntry.objects.log_action(
        user_id = request.user.id,
        content_type_id = ContentType.objects.get_for_model(review).pk,
        object_id = review.id,
        object_repr = prob.label,
        action_flag = ADDITION,
        change_message = "problemeditor/redirectproblem/"+str(prob.pk)+'/',
        )
    return JsonResponse({'approvals':render_to_string('problemeditor/problem-snippets/CMcomponents/approval-div.html',{'prob':prob})})

@login_required
def new_comment(request,**kwargs):
    prob = get_object_or_404(Problem,pk = request.POST.get('pk',''))
    form = CommentForm()
    return JsonResponse({'modal-html':render_to_string('problemeditor/problem-snippets/CMmodals/modal-new-comment.html',{'form':form,'prob':prob})})

@login_required
def save_comment(request,**kwargs):
    prob = get_object_or_404(Problem,pk = request.POST.get('nc-pk',''))
    com_form = CommentForm(request.POST)
    com_num=prob.comments.count()+1
    if com_form.is_valid():
        com = com_form.save(commit=False)
        com.comment_number=com_num
        com.author = request.user
        com.problem_label=prob.label
        com.save()
        prob.comments.add(com)
        prob.save()
        if prob.comments.count() > 1:
            return JsonResponse({'new_comment':0,'comment':render_to_string('problemeditor/problem-snippets/CMcomponents/comment.html',{'com':com_form.instance,'request':request,'prob':prob})})
        else:
            return JsonResponse({'new_comment':1,'comments-div':render_to_string('problemeditor/problem-snippets/CMcomponents/comments-div.html',{'prob':prob,'request':request})})
    return JsonResponse({})

def delete_comment(request, **kwargs):
    prob = get_object_or_404(Problem,pk = request.POST.get('pk',''))
    comment = get_object_or_404(Comment,pk = request.POST.get('com_pk',''))
    comment.delete()
    return JsonResponse({'comments-div':render_to_string('problemeditor/problem-snippets/CMcomponents/comments-div.html',{'prob':prob,'request':request})})
