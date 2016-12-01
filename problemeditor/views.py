from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader,RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from randomtest.models import Problem, Tag, Type, Test, UserProfile, Solution,Dropboxurl,Comment
from .forms import ProblemForm,SolutionForm,ProblemTextForm,AddProblemForm,DetailedProblemForm,CommentForm
from randomtest.utils import goodtag,goodurl,newtexcode

# Create your views here.
@login_required
def typeview(request):
    obj=list(Type.objects.all().exclude(type__startswith="CM"))
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
    obj2=list(Type.objects.filter(type__startswith="CM"))
    obj2=sorted(obj2,key=lambda x:x.type)
    rows2=[]
    for i in range(0,len(obj2)):
        P = Problem.objects.filter(types__in=[obj2[i]])
        num_problems = P.count()
        untagged = P.filter(tags__isnull=True)
        num_untagged = untagged.count()
        nosolutions = P.filter(solutions__isnull=True)
        num_nosolutions = nosolutions.count()
        notapproved = P.filter(approval_status=False)
        num_notapproved = notapproved.count()
        rows2.append((obj2[i].type,obj2[i].label,num_untagged,num_nosolutions,num_problems,num_notapproved))
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
            rows.append((goodurl(str(obj[i])),str(obj[i]),num_nosolutions,num_problems))
    template=loader.get_template('problemeditor/CMtagview.html')
    context= {'rows': rows, 'type' : typ.type, 'typelabel':typ.label,'num_untagged': num_untagged, 'nbar': 'problemeditor','prefix':'CMbytag'}
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
    tag=goodtag(tag)
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
def CMtypetagview(request,type,tag):
    tag=goodtag(tag)
    typ=get_object_or_404(Type, type=type)
    rows=[]
    if tag!='untagged':
        ttag=get_object_or_404(Tag, tag=tag)
        problems=list(Problem.objects.filter(types__in=[typ]).filter(tags__in=[ttag]))
    else:
        problems=list(Problem.objects.filter(types__in=[typ]).filter(tags__isnull=True))
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
        problems=list(Problem.objects.filter(types__in=[typ]).filter(tags__isnull=True))
    problems=sorted(problems, key=lambda x:(x.year,x.problem_number))
    for i in range(0,len(problems)):
        num_solutions=problems[i].solutions.count()
        rows.append((problems[i].label,problems[i].print_tags(),num_solutions))
    template=loader.get_template('problemeditor/typetagview.html')
    context= {'rows' : rows, 'type': typ.type, 'nbar': 'problemeditor','type':typ.type,'typelabel':typ.label,'tag':testlabel}
    return HttpResponse(template.render(context,request))

@login_required
def unapprovedview(request,type):
    typ=get_object_or_404(Type, type=type)
    rows=[]
    problems=list(Problem.objects.filter(types__in=[typ]).filter(approval_status=False))
    problems=sorted(problems, key=lambda x:(x.pk))
    for i in range(0,len(problems)):
        num_solutions=problems[i].solutions.count()
        rows.append((problems[i].label,problems[i].print_tags(),num_solutions,problems[i].pk))
    template=loader.get_template('problemeditor/unapprovedview.html')
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
    return render(request, 'problemeditor/view.html', {'form': form, 'nbar': 'problemeditor','dropboxpath':dropboxpath, 'typelabel':typ.label,'tag':tag,'label':label,'prob_latex':texcode,'readablelabel':readablelabel})

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
    else:
        form = ProblemTextForm(instance=prob)
    texcode=newtexcode(form.instance.problem_text,dropboxpath,label,prob.answer_choices)
    readablelabel=form.instance.readable_label.replace('\\#','#')
    breadcrumbs=[('/problemeditor/','Select Type'),('../../../',typ.label),('../../',tag),('../',readablelabel),]
    return render(request, 'problemeditor/editproblemtext.html', {'form': form, 'nbar': 'problemeditor','dropboxpath':dropboxpath, 'typelabel':typ.label,'label':label,'tag':tag,'prob_latex':texcode,'readablelabel':readablelabel,'breadcrumbs':breadcrumbs})

