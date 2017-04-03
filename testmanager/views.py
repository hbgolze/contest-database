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

from randomtest.models import Problem, Tag, Type, Test, UserProfile, Response, Responses, QuestionType,Dropboxurl,get_or_create_up,UserResponse,Sticky,TestCollection,TestTimeStamp,Folder,UserTest

from .utils import parsebool,newtexcode,newsoltexcode,pointsum

from random import shuffle
import time
from datetime import datetime,timedelta

# Create your views here.


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
            ti=TestTimeStamp(test_pk=T.pk)
            ti.save()
            U.timestamps.add(ti)
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
            T.types.add(Type.objects.get(type=testtype))
            T.save()
            ut=UserTest(test = T,responses = R,num_probs = len(P),num_correct = 0)
            ut.save()
            U.usertests.add(ut)
            U.save()


#            return testview(request,T.pk)
            return redirect('/test/'+str(ut.pk)+'/')
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


@login_required
def tableview(request,**kwargs):
    context={}
    userprof = get_or_create_up(request.user)
    studentusers=userprof.students.all()
    studentusernames=[]
    for i in studentusers:
        studentusernames.append(i.username)
    context['studentusernames'] = studentusernames

    template=loader.get_template('testmanager/tableview.html')

    folders=userprof.folders.all()

    context['nbar'] = 'testmanager'
    context['folders'] = folders
    return HttpResponse(template.render(context,request))


@login_required
def testview(request,**kwargs):#switching to UserTest
    context={}
    pk=kwargs['pk']
    curruserprof=get_or_create_up(request.user)
    if 'username' in kwargs:
        username = kwargs['username']
        context['username'] = username
        user=get_object_or_404(User,username=username)
        if user not in curruserprof.students.all():
            return HttpResponse('Unauthorized', status=401)
        userprofile = get_or_create_up(user)
    else:
        userprofile = get_or_create_up(request.user)
    usertest = get_object_or_404(UserTest, pk=pk)
    if userprofile.usertests.filter(pk=pk).exists() == False:
        return HttpResponse('Unauthorized', status=401)
    test = get_object_or_404(Test, pk=usertest.test.pk)
    allresponses = usertest.responses
    
    
    dropboxpath = list(Dropboxurl.objects.all())[0].url
    if request.method == "POST" and 'username' not in kwargs:
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
                    pv=0
                    if P[i].type_new.type=='AIME':
                        if P[i].problem_number<=1:
                            pv=-3
                        elif P[i].problem_number<=5:
                            pv=1
                        elif P[i].problem_number<=10:
                            pv=3
                        else:
                            pv=5
                    ur=UserResponse(test_label=test.name,test_pk=usertest.pk,response=tempanswer,problem_label=P[i].label,modified_date=t,point_value=pv)
                    ur.save()
                    r.modified_date = t
                    r.response = tempanswer
                    if r.response==P[i].answer and P[i].question_type_new.question_type !='proof':
                        ur.correct=1
                        ur.save()
                    userprofile.responselog.add(ur)
            tempsticky = form.get('sticky'+P[i].label)
            if tempsticky=='on':
                if r.stickied == False:
                    s=Sticky(problem_label=P[i].label,sticky_date=timezone.now(),test_pk=usertest.pk,test_label=test.name)
                    s.save()
                    userprofile.stickies.add(s)
                r.stickied = True
            else:
                if r.stickied == True:
                    try:
                        s=Sticky.objects.get(problem_label=P[i].label,test_pk=usertest.pk)
                        s.delete()
                    except Sticky.DoesNotExist:
                        s=None
                r.stickied = False
            r.save()
            if r.response==P[i].answer and P[i].question_type_new.question_type !='proof':
                num_correct+=1
            if P[i].question_type_new.question_type=='multiple choice' or P[i].question_type_new.question_type=='multiple choice short answer':
                texcode=newtexcode(P[i].mc_problem_text,dropboxpath,P[i].label,P[i].answers())
            else:
                texcode=newtexcode(P[i].problem_text,dropboxpath,P[i].label,'')
            readablelabel=P[i].readable_label.replace('\\#','#')
            rows.append((texcode,P[i].label,str(P[i].answer),r.response,P[i].question_type_new,P[i].pk,P[i].solutions.count(),r.attempted,r.modified_date,r.stickied,readablelabel))
        allresponses.num_problems_correct=num_correct
        allresponses.show_answer_marks=1
        allresponses.save()
        usertest.num_correct = num_correct
        usertest.save()
        R=allresponses.responses
    else:
        P=list(test.problems.all())
        P=sorted(P,key=lambda x:(x.problem_number,x.year))
        R=allresponses.responses
        rows=[]
        for i in range(0,len(P)):
            r=R.get(problem_label=P[i].label)
            if P[i].question_type_new.question_type=='multiple choice' or P[i].question_type_new.question_type=='multiple choice short answer':
                texcode=newtexcode(P[i].mc_problem_text,dropboxpath,P[i].label,P[i].answers())
            else:
                texcode=newtexcode(P[i].problem_text,dropboxpath,P[i].label,'')
            readablelabel=P[i].readable_label.replace('\\#','#')
            rows.append((texcode,P[i].label,str(P[i].answer),r.response,P[i].question_type_new,P[i].pk,P[i].solutions.count(),r.attempted,r.modified_date,r.stickied,readablelabel))
    context['rows'] = rows
    context['pk'] = pk
    context['nbar'] = 'viewmytests'
    context['dropboxpath'] = dropboxpath
    context['name'] = test.name
    context['show_marks'] = allresponses.show_answer_marks
    return render(request, 'randomtest/testview.html',context)



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
def latexview(request,pk):
    test = get_object_or_404(Test, pk=pk)
    P=list(test.problems.all())
    rows=[]
    include_problem_labels = True
    for i in range(0,len(P)):
        ptext=''
        if P[i].question_type_new.question_type=='multiple choice' or P[i].question_type_new.question_type=='multiple choice short answer':
            ptext=P[i].mc_problem_text
            rows.append((ptext,P[i].readable_label,P[i].answers()))
        else:
            ptext=P[i].problem_text
            rows.append((ptext,P[i].readable_label,''))
    if request.method == "GET":
        if request.GET.get('problemlabels')=='no':
            include_problem_labels = False
    return render(request, 'randomtest/latexview.html',{'name': test.name,'rows': rows,'pk' : pk,'nbar': 'viewmytests', 'include_problem_labels' : include_problem_labels})

