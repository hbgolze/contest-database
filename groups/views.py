from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
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

from randomtest.models import Problem, Tag, Type, Test, UserProfile, QuestionType,get_or_create_up,UserResponse,Sticky,TestCollection,TestTimeStamp,Folder,UserTest,ProblemGroup,NewTag,NewResponse
from randomtest.utils import newtexcode
from .forms import GroupModelForm

from random import shuffle
import time
from datetime import datetime,timedelta

# Create your views here.

@login_required
def tableview(request):
    userprofile = get_or_create_up(request.user)
    if request.method=='POST':
        group_form = GroupModelForm(request.POST)
        if group_form.is_valid():
            group = group_form.save()
            userprofile.problem_groups.add(group)
            userprofile.save()
    prob_groups = userprofile.problem_groups.all()
    template=loader.get_template('groups/tableview.html')    
    group_inst = ProblemGroup(name='')
    form = GroupModelForm(instance=group_inst)
    context = {}
    context['form'] = form
    context['nbar'] = 'groups'
    context['probgroups'] =  prob_groups
    return HttpResponse(template.render(context,request))

@login_required
def tagtableview(request):
    userprofile = get_or_create_up(request.user)
    tags=NewTag.objects.all().exclude(tag='root').order_by('tag')
    template=loader.get_template('groups/tagtableview.html')
    context = {}
    context['nbar'] = 'groups'
    context['tags'] =  tags
    return HttpResponse(template.render(context,request))

@login_required
def viewproblemgroup(request,pk):
    userprofile = get_or_create_up(request.user)
    prob_group = get_object_or_404(ProblemGroup,pk=pk)
    if prob_group not in userprofile.problem_groups.all():
        return HttpResponse('Unauthorized', status=401)
    P = prob_group.problems.all()
    name = prob_group.name
    context = {}
    context['nbar'] = 'groups'
    context['prob_group'] = prob_group
    template = loader.get_template('groups/probgroupview.html')
    return HttpResponse(template.render(context,request))


@login_required
def viewtaggroup(request,pk):
    userprofile = get_or_create_up(request.user)
    tag = get_object_or_404(NewTag,pk=pk)
    if request.method == 'POST':
        if request.POST.get("newtest"):
            form = request.POST

            if "chk" in form:
                checked = form.getlist("chk")
                if len(checked)>0:
#                P = prob_group.problems.all()
                    testname = form.get('testname','')
                
                    t = Test(name = testname)
                    t.save()
                    for i in checked:
                        p = Problem.objects.get(label = i)
                        t.problems.add(p)
                    t.save()
                    userprofile.tests.add(t)
                    ti = TestTimeStamp(test_pk = t.pk)
                    ti.save()
                    userprofile.timestamps.add(ti)
                    ut = UserTest(test = t,num_probs = t.problems.count(),num_correct = 0,userprof = userprofile)
                    ut.save()
                    for i in t.problems.all():
                        r = NewResponse(response = '',problem_label = i.label,problem = i,usertest = ut)
                        r.save()
                    t.save()
#                    userprofile.usertests.add(ut)
                    userprofile.save()            
                    return redirect('/test/'+str(ut.pk)+'/')
    P = tag.problems.filter(type_new__in = userprofile.user_type_new.allowed_types.all())
    context = {}
    if request.method == 'GET':
        if "updatetypes" in request.GET:
            form = request.GET
            include_types_names = form.getlist('includetypes')
            include_types = Type.objects.filter(type__in = include_types_names)
            P = P.filter(type_new__in = include_types)
            context['include_types'] = include_types
    name = tag.tag
    context['rows'] = P
    context['name'] = name
    context['nbar'] = 'groups'
    context['pk'] = pk
    context['userprofile'] = userprofile
    template=loader.get_template('groups/taggroupview.html')
    return HttpResponse(template.render(context,request))


@login_required
def deletegroup(request,pk):
    pg = get_object_or_404(ProblemGroup, pk=pk)
    userprofile = get_or_create_up(request.user)
    if pg in userprofile.problem_groups.all():
        if pg.is_shared==0:
            pg.delete()
        else:
            userprofile.problem_groups.remove(pg)
    return redirect('/problemgroups/')
        
#use post to select problems for test...
#also edit search and 'contest collection' to allow adding to problemgroup...
#get templates and urls ready
#add to installed apps
#migrations

@login_required
def savegroup(request,**kwargs):
    form = request.POST
    prob_group = get_object_or_404(ProblemGroup,pk = form.get('startform'))
    userprofile = request.user.userprofile
    if prob_group in userprofile.problem_groups.all():
        P = prob_group.problems.all()
        checked = form.getlist("chk")
        for i in P:
            if i.label not in checked:
                prob_group.problems.remove(i)
    return JsonResponse({})

@login_required
def create_test(request,**kwargs):
    form = request.POST
    userprofile = request.user.userprofile
    if "chk" in form:
        checked = form.getlist("chk")
        if len(checked)>0:
            testname = form.get('testname','')
            t = Test(name = testname)
            t.save()
            for i in checked:
                p = Problem.objects.get(label = i)
                t.problems.add(p)
            t.save()
            userprofile.tests.add(t)
            ti = TestTimeStamp(test_pk = t.pk)
            ti.save()
            userprofile.timestamps.add(ti)
            ut = UserTest(test = t,num_probs = t.problems.count(),num_correct = 0,userprof = userprofile)
            ut.save()
            for i in t.problems.all():
                r = NewResponse(response = '',problem_label = i.label,problem = i,usertest = ut)
                r.save()
            t.save()
            userprofile.save()            
            return JsonResponse({'url':'/randomtest/test/'+str(ut.pk)+'/'})
    return JsonResponse({'error-message':'No problems checked!'})
