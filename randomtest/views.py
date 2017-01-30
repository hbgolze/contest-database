from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader,RequestContext,Context

from django.template.loader import get_template

from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.admin import User
from django.contrib.auth.decorators import login_required
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from django.conf import settings

from subprocess import Popen,PIPE
import tempfile
import os

import logging
logger = logging.getLogger(__name__)

from .models import Problem, Tag, Type, Test, UserProfile, Response, Responses, QuestionType,Dropboxurl,get_or_create_up,UserResponse
from .forms import TestForm,UserForm,UserProfileForm,TestModelForm

from .utils import parsebool,newtexcode,newsoltexcode

from random import shuffle
import time
from datetime import datetime

# Create your views here.

class TestDelete(DeleteView):
    model = Test
    success_url = reverse_lazy('tableview')

@login_required
def deletetestresponses(request,pk):
    test = get_object_or_404(Test, pk=pk)
    if test.responses_set.count()<=1:
        test.delete()
    else:
        userprofile = get_or_create_up(request.user)
        testresponses = Responses.objects.filter(test=test).filter(user_profile=userprofile)
        if testresponses.count()>=1:
            testresponses.delete()
        userprofile.tests.remove(test)
    return redirect('/')

@login_required
def startform(request):
    if request.method=='POST':
        form=request.POST
        if form.get('startform','')=="start":
            testname=form.get('testname','')
            testtype=form.get('testtype','')
            tag=form.get('tag','')
            if tag=="Unspecified":
                tag=''

            num=form.get('numproblems','')
            if num is None or num==u'':
                num=10
            else:
                num=int(num)
                
            
            probbegin=form.get('probbegin','')
            if probbegin is None or probbegin==u'':
                probbegin=0
            else:
                probbegin=int(probbegin)

            probend=form.get('probend','')
            if probend is None or probend==u'':
                probend=10000
            else:
                probend=int(probend)

            yearbegin=form.get('yearbegin','')
            if yearbegin is None or yearbegin==u'':
                yearbegin=0
            else:
                yearbegin=int(yearbegin)

            yearend=form.get('yearend','')
            if yearend is None or yearend==u'':
                yearend=10000
            else:
                yearend=int(yearend)
            if len(tag)>0:
                P=Problem.objects.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend).filter(types__type=testtype)
                P=P.filter(tags__in=Tag.objects.filter(tag__startswith=tag)).distinct()
            else:
                P=Problem.objects.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend).filter(types__type=testtype).distinct()

            rows=[]

            P=list(P)
            shuffle(P)
            P=P[0:num]
            P=sorted(P,key=lambda x:(x.problem_number,x.year))
            T=Test(name=testname)
            T.save()
            for i in range(0,len(P)):
                T.problems.add(P[i])
            T.save()
            U,boolcreated=UserProfile.objects.get_or_create(user=request.user)
            U.tests.add(T)
            U.save()
            R=Responses(test=T,num_problems_correct=0)
            R.save()
            for i in range(0,len(P)):
                r=Response(response='',problem_label=P[i].label)
                r.response=form.get('answer'+P[i].label)
                if r.response==None:
                    r.response=''
                r.save()
                R.responses.add(r)
                rows.append((P[i].label, str(P[i].answer), ''))
            R.save()
            U.allresponses.add(R)
            U.save()
            T.types.add(Type.objects.get(type=testtype))
            T.save()
#            return testview(request,T.pk)
            return redirect('/test/'+str(T.pk)+'/')
        else:
            return testview(request,int(form.get('startform','')))
    else:
        types=list(Type.objects.all())
        tags=sorted(list(Tag.objects.all()),key=lambda x:x.tag)
        rows=[]
        for i in range(0,len(types)):
            rows.append((types[i].type,types[i].label))
        rows=sorted(rows,key=lambda x:x[1])
        template = loader.get_template('randomtest/startform2.html')
        context={'nbar' : 'newtest', 'rows' : rows,'tags' : tags}
        return HttpResponse(template.render(context,request))

#    P=Problem.objects.order_by('-year')