@login_required
def latexsolview(request,pk):
    test = get_object_or_404(Test, pk=pk)
    P=list(test.problems.all())
    rows=[]
    include_problem_labels = True
    for i in range(0,len(P)):
        ptext=''
        if P[i].question_type_new.question_type=='multiple choice' or P[i].question_type_new.question_type=='multiple choice short answer':
            ptext=P[i].mc_problem_text
            rows.append((ptext,P[i].readable_label,P[i].answers(),P[i].solutions.all()))
        else:
            ptext=P[i].problem_text
            rows.append((ptext,P[i].readable_label,'',P[i].solutions.all()))
    if request.method == "GET":
        if request.GET.get('problemlabels')=='no':
            include_problem_labels = False
    return render(request, 'randomtest/latexsolview.html',{'name': test.name,'rows': rows,'pk' : pk,'nbar': 'viewmytests', 'include_problem_labels' : include_problem_labels})

@login_required
def readme(request):
    return render(request,'randomtest/readme.html',{'nbar':'newtest'})

@login_required
def test_as_pdf(request, pk):
    test = get_object_or_404(Test, pk=pk)
    P=list(test.problems.all())
    rows=[]
    include_problem_labels = True
    for i in range(0,len(P)):
        ptext=''
        if P[i].question_type_new.question_type=='multiple choice' or P[i].question_type_new.question_type=='multiple choice short answer':
            ptext=P[i].mc_problem_text
            rows.append((ptext,P[i].readable_label,P[i].answers()))
        else:
            ptext=P[i].problem_text
            rows.append((ptext,P[i].readable_label,''))
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
def test_sol_as_pdf(request, pk):
    test = get_object_or_404(Test, pk=pk)
    P=list(test.problems.all())
    rows=[]
    include_problem_labels = True
    for i in range(0,len(P)):
        ptext=''
        if P[i].question_type_new.question_type=='multiple choice' or P[i].question_type_new.question_type=='multiple choice short answer':
            ptext=P[i].mc_problem_text
            rows.append((ptext,P[i].readable_label,P[i].answers(),P[i].solutions.all()))
        else:
            ptext=P[i].problem_text
            rows.append((ptext,P[i].readable_label,'',P[i].solutions.all()))
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
    template = get_template('randomtest/my_latex_sol_template.tex')
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
        template = get_template('randomtest/my_latex_sol_template.tex')
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
def solutionview(request,**kwargs):
    context={}
    if 'username' in kwargs:
        context['username'] = kwargs['username']
    testpk = kwargs['testpk']
    pk = kwargs['pk']
    prob = get_object_or_404(Problem, pk=pk)
    usertest = get_object_or_404(UserTest, pk=testpk)
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    sols=list(prob.solutions.all())
    sollist=[]
    rows=[]
    for sol in sols:
        rows.append((newsoltexcode(sol.solution_text,dropboxpath,prob.label+'sol'+str(sol.solution_number)),sol.pk))
    readablelabel=prob.readable_label.replace('\\#','#')
    if prob.question_type_new.question_type=='multiple choice' or prob.question_type_new.question_type=='multiple choice short answer':
        texcode=newtexcode(prob.mc_problem_text,dropboxpath,prob.label,prob.answers())
    else:
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,'')
    context['prob_latex']=texcode
    context['rows']=rows
    context['testpk']=testpk
    context['testname']=usertest.test.name
    context['nbar']='viewmytests'
    context['dropboxpath']=dropboxpath
    context['readablelabel']=readablelabel

    return render(request, 'randomtest/solview.html', context)

