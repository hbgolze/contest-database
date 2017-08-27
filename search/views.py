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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import logging
logger = logging.getLogger(__name__)

from randomtest.models import Problem, Tag, Type, Test, UserProfile, Response, Responses, QuestionType,get_or_create_up,UserResponse,ProblemGroup

from randomtest.utils import parsebool,newtexcode,newsoltexcode


@login_required
def searchform(request):
    userprofile = get_or_create_up(request.user)
    if userprofile.user_type == 'member':
        types=list(Type.objects.exclude(type__startswith="CM"))
    elif userprofile.user_type == 'manager':
        types=list(Type.objects.filter(type__startswith="CM"))
    elif userprofile.user_type == 'super':
        types=list(Type.objects.all())
    tags=sorted(list(Tag.objects.all()),key=lambda x:x.tag)
    rows=[]
    for i in range(0,len(types)):
        rows.append((types[i].type,types[i].label))
    rows=sorted(rows,key=lambda x:x[1])
    template = loader.get_template('search/searchform.html')
    context={'nbar' : 'search', 'rows' : rows,'tags' : tags}
    return HttpResponse(template.render(context,request))

@login_required
def searchresults(request):
    userprofile = get_or_create_up(request.user)
    if request.method=='POST':
        form=request.POST
        next = form.get('next', '')
        next = next[next.index('?'):next.index('\'>')]
        for i in form:
            if 'problemgroup' in i:
                pk = i.split('_')[1]
                prob = Problem.objects.get(pk=pk)
                gpk = form[i]
                probgroup = ProblemGroup.objects.get(pk=gpk)
                probgroup.problems.add(prob)
                probgroup.save()
        return HttpResponseRedirect(next)
    if request.method=='GET':
        page = request.GET.get('page')
        z=request.GET.copy()
        if 'page' in z:
            del(z['page'])
        current_url=z.urlencode()
        form=request.GET
        if form.get('searchform','')=="start":
            testtype = form.get('testtype','')

            searchterm = form.get('keywords','')
            if searchterm is None or searchterm==u'':
                keywords=[]
            else:
                keywords=searchterm.split(' ')

            tag=form.get('tag','')
            if tag=="Unspecified":
                tag=''

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

            for i in keywords:
                P=P.filter(Q(problem_text__contains=i)|Q(mc_problem_text__contains=i)|Q(label=i)|Q(test_label=i))
            P=list(P)
            P=sorted(P,key=lambda x:(x.problem_number,x.year))
            probgroups = userprofile.problem_groups
            paginator=Paginator(P,25)
            page = request.GET.get('page')
            try:
                prows=paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                prows = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                prows = paginator.page(paginator.num_pages)
            template = loader.get_template('search/searchresults.html')
            context={'nbar' : 'search', 'rows' : prows, 'searchterm': searchterm, 'current_url' : current_url,'matchnums':len(P), 'probgroups' : probgroups,'request' : request,
                     }
            return HttpResponse(template.render(context,request))