#    types = models.ManyToManyField(Type)

@login_required
def tagcounts(request):
    types=list(Type.objects.all())
    tags=list(Tag.objects.all())
    tags=sorted(tags,key=lambda x:x.tag)
    tagcounts=[]
    typeheaders=[]
    for i in range(0,len(types)):
        tagcounts.append([])
        typeheaders.append(types[i].type)
    for i in range(0,len(tags)):
        t=Problem.objects.filter(tags__in=[tags[i]])
        for j in range(0,len(types)):
            c=t.filter(types__in=[types[j]]).count()
            if c>0:
                tagcounts[j].append((tags[i].tag,c))
    tagrows=[]
    maxicounts=max([len(tagcounts[i]) for i in range(0,len(tagcounts))])
    for i in range(0,maxicounts):
        t=[[]]*len(tagcounts)
        for j in range(0,len(tagcounts)):
            if i<len(tagcounts[j]):
                ent=tagcounts[j][i]
            else:
                ent=('','')
            t[j]=ent
        tagrows.append(t)
    template = loader.get_template('randomtest/taglist.html')
    context={'nbar': 'newtest', 'typeheaders' : typeheaders,'tagrows':tagrows}
    return HttpResponse(template.render(context,request))

def tagcounts2(request):
    types=list(Type.objects.all())
    tags=list(Tag.objects.all())
    tags=sorted(tags,key=lambda x:x.tag)
    tagcounts=[]# will be a #types x #tags array
    typeheaders=[]
    for i in range(0,len(types)):
        tagcounts.append([])
        Dcounts={}
        typeheaders.append(types[i].type)
        p=Problem.objects.filter(types__type=types[i].type)
        for j in p:
            for k in j.tags.all():
                if k.tag in Dcounts:
                    Dcounts[k.tag]+=1
                else:
                    Dcounts[k.tag]=1
        for j in Dcounts:
            tagcounts[i].append((j,Dcounts[j]))
    tagrows=[]
    maxicounts=max([len(tagcounts[i]) for i in range(0,len(tagcounts))])
    for i in range(0,maxicounts):
        t=[[]]*len(tagcounts)
        for j in range(0,len(tagcounts)):
            if i<len(tagcounts[j]):
                ent=tagcounts[j][i]
            else:
                ent=('','')
            t[j]=ent
        tagrows.append(t)
    template = loader.get_template('randomtest/taglist.html')
    context={'nbar': 'newtest', 'typeheaders' : typeheaders,'tagrows':tagrows}
    return HttpResponse(template.render(context,request))

@login_required
def tableview(request):
    template=loader.get_template('randomtest/tableview.html')
    userprof = get_or_create_up(request.user)
    tests=list(userprof.tests.all())
    rows=[]
    for i in range(0,len(tests)):
#        if userprof.tests.filter(pk=tests[i].pk).count()==0:
#        userprof.tests.add(tests[i])#this line was indented
#        userprof.save()
#        testresponses = Responses.objects.filter(test=tests[i]).filter(user_profile=userprof)
        testresponses=userprof.allresponses.filter(test=tests[i])
        if testresponses.count()==0:
            allresponses=Responses(test=tests[i],num_problems_correct=0)
            allresponses.save()
            P=list(tests[i].problems.all())
            for j in range(0,len(P)):
                r=Response(response='',problem_label=P[j].label)
                r.save()
                allresponses.responses.add(r)
            allresponses.save()
            userprof.allresponses.add(allresponses)
            userprof.save()
        else:
            allresponses=Responses.objects.get(test=tests[i],user_profile=userprof)
        rows.append((tests[i].pk,tests[i].name,tests[i].types.all(),allresponses.num_problems_correct,tests[i].problems.count(),tests[i].created_date))
    studentusers=userprof.students.all()
    studentusernames=[]
    todaycorrect=str(userprof.responselog.filter(modified_date__date=datetime.today().date()).filter(correct=1).count())
    for i in studentusers:
        studentusernames.append(i.username)
    context= {'testcount':len(tests),'rows': rows, 'nbar': 'viewmytests', 'responselog':userprof.responselog.all().order_by('-modified_date')[0:50],'studentusernames' : studentusernames,'todaycorrect': todaycorrect}
    return HttpResponse(template.render(context,request))

