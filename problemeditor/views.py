from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader,RequestContext
from django.contrib.auth.decorators import login_required

from randomtest.models import Problem, Tag, Type, Test, UserProfile, Solution,Dropboxurl
from .forms import ProblemForm,SolutionForm,ProblemTextForm
from randomtest.utils import asyreplacementindexes,ansscrape

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
def testlabelview(request,type,testlabel):
    typ=get_object_or_404(Type, type=type)
    rows=[]
    if testlabel!='untagged':
        problems=list(Problem.objects.filter(test_label=testlabel))
    else:
        problems=list(Problem.objects.filter(types__in=[typ]).filter(tags__isnull=True))
    problems=sorted(problems, key=lambda x:(x.year,x.problem_number))
    for i in range(0,len(problems)):
        num_solutions=problems[i].solutions.count()
        rows.append((problems[i].label,problems[i].print_tags(),num_solutions))
    template=loader.get_template('problemeditor/typetagview.html')
    context= {'rows' : rows, 'type': typ.type, 'nbar': 'problemeditor','type':typ.type,'typelabel':typ.label,'tag':testlabel}
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
    texcode=form.instance.problem_text
    repl=asyreplacementindexes(texcode)
    newtexcode=''
    if len(repl)==0:
        newtexcode=texcode
    else:
        newtexcode=texcode[0:repl[0][0]]
        for i in range(0,len(repl)-1):
            newtexcode+='<img class=\"displayed\" src=\"'+dropboxpath+label+'-'+str(i+1)+'.png\"/>'
            newtexcode+=texcode[repl[i][1]:repl[i+1][0]]
        newtexcode+='<img class=\"displayed\" src=\"'+dropboxpath+label+'-'+str(len(repl))+'.png\"/>'
        newtexcode+=texcode[repl[-1][1]:]
    newtexcode+=ansscrape(form.instance.answer_choices)
    readablelabel=form.instance.readable_label.replace('\\#','#')
    return render(request, 'problemeditor/view.html', {'form': form, 'nbar': 'problemeditor','dropboxpath':dropboxpath, 'typelabel':typ.label,'tag':tag,'label':label,'prob_latex':newtexcode,'readablelabel':readablelabel})

@login_required
def editproblemtextview(request,type,tag,label):
    typ=get_object_or_404(Type, type=type)
    prob=get_object_or_404(Problem, label=label)
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        form = ProblemTextForm(request.POST, instance=prob)
        if form.is_valid():
            problem = form.save()
            problem.save()
    else:
        form = ProblemTextForm(instance=prob)
    texcode=form.instance.problem_text
    repl=asyreplacementindexes(texcode)
    newtexcode=''
    if len(repl)==0:
        newtexcode=texcode
    else:
        newtexcode=texcode[0:repl[0][0]]
        for i in range(0,len(repl)-1):
            newtexcode+='<img class=\"displayed\" src=\"'+dropboxpath+label+'-'+str(i+1)+'.png\"/>'
            newtexcode+=texcode[repl[i][1]:repl[i+1][0]]
        newtexcode+='<img class=\"displayed\" src=\"'+dropboxpath+label+'-'+str(len(repl))+'.png\"/>'
        newtexcode+=texcode[repl[-1][1]:]
    newtexcode+=ansscrape(form.instance.answer_choices)
    readablelabel=form.instance.readable_label.replace('\\#','#')
    return render(request, 'problemeditor/editproblemtext.html', {'form': form, 'nbar': 'problemeditor','dropboxpath':dropboxpath, 'typelabel':typ.label,'label':label,'tag':tag,'prob_latex':newtexcode,'readablelabel':readablelabel})


@login_required
def solutionview(request,type,tag,label):
    typ=get_object_or_404(Type, type=type)
    prob=get_object_or_404(Problem, label=label)
    dropboxpath=list(Dropboxurl.objects.all())[0].url
#    if request.method == "POST":
#        sollist = request.POST.getlist('solution_text')
#        for i in range(0,len(sollist)):
#            s=prob.solutions.get(solution_number=i+1)
#            s.solution_text=sollist[i]
#            s.save()
#        prob.save()
    sols=list(prob.solutions.all())
    sollist=[]

    rows=[]#

    for sol in sols:
