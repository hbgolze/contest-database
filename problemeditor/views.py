from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader,RequestContext
from django.contrib.auth.decorators import login_required

from randomtest.models import Problem, Tag, Type, Test, UserProfile, Solution,Dropboxurl
from .forms import ProblemForm,SolutionForm


# Create your views here.
@login_required
def typeview(request):
    obj=list(Type.objects.all())
    obj=sorted(obj,key=lambda x:x.type)
    rows=[]
    for i in range(0,len(obj)):
        P = Problem.objects.filter(types__in=[obj[i]])
        num_problems = P.count()
        untagged = P.filter(tags__isnull=True)
        num_untagged = untagged.count()
        nosolutions = P.filter(solutions__isnull=True)
        num_nosolutions = nosolutions.count()
        rows.append((obj[i].type,obj[i].label,num_untagged,num_nosolutions,num_problems))
    template=loader.get_template('problemeditor/typeview.html')
#    tests=list(UserProfile.objects.get(user=request.user).tests.all())
    context= {'rows': rows, 'nbar': 'problemeditor'}
    return HttpResponse(template.render(context,request))

@login_required
def tagview(request,type):
    typ=get_object_or_404(Type, type=type)
    obj=list(Tag.objects.all())
    obj=sorted(obj,key=lambda x:x.tag)
    rows=[]
    probsoftype=Problem.objects.filter(types__in=[typ])
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
            rows.append((str(obj[i]),num_nosolutions,num_problems))
    template=loader.get_template('problemeditor/tagview.html')
    context= {'rows': rows, 'type' : typ.type, 'typelabel':typ.label,'num_untagged': num_untagged, 'nbar': 'problemeditor','prefix':'bytag'}
    return HttpResponse(template.render(context,request))

@login_required
def testview(request,type):
    typ=get_object_or_404(Type, type=type)
    probsoftype=Problem.objects.filter(types__in=[typ])
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
    typ=get_object_or_404(Type, type=type)
    rows=[]
    if tag!='untagged':
        ttag=get_object_or_404(Tag, tag=tag)
        problems=list(Problem.objects.filter(types__in=[typ]).filter(tags__in=[ttag]))
    else:
        problems=list(Problem.objects.filter(types__in=[typ]).filter(tags__isnull=True))
    problems=sorted(problems, key=lambda x:(x.year,x.problem_number))
    for i in range(0,len(problems)):
        num_solutions=problems[i].solutions.count()
        rows.append((problems[i].label,problems[i].print_tags(),num_solutions))
    template=loader.get_template('problemeditor/typetagview.html')
    context= {'rows' : rows, 'type' : typ.type, 'nbar': 'problemeditor','tag':tag,'typelabel':typ.label}
    return HttpResponse(template.render(context,request))

@login_required
def problemview(request,type,tag,label):
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
    return render(request, 'problemeditor/view.html', {'form': form, 'nbar': 'problemeditor','dropboxpath':dropboxpath, 'typelabel':typ.label,'tag':tag,'label':label})


@login_required
def solutionview(request,type,tag,label):
    typ=get_object_or_404(Type, type=type)
    prob=get_object_or_404(Problem, label=label)
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        sollist = request.POST.getlist('solution_text')
#        sollist = [SolutionForm(solution_text=sollist[i],solution_number=i+1,problem_label=label) for i in range(0,len(sollist))]
        for i in range(0,len(sollist)):
            s=prob.solutions.get(solution_number=i+1)
            s.solution_text=sollist[i]
            s.save()
        prob.save()
############ISSSUES!!!!
#        form = ProblemForm(request.POST, instance=prob)
#        if form.is_valid():
#            problem = form.save()
#            problem.save()
#    else:
    sols=list(prob.solutions.all())
    sollist=[]

    rows=[]#

    for sol in sols:
        form = SolutionForm(instance=sol)
        sollist.append(form)
        rows.append((form,sol.solution_text))
    return render(request, 'problemeditor/solview.html', {'rows': rows,'label':label, 'nbar': 'problemeditor','dropboxpath':dropboxpath,'typelabel':typ.label,'tag':tag,'label':label})

@login_required
def newsolutionview(request,type,tag,label):
    typ=get_object_or_404(Type, type=type)
    prob=get_object_or_404(Problem, label=label)
    sol_num=prob.solutions.count()+1
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        sol_form = SolutionForm(request.POST)
        if sol_form.is_valid():
            sol = sol_form.save()
            sol.solution_number=sol_num
            sol.save()
            prob.solutions.add(sol)
            prob.save()
        return redirect(solutionview,type=type,label=label)
    else:
        sol=Solution(solution_text='', solution_number=sol_num, problem_label=label)
        form = SolutionForm(instance=sol)
    return render(request, 'problemeditor/newsol.html', {'form': form,'label':label, 'nbar': 'problemeditor','dropboxpath':dropboxpath,'typelabel':typ.label,'tag':tag,'label':label})

@login_required
def untaggedview(request,type):
    typ=get_object_or_404(Type, type=type)
    rows=[]
    problems=list(Problem.objects.filter(types__in=[typ]).filter(tags__isnull=True))
    problems=sorted(problems, key=lambda x:(x.year,x.problem_number))
    for i in range(0,len(problems)):
        num_solutions=problems[i].solutions.count()
        rows.append((problems[i].label,problems[i].print_tags(),num_solutions))
    template=loader.get_template('problemeditor/typetagview.html')
    context= {'rows' : rows, 'type' : typ.type, 'nbar': 'problemeditor'}
    return HttpResponse(template.render(context,request))

@login_required
def testlabelview(request,type,testlabel):
    typ=get_object_or_404(Type, type=type)
    rows=[]
    problems=list(Problem.objects.filter(test_label=testlabel))
    problems=sorted(problems, key=lambda x:(x.year,x.problem_number))
    for i in range(0,len(problems)):
        num_solutions=problems[i].solutions.count()
        rows.append((problems[i].label,problems[i].print_tags(),num_solutions))
    template=loader.get_template('problemeditor/typetagview.html')
    context= {'rows' : rows, 'type': typ.type, 'nbar': 'problemeditor','type':typ.type,'typelabel':typ.label,'tag':testlabel}
    return HttpResponse(template.render(context,request))