@login_required
def testview(request,pk):
    test = get_object_or_404(Test, pk=pk)
    userprofile = get_or_create_up(request.user)
    if userprofile.tests.filter(pk=pk).count()==0:
        userprofile.tests.add(test)
    userprofile.save()
    testresponses = Responses.objects.filter(test=test).filter(user_profile=userprofile)
    if testresponses.count()==0:
        allresponses=Responses(test=test,num_problems_correct=0)
        allresponses.save()
        P=list(test.problems.all())
        for i in range(0,len(P)):
            r=Response(response='',problem_label=P[i].label)
            r.save()
            allresponses.responses.add(r)
        allresponses.save()
        userprofile.allresponses.add(allresponses)
        userprofile.save()
    else:
        allresponses=Responses.objects.get(test=test,user_profile=userprofile)
    
    dropboxpath = list(Dropboxurl.objects.all())[0].url
#test_label = models.CharField(max_length=50,blank=True)
#    response = models.CharField(max_length=10,blank=True)
#    problem_label = models.CharField(max_length=30)
#    modified_date = models.DateTimeField(default = timezone.now)
#    correct = BooleanField(default = 0)
    if request.method == "POST":
        form=request.POST
        P=list(test.problems.all())
        P=sorted(P,key=lambda x:(x.problem_number,x.year))
        num_correct=0
        rows=[]
        for i in range(0,len(P)):
            r=allresponses.responses.get(problem_label=P[i].label)
            tempanswer = form.get('answer'+P[i].label)
            if tempanswer != None and tempanswer !='':
                t=timezone.now()
                r.attempted = 1
                if r.response != tempanswer:
                    ur=UserResponse(test_label=test.name,test_pk=test.pk,response=tempanswer,problem_label=P[i].label,modified_date=t)
                    ur.save()
                    r.modified_date = t
                    r.response = tempanswer
                    if r.response==P[i].answer and P[i].question_type_new.question_type !='proof':
                        ur.correct=1
                        ur.save()
                    userprofile.responselog.add(ur)
            r.save()
            if r.response==P[i].answer and P[i].question_type_new.question_type !='proof':
                num_correct+=1
            rows.append((P[i].label,str(P[i].answer),r.response,P[i].question_type_new,P[i].pk,P[i].solutions.count(),r.attempted,r.modified_date))
        allresponses.num_problems_correct=num_correct
        allresponses.show_answer_marks=1
        allresponses.save()
        R=allresponses.responses
    else:
        P=list(test.problems.all())
        P=sorted(P,key=lambda x:(x.problem_number,x.year))
        R=allresponses.responses
        rows=[]
        for i in range(0,len(P)):
            r=R.get(problem_label=P[i].label)
            rows.append((P[i].label,str(P[i].answer),r.response,P[i].question_type_new,P[i].pk,P[i].solutions.count(),r.attempted,r.modified_date))
    return render(request, 'randomtest/testview.html',{'rows': rows,'pk' : pk,'nbar': 'viewmytests', 'dropboxpath': dropboxpath,'name':test.name,'show_marks':allresponses.show_answer_marks})



@login_required
def testeditview(request,pk):
    test = get_object_or_404(Test, pk=pk)
    userprofile = get_or_create_up(request.user)
    testresponses = Responses.objects.filter(test=test).filter(user_profile=userprofile)
    if testresponses.count()==0:
        allresponses=Responses(test=test,num_problems_correct=0)
        allresponses.save()
        P=list(test.problems.all())
        for i in range(0,len(P)):
            r=Response(response='',problem_label=P[i].label)
            r.save()
            allresponses.reponses.add(r)
        allresponses.save()
        userprofile.allresponses.add(allresponses)
        userprofile.save()
    else:
        allresponses=Responses.objects.get(test=test,user_profile=userprofile)
    msg=""
    dropboxpath = list(Dropboxurl.objects.all())[0].url