@login_required
def editproblemtextpkview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('/problemeditor/','Select Type'),('../../../',typ.label),('../../',kwargs['tag']),('../',str(prob.readable_label))]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('/problemeditor/','Select Type'),('../../','Unapproved '+typ.label+' Problems'),('../',str(prob.readable_label))]
    else:
        breadcrumbs=[('/problemeditor/','Select Type'),('../',str(prob.readable_label)),]
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        form = ProblemTextForm(request.POST, instance=prob)
        if form.is_valid():
            problem = form.save()
            problem.save()
    else:
        form = ProblemTextForm(instance=prob)
    texcode=newtexcode(form.instance.problem_text,dropboxpath,prob.label,prob.answer_choices)
    readablelabel=form.instance.readable_label.replace('\\#','#')
    return render(request, 'problemeditor/editproblemtext.html', {'form': form, 'nbar': 'problemeditor','dropboxpath':dropboxpath,'prob_latex':texcode,'readablelabel':readablelabel,'breadcrumbs':breadcrumbs})


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
    texcode=newtexcode(prob.problem_text,dropboxpath,label,prob.answer_choices)
    readablelabel=prob.readable_label.replace('\\#','#')
    return render(request, 'problemeditor/solview.html', {'rows': rows,'label':label, 'nbar': 'problemeditor','dropboxpath':dropboxpath,'typelabel':typ.label,'tag':tag,'label':label,'answer':prob.answer, 'prob_latex':texcode,'readablelabel':readablelabel})

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

    texcode=newtexcode(prob.problem_text,dropboxpath,label,prob.answer_choices)
    readablelabel=prob.readable_label.replace('\\#','#')
    breadcrumbs=[('../../../../',typ.label),('../../../',tag),('../','Solutions to '+readablelabel),]
    return render(request, 'problemeditor/newsol.html', {'form': form,'label':label, 'nbar': 'problemeditor','dropboxpath':dropboxpath,'typelabel':typ.label,'tag':tag,'label':label,'answer':prob.answer, 'prob_latex':texcode,'readablelabel':readablelabel,'breadcrumbs':breadcrumbs})

@login_required
def newsolutionpkview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../../',typ.label),('../../',kwargs['tag']),('../',str(prob.readable_label))]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../../','Unapproved '+typ.label+' Problems'),('../',prob.readable_label)]
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
        breadcrumbs=[('../../../','Unapproved '+typ.label+' Problems'),('../../',prob.readable_label),]
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
    problems=list(Problem.objects.filter(types__in=[typ]).filter(tags__isnull=True))
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
        breadcrumbs=[('../../','Unapproved '+typ.label+' Problems'),('../',prob.readable_label),]
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

    return render(request, 'problemeditor/newcom.html', {'form': com_form, 'nbar': 'problemeditor','dropboxpath':dropboxpath,'breadcrumbs':breadcrumbs})


@login_required
def detailedproblemview(request,**kwargs):
    pk=kwargs['pk']
    prob=get_object_or_404(Problem, pk=pk)
    if 'tag' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../',typ.label),('../',kwargs['tag']),]
    elif 'type' in kwargs:
        typ=get_object_or_404(Type, type=kwargs['type'])
        breadcrumbs=[('../','Unapproved '+typ.label+' Problems'),]
    else:
        breadcrumbs=[]
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    is_approved=prob.approval_status
    if request.method == "POST":#need more (was previously disabled)
        form=DetailedProblemForm(request.POST,instance=prob)
        if form.is_valid():
            problem = form.save()
            problem.save()
            if is_approved==False and problem.approval_status==True:
                problem.approval_user=request.user
                problem.save()
    else:
        form=DetailedProblemForm(instance=prob)
    #problem_text
    texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
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
    return render(request, 'problemeditor/detailedview.html', {'rows': rows,'nbar': 'problemeditor','dropboxpath':dropboxpath,'answer':prob.answer, 'prob_latex':texcode,'readablelabel':readablelabel,'form':form,'crows':crows,'breadcrumbs':breadcrumbs})

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

