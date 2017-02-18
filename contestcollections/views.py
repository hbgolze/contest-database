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

from randomtest.models import Problem, Tag, Type, Test, UserProfile, Response, Responses, QuestionType,Dropboxurl,get_or_create_up,UserResponse,Sticky,TestCollection

from randomtest.utils import parsebool,newtexcode,newsoltexcode

from random import shuffle
import time
from datetime import datetime,timedelta

# Create your views here.                                                                            
@login_required
def tableview(request):
    TC=TestCollection.objects.order_by('name')
    rows=[]
    for i in TC:
        T=list(i.tests.order_by('name'))
        q=int(len(T)/4)
        leftover=len(T)%4
        lim=[0]
        for j in range(0,4):
            if j<leftover:
                lim.append(lim[-1]+q+1)
            else:
                lim.append(lim[-1]+q)
        T1=T[0:lim[1]]
        T2=T[lim[1]:lim[2]]
        T3=T[lim[2]:lim[3]]
        T4=T[lim[3]:]
        rows.append((i.name,T1,T2,T3,T4))
    return render(request, 'contestcollections/tableview.html',{'rows': rows,'nbar': 'contestcollection'})

@login_required
def testview(request,pk):
    test = get_object_or_404(Test, pk=pk)
    dropboxpath=list(Dropboxurl.objects.all())[0].url
    P=list(test.problems.all())
    P=sorted(P,key=lambda x:(x.problem_number,x.year))
    rows=[]
    for i in range(0,len(P)):
        texcode=newtexcode(P[i].problem_text,dropboxpath,P[i].label,'')
        mc_texcode=newtexcode(P[i].mc_problem_text,dropboxpath,P[i].label,P[i].answers())
        readablelabel=P[i].readable_label.replace('\\#','#')
        rows.append((P[i].label,str(P[i].answer),P[i].question_type_new,P[i].pk,P[i].solutions.count(),texcode,readablelabel,mc_texcode))
    return render(request, 'contestcollections/testview.html',{'rows': rows,'pk' : pk,'nbar': 'contestcollection', 'name':test.name})

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
    if prob.question_type_new.question_type=='multiple choice' or prob.question_type_new.question_type=='multiple choice short answer':
        texcode=newtexcode(prob.mc_problem_text,dropboxpath,prob.label,prob.answers())
    else:
        texcode=newtexcode(prob.problem_text,dropboxpath,prob.label,'')
    context={}
    context['prob_latex']=texcode
    context['rows']=rows
    context['testpk']=testpk
    context['testname']=test.name
    context['nbar']='viewmytests'
    context['dropboxpath']=dropboxpath
    context['readablelabel']=readablelabel

    return render(request, 'contestcollections/solview.html', context)