#Prepare for the add problems form
    types=list(Type.objects.all())
    taglist=sorted(list(Tag.objects.all()),key=lambda x:x.tag)
    testrows=[]
    for i in range(0,len(types)):
        testrows.append((types[i].type,types[i].label))
    testrows=sorted(testrows,key=lambda x:x[1])
        
    if request.method == "POST":
        rows=[]
        if request.POST.get("remove"):
            form=request.POST
            P=list(test.problems.all())
            for i in range(0,len(P)):
                if "chk"+P[i].label not in form:
                    test.problems.remove(P[i])
                    A=list(Responses.objects.filter(test=test))
                    for j in range(0,len(A)):
                        r=A[j].responses.get(problem_label=P[i].label)
                        r.delete()
            P=list(test.problems.all())
            P=sorted(P,key=lambda x:(x.problem_number,x.year))
            num_correct=0
            for i in range(0,len(P)):
                r=allresponses.responses.get(problem_label=P[i].label)
                if r.response==P[i].answer:
                    num_correct+=1
            allresponses.num_problems_correct=num_correct
            allresponses.save()
            R=allresponses.responses
            for i in range(0,len(P)):
                rows.append((P[i].label,str(P[i].answer),"checked=\"checked\""))
            msg="Problems Removed."
            test.refresh_types()
        elif request.POST.get("addproblems"):
            form=request.POST
            if form.get('startform','')=="start":
                testname=form.get('testname','')
                testtype=form.get('testtype','')
                tag=form.get('tag','')
                if tag=="Unspecified":
                    tag=''
                num=form.get('numproblems','')
                if num is None or num==u'':
                    num=10
                else:
                    num=int(num)
                probbegin=form.get('probbegin','')
                if probbegin is None or probbegin==u'':
                    probbegin=0
                else:
                    probbegin=int(probbegin)
                probend=form.get('probend','')
                if probend is None or probend==u'':
                    probend=10000
                else:
                    probend=int(probend)
                yearbegin=form.get('yearbegin','')
                if yearbegin is None or yearbegin==u'':
                    yearbegin=0
                else:
                    yearbegin=int(yearbegin)
                yearend=form.get('yearend','')
                if yearend is None or yearend==u'':
                    yearend=10000
                else:
                    yearend=int(yearend)

                if len(tag)>0:
                    matches=Problem.objects.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend).filter(types__type=testtype)
                    matches=matches.filter(tags__in=Tag.objects.filter(tag__startswith=tag))
                else:
                    matches=Problem.objects.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend).filter(types__type=testtype)
                matches.exclude(id__in=test.problems.all())


            matches=list(matches)
            shuffle(matches)
            matches=matches[0:num]
            for i in range(0,len(matches)):
                test.problems.add(matches[i])
                A=list(Responses.objects.filter(test=test))
                for j in range(0,len(A)):
                    r=Response(response='',problem_label=matches[i].label)
                    r.save()
                    A[j].responses.add(r)
                    A[j].save()
            test.save()
            P=test.problems.all()
            P=sorted(P,key=lambda x:(x.problem_number,x.year))
            for i in range(0,len(P)):
                rows.append((P[i].label,str(P[i].answer),"checked=\"checked\""))
            test.refresh_types()
        else:
            P=list(test.problems.all())
            P=sorted(P,key=lambda x:(x.problem_number,x.year))
            for i in range(0,len(P)):
                rows.append((P[i].label,str(P[i].answer),"checked=\"checked\""))
    else:
        P=list(test.problems.all())
        P=sorted(P,key=lambda x:(x.problem_number,x.year))
        rows=[]
        for i in range(0,len(P)):
            rows.append((P[i].label,str(P[i].answer),"checked=\"checked\""))
    return render(request, 'randomtest/testeditview.html',{'rows': rows,'pk' : pk,'nbar': 'viewmytests','msg':msg, 'dropboxpath': dropboxpath, 'testrows' : testrows,'taglist':taglist})