#        form = SolutionForm(instance=sol)
#        sollist.append(form)
        rows.append((sol.solution_text,sol.pk))

    texcode=prob.problem_text
    repl=asyreplacementindexes(texcode)
    newtexcode=''
    if len(repl)==0:
        newtexcode=texcode
    else:
        newtexcode=texcode[0:repl[0][0]]
        for i in range(0,len(repl)-1):
            newtexcode+='<img class=\"displayed\" src=\"'+dropboxpath+label+'-'+str(i+1)+'.png\"/>'
            newtexcode+=texcode[repl[i][1]:repl[i+1][0]]
        newtexcode+='<img class=\"displayed\" src=\"'+dropboxpath+label+'-'+str(len(repl))+'.png\"/>'
        newtexcode+=texcode[repl[-1][1]:]
    newtexcode+=ansscrape(prob.answer_choices)
    readablelabel=prob.readable_label.replace('\\#','#')

    return render(request, 'problemeditor/solview.html', {'rows': rows,'label':label, 'nbar': 'problemeditor','dropboxpath':dropboxpath,'typelabel':typ.label,'tag':tag,'label':label,'answer':prob.answer, 'prob_latex':newtexcode,'readablelabel':readablelabel})

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
            sol.authors.add(request.user)
            sol.problem_label=label
            sol.save()
            prob.solutions.add(sol)
            prob.save()
        return redirect(solutionview,type=type,tag=tag,label=label)
    else:
        sol=Solution(solution_text='', solution_number=sol_num, problem_label=label)
        form = SolutionForm(instance=sol)

    texcode=prob.problem_text
    repl=asyreplacementindexes(texcode)
    newtexcode=''
    if len(repl)==0:
        newtexcode=texcode
    else:
        newtexcode=texcode[0:repl[0][0]]
        for i in range(0,len(repl)-1):
            newtexcode+='<img class=\"displayed\" src=\"'+dropboxpath+label+'-'+str(i+1)+'.png\"/>'
            newtexcode+=texcode[repl[i][1]:repl[i+1][0]]
        newtexcode+='<img class=\"displayed\" src=\"'+dropboxpath+label+'-'+str(len(repl))+'.png\"/>'
        newtexcode+=texcode[repl[-1][1]:]
    newtexcode+=ansscrape(prob.answer_choices)
    readablelabel=prob.readable_label.replace('\\#','#')

    return render(request, 'problemeditor/newsol.html', {'form': form,'label':label, 'nbar': 'problemeditor','dropboxpath':dropboxpath,'typelabel':typ.label,'tag':tag,'label':label,'answer':prob.answer, 'prob_latex':newtexcode,'readablelabel':readablelabel})

@login_required
def editsolutionview(request,type,tag,label,spk):
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

    texcode=prob.problem_text
    repl=asyreplacementindexes(texcode)
    newtexcode=''
    if len(repl)==0:
        newtexcode=texcode
    else:
        newtexcode=texcode[0:repl[0][0]]
        for i in range(0,len(repl)-1):
            newtexcode+='<img class=\"displayed\" src=\"'+dropboxpath+label+'-'+str(i+1)+'.png\"/>'
            newtexcode+=texcode[repl[i][1]:repl[i+1][0]]
        newtexcode+='<img class=\"displayed\" src=\"'+dropboxpath+label+'-'+str(len(repl))+'.png\"/>'
        newtexcode+=texcode[repl[-1][1]:]
    newtexcode+=ansscrape(prob.answer_choices)
    readablelabel=prob.readable_label.replace('\\#','#')

    return render(request, 'problemeditor/editsol.html', {'form': form,'label':label, 'nbar': 'problemeditor','dropboxpath':dropboxpath,'typelabel':typ.label,'tag':tag,'label':label,'answer':prob.answer, 'solution_text':sol.solution_text, 'prob_latex':newtexcode,'readablelabel':readablelabel})

@login_required
def deletesolutionview(request,type,tag,label,spk):#If solution_number is kept, this must be modified to adjust.
    sol = get_object_or_404(Solution, pk=spk)
    sol.delete()
    return redirect('../../')

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

