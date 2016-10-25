from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader,RequestContext
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


from .models import Problem, Tag, Type, Test, UserProfile, Answer, QuestionType,Dropboxurl
from .forms import TestForm,UserForm,UserProfileForm,TestModelForm

from .utils import parsebool
from random import shuffle
import time

# Create your views here.

class TestDelete(DeleteView):
    model = Test
    success_url = reverse_lazy('tableview')

@login_required
def startform(request):
    if request.method=='POST':
        form=request.POST
        if form.get('startform','')=="start":
            testname=form.get('testname','')
            testtype=form.get('testtype','')
            tags=form.get('tag','')
            if tags is None:
                tags=''

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
            if len(tags)>0:
                boo,taglist=parsebool(tags)
                P=Problem.objects.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend).filter(types__type=testtype)
                if boo=='or':
                    P=P.filter(Q(tags__in=Tag.objects.filter(tag__in=taglist)) | Q(test_label__in=taglist) | Q(label__in=taglist))
                else:
                    for t in taglist:
                        P=P.filter(tags__in=Tag.objects.filter(tag__in=[t]))#this doesn't account for test/problem tags at the moment...(problem tags unnecessary with AND).
            else:
                P=Problem.objects.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend).filter(types__type=testtype)

            rows=[]

            template=loader.get_template('randomtest/testview.html')
            P=list(P)
            shuffle(P)
            P=P[0:num]
            P=sorted(P,key=lambda x:(x.problem_number,x.year))
            T=Test(name=testname,num_problems_correct=0)
            T.save()
            for i in range(0,len(P)):
                T.problems.add(P[i])
                a=Answer(answer='',problem_label=P[i].label)
                a.answer=form.get('answer'+P[i].label)
                if a.answer==None:
                    a.answer=''
                a.save()
                T.answers.add(a)
                rows.append((P[i].label, str(P[i].answer), ''))
            T.types.add(Type.objects.get(type=testtype))
            T.save()
            U,boolcreated=UserProfile.objects.get_or_create(user=request.user)
            U.tests.add(T)
            U.save()
            return testview(request,T.pk)
        else:
            return testview(request,int(form.get('startform','')))
    else:
        types=list(Type.objects.all())
        rows=[]
        for i in range(0,len(types)):
            rows.append((types[i].type,types[i].label))
        rows=sorted(rows,key=lambda x:x[1])
        template = loader.get_template('randomtest/startform2.html')
        context={'nbar': 'newtest','rows':rows}
        return HttpResponse(template.render(context,request))

#    P=Problem.objects.order_by('-year')

#    types = models.ManyToManyField(Type)

@login_required
def tableview(request):
    template=loader.get_template('randomtest/tableview.html')
    userprof,boolcreated=UserProfile.objects.get_or_create(user=request.user)
    if boolcreated==False:
        userprof.save()
    tests=userprof.tests.all()
    context= {'tests': tests, 'nbar': 'viewmytests'}
    return HttpResponse(template.render(context,request))

@login_required
def testview(request,pk):
    test = get_object_or_404(Test, pk=pk)
    dropboxpath = list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        form=request.POST
        P=list(test.problems.all())
        num_correct=0
        for i in range(0,len(P)):
            a=test.answers.get(problem_label=P[i].label)
            a.answer = form.get('answer'+P[i].label)
            if a.answer==None:
                a.answer=''
            a.save()
            if a.answer==P[i].answer and P[i].question_type.filter(question_type='proof').count()==0:
                num_correct+=1
        test.num_problems_correct=num_correct
        test.save()
        A=test.answers
        rows=[]
        for i in range(0,len(P)):
            rows.append((P[i].label,str(P[i].answer),A.get(problem_label=P[i].label).answer,list(P[i].question_type.all())[0]))
    else:
        P=list(test.problems.all())
        A=test.answers
        rows=[]
        for i in range(0,len(P)):
            rows.append((P[i].label,str(P[i].answer),A.get(problem_label=P[i].label).answer,list(P[i].question_type.all())[0]))
    return render(request, 'randomtest/testview.html',{'rows': rows,'pk' : pk,'nbar': 'viewmytests', 'dropboxpath': dropboxpath,'name':test.name})



@login_required
def testeditview(request,pk):
    test = get_object_or_404(Test, pk=pk)
    msg=""
    dropboxpath = list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        rows=[]
        if request.POST.get("remove"):
            form=request.POST
            P=list(test.problems.all())
            for i in range(0,len(P)):
                if "chk"+P[i].label not in form:
                    test.problems.remove(P[i])
            P=list(test.problems.all())
            num_correct=0
            for i in range(0,len(P)):
                a=test.answers.get(problem_label=P[i].label)
                a.answer = form.get('answer'+P[i].label)
                if a.answer==None:
                    a.answer=''
                a.save()
                if a.answer==P[i].answer:
                    num_correct+=1
            test.num_problems_correct=num_correct
            test.save()
            A=test.answers
            for i in range(0,len(P)):
                rows.append((P[i].label,str(P[i].answer),A.get(problem_label=P[i].label).answer,list(P[i].question_type.all())[0],"checked=\"checked\""))
            msg="Problems Removed."
        elif request.POST.get("save"):
            pass
        else:
            P=list(test.problems.all())
            A=test.answers
            for i in range(0,len(P)):
                rows.append((P[i].label,str(P[i].answer),A.get(problem_label=P[i].label).answer,list(P[i].question_type.all())[0],"checked=\"checked\""))
    else:
        P=list(test.problems.all())
        A=test.answers
        rows=[]
        for i in range(0,len(P)):
            rows.append((P[i].label,str(P[i].answer),A.get(problem_label=P[i].label).answer,list(P[i].question_type.all())[0],"checked=\"checked\""))
    return render(request, 'randomtest/testeditview.html',{'rows': rows,'pk' : pk,'nbar': 'viewmytests','msg':msg, 'dropboxpath': dropboxpath})

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
    if request.method == "POST":
        form=request.POST
        P=list(test.problems.all())
        rows=[]
        for i in range(0,len(P)):
            rows.append(P[i].problem_text)
    else:
        P=list(test.problems.all())
        rows=[]
        for i in range(0,len(P)):
            rows.append(P[i].problem_text)
    return render(request, 'randomtest/latexview.html',{'rows': rows,'pk' : pk,'nbar': 'viewmytests'})

@login_required
def readme(request):
    return render(request,'randomtest/readme.html',{'nbar':'newtest'})