@login_required
def UpdatePassword(request):
    form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('/')
    return render(request, 'registration/change-password.html', {
        'form': form,
    })

@login_required
def latexview(request,pk):
    test = get_object_or_404(Test, pk=pk)
    P=list(test.problems.all())
    rows=[]
    include_problem_labels = True
    for i in range(0,len(P)):
        ptext=''
        if P[i].question_type_new.question_type=='multiple choice' or P[i].question_type_new.question_type=='multiple choice short answer':
            ptext=P[i].mc_problem_text
        else:
            ptext=P[i].problem_text
        rows.append((ptext,P[i].readable_label,P[i].answer_choices))
    if request.method == "GET":
        if request.GET.get('problemlabels')=='no':
            include_problem_labels = False
    return render(request, 'randomtest/latexview.html',{'name': test.name,'rows': rows,'pk' : pk,'nbar': 'viewmytests', 'include_problem_labels' : include_problem_labels})

@login_required
def readme(request):
    return render(request,'randomtest/readme.html',{'nbar':'newtest'})

def test_as_pdf(request, pk):
    test = get_object_or_404(Test, pk=pk)
    P=list(test.problems.all())
    rows=[]
    include_problem_labels = True
    for i in range(0,len(P)):
        ptext=''
        if P[i].question_type_new.question_type=='multiple choice' or P[i].question_type_new.question_type=='multiple choice short answer':
            ptext=P[i].mc_problem_text
        else:
            ptext=P[i].problem_text
        rows.append((ptext,P[i].readable_label,P[i].answer_choices))
    if request.method == "GET":
        if request.GET.get('problemlabels')=='no':
            include_problem_labels = False
    context = Context({  
            'name':test.name,
            'rows':rows,
            'pk':pk,
            'include_problem_labels':include_problem_labels,
            })
    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('randomtest/my_latex_template.tex')
    rendered_tpl = template.render(context).encode('utf-8')  
    # Python3 only. For python2 check out the docs!
    with tempfile.TemporaryDirectory() as tempdir:
        # Create subprocess, supress output with PIPE and
        # run latex twice to generate the TOC properly.
        # Finally read the generated pdf.
        fa=open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        logger.debug(os.listdir(tempdir))
        context = Context({  
                'name':test.name,
                'rows':rows,
                'pk':pk,
                'include_problem_labels':include_problem_labels,
                'tempdirect':tempdir,
                })
        template = get_template('randomtest/my_latex_template.tex')
        rendered_tpl = template.render(context).encode('utf-8')  
        ftex=open(os.path.join(tempdir,'texput.tex'),'wb')
        ftex.write(rendered_tpl)
        ftex.close()
        logger.debug(os.listdir(tempdir))
        for i in range(1):
            process = Popen(
                ['pdflatex', 'texput.tex'],
                stdin=PIPE,
                stdout=PIPE,
                cwd = tempdir,
            )
            stdout_value = process.communicate()[0]
        L=os.listdir(tempdir)
        logger.debug(os.listdir(tempdir))

        for i in range(0,len(L)):
            if L[i][-4:]=='.asy':
                process1 = Popen(
                    ['asy', L[i]],
                    stdin = PIPE,
                    stdout = PIPE,
                    cwd = tempdir,
                    )
                stdout_value = process1.communicate()[0]
        logger.debug(os.listdir(tempdir))
        for i in range(2):
            process2 = Popen(
                ['pdflatex', 'texput.tex'],
                stdin=PIPE,
                stdout=PIPE,
                cwd = tempdir,
            )
            stdout_value = process2.communicate()[0]
        logger.debug(os.listdir(tempdir))
        with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
            pdf = f.read()
    r = HttpResponse(content_type='application/pdf')  
    r.write(pdf)
    return r

@login_required
def solutionview(request,testpk,pk):
    prob = get_object_or_404(Problem, pk=pk)
    test = get_object_or_404(Test, pk=testpk)
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    sols=list(prob.solutions.all())
    sollist=[]
    rows=[]
    for sol in sols:
        rows.append((newsoltexcode(sol.solution_text,dropboxpath,prob.label+'sol'+str(sol.solution_number)),sol.pk))
    readablelabel=prob.readable_label.replace('\\#','#')
    texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,prob.answer_choices)
    context={}
    context['prob_latex']=texcode
    context['rows']=rows
    context['testpk']=testpk
    context['testname']=test.name
    context['nbar']='viewmytests'
    context['dropboxpath']=dropboxpath
    context['readablelabel']=readablelabel

    return render(request, 'randomtest/solview.html', context)

@login_required
def studenttableview(request,username):
    template=loader.get_template('randomtest/studenttableview.html')###
    curruserprof=get_or_create_up(request.user)
    user=get_object_or_404(User,username=username)
    if user not in curruserprof.students.all():
        return HttpResponse('Unauthorized', status=401)
    userprof = get_or_create_up(user)
    tests=list(userprof.tests.all())
    rows=[]
    for i in range(0,len(tests)):
        testresponses=userprof.allresponses.filter(test=tests[i])
        if testresponses.count()==0:
            allresponses=Responses(test=tests[i],num_problems_correct=0)
            allresponses.save()
            P=list(tests[i].problems.all())
            for j in range(0,len(P)):
                r=Response(response='',problem_label=P[j].label)
                r.save()
                allresponses.responses.add(r)
            allresponses.save()
            userprof.allresponses.add(allresponses)
            userprof.save()
        else:
            allresponses=Responses.objects.get(test=tests[i],user_profile=userprof)
        rows.append((tests[i].pk,tests[i].name,tests[i].types.all(),allresponses.num_problems_correct,tests[i].problems.count(),tests[i].created_date))
    todaycorrect=str(userprof.responselog.filter(modified_date__date=datetime.today().date()).filter(correct=1).count())
    context= {'testcount' : len(tests), 'rows' : rows, 'nbar' : 'viewmytests', 'responselog' : userprof.responselog.all().order_by('-modified_date')[0:50], 'username' : username, 'todaycorrect':todaycorrect}
    return HttpResponse(template.render(context,request))

@login_required
def studenttestview(request,username,pk):
    test = get_object_or_404(Test, pk=pk)
    curruserprof=get_or_create_up(request.user)
    user=get_object_or_404(User,username=username)
    if user not in curruserprof.students.all():
        return HttpResponse('Unauthorized', status=401)
    userprofile = get_or_create_up(user)
    testresponses = Responses.objects.filter(test=test).filter(user_profile=userprofile)
#    if testresponses.count()==0:
#        allresponses=Responses(test=test,num_problems_correct=0)
#        allresponses.save()
#        P=list(test.problems.all())
#        for i in range(0,len(P)):
#            r=Response(response='',problem_label=P[i].label)
#            r.save()
#            allresponses.responses.add(r)
#        allresponses.save()
#        userprofile.allresponses.add(allresponses)
#        userprofile.save()
#    else:
    allresponses = get_object_or_404(Responses,test=test,user_profile=userprofile)
    dropboxpath = list(Dropboxurl.objects.all())[0].url
    
    P=list(test.problems.all())
    P=sorted(P,key=lambda x:(x.problem_number,x.year))
    R=allresponses.responses
    rows=[]
    for i in range(0,len(P)):
        r=R.get(problem_label=P[i].label)
        texcode=newtexcode(P[i].problem_text,dropboxpath,P[i].label,P[i].answer_choices)
        mc_texcode=newtexcode(P[i].mc_problem_text,dropboxpath,P[i].label,P[i].answer_choices)
        readablelabel=P[i].readable_label.replace('\\#','#')
        rows.append((P[i].label,str(P[i].answer),r.response,P[i].question_type_new,P[i].pk,P[i].solutions.count(),r.attempted,r.modified_date,texcode,readablelabel,mc_texcode))
    return render(request, 'randomtest/studenttestview.html',{'rows': rows,'pk' : pk,'nbar': 'viewmytests', 'dropboxpath': dropboxpath,'name':test.name,'show_marks':allresponses.show_answer_marks})

