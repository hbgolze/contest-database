from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.template import loader,RequestContext,Context

from django.template.loader import get_template,render_to_string
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

from randomtest.models import Problem, Tag, Type, Test, UserProfile,  QuestionType,get_or_create_up,UserResponse,ProblemGroup,NewTag,Solution

from randomtest.utils import parsebool,newtexcode,newsoltexcode

from itertools import chain

@login_required
def searchform(request):
    form = request.GET
    advanced = False
    if 'advanced' in form:
        advanced = True
    userprofile = get_or_create_up(request.user)
    types = userprofile.user_type_new.allowed_types.all()
    tags = sorted(list(NewTag.objects.exclude(label='root')),key=lambda x:x.tag)
    template = loader.get_template('search/searchform.html')
    context = {'nbar' : 'search', 'types' : types,'tags' : tags, 'advanced': advanced,'userprofile':userprofile,}
    return HttpResponse(template.render(context,request))

@login_required
def searchresults(request):
    userprofile = get_or_create_up(request.user)
#    if request.method=='POST':
#        form=request.POST
#        next = form.get('next', '')
#        next = next[next.index('?'):next.index('\'>')]
#        for i in form:
#            if 'problemgroup' in i:
#                pk = i.split('_')[1]
#                prob = Problem.objects.get(pk=pk)
#                gpk = form[i]
#                probgroup = ProblemGroup.objects.get(pk=gpk)
#                probgroup.problems.add(prob)
#                probgroup.save()
#        return HttpResponseRedirect(next)
    if request.method=='GET':
        page = request.GET.get('page')
        z = request.GET.copy()
        if 'page' in z:
            del(z['page'])
        current_url = z.urlencode()
        form = request.GET
        if form.get('searchform','') == "start":
            testtype = form.get('tp','')
            type_args = testtype.split('_')
            round_or_type = type_args[0]
            rt_pk = type_args[1]

            searchterm = form.get('keywords','')
            if searchterm is None or searchterm == u'':
                keywords = []
            else:
                keywords = searchterm.split(' ')

            tag = form.get('tag','')
            if tag == "Unspecified":
                tag = ''

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

            sol_opts = form.get('sol_opts','')
            if sol_opts == "sols":
                P = Problem.objects.exclude(solutions=None)
            elif sol_opts == "nosols":
                P = Problem.objects.filter(solutions=None)
            else:
                P = Problem.objects.all()

            if len(tag)>0:
                if round_or_type == "T":
                    P = P.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend).filter(type_new__pk=rt_pk)#
                else:
                    P = P.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend).filter(round__pk=rt_pk)#
                P = P.filter(newtags__in=NewTag.objects.filter(tag__startswith=tag)).distinct()

            else:
                if round_or_type == "T":
                    P = P.filter(problem_number__gte = probbegin,problem_number__lte = probend).filter(year__gte = yearbegin,year__lte = yearend).filter(type_new__pk = rt_pk).distinct()#
                else:
                    P = P.filter(problem_number__gte = probbegin,problem_number__lte = probend).filter(year__gte = yearbegin,year__lte = yearend).filter(round__pk = rt_pk).distinct()#

#            if form.get('solution_search','') is not None:
#                S = Solution.objects.filter(parent_problem__problem_number__gte = probbegin,parent_problem__problem_number__lte = probend).filter(parent_problem__year__gte = yearbegin,parent_problem__year__lte = yearend).filter(parent_problem__types__type = testtype).distinct()
#                for i in keywords:
#                    S = S.filter(solution_text__contains = i)
#                P2 = Problem.objects.filter(id__in = S.values('parent_problem_id'))

            if 'solutionsearch' in form:
                if round_or_type == "T":
                    S = Solution.objects.filter(parent_problem__problem_number__gte = probbegin,parent_problem__problem_number__lte = probend).filter(parent_problem__year__gte = yearbegin,parent_problem__year__lte = yearend).filter(parent_problem__type_new__pk = rt_pk).distinct()
                else:
                    S = Solution.objects.filter(parent_problem__problem_number__gte = probbegin,parent_problem__problem_number__lte = probend).filter(parent_problem__year__gte = yearbegin,parent_problem__year__lte = yearend).filter(parent_problem__round__pk = rt_pk).distinct()
                for i in keywords:
                    S = S.filter(solution_text__contains = i)
                for i in keywords:
                    P = P.filter(Q(problem_text__contains = i)|Q(mc_problem_text__contains = i)|Q(label = i)|Q(test_label = i))
                P = Problem.objects.filter(Q(id__in = S.values('parent_problem_id'))|Q(id__in=P))
            else:
                for i in keywords:
                    P = P.filter(Q(problem_text__contains = i)|Q(mc_problem_text__contains = i)|Q(label = i)|Q(test_label = i))
            P = list(P)
            P = sorted(P,key = lambda x:(x.problem_number,x.year))
            owned_groups = userprofile.problem_groups.all()
            editable_groups = userprofile.editable_problem_groups.all()
            probgroups = list(chain(owned_groups,editable_groups))
            paginator = Paginator(P,25)
            page = request.GET.get('page')
            try:
                prows = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                prows = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                prows = paginator.page(paginator.num_pages)
            template = loader.get_template('search/searchresults.html')
            context={'nbar' : 'search', 'rows' : prows, 'searchterm': searchterm, 'current_url' : current_url,'matchnums':len(P), 'probgroups' : probgroups,'request' : request, 'tags':NewTag.objects.exclude(tag='root')}
            return HttpResponse(template.render(context,request))

@login_required
def advanced_searchresults(request):
    userprofile = get_or_create_up(request.user)
    if request.method=='GET':
        page = request.GET.get('page')
        z = request.GET.copy()
        if 'page' in z:
            del(z['page'])
        current_url = z.urlencode()
        form = request.GET
        if form.get('searchform','') == "start":
            testtypes = form.getlist('tp')
            type_pks = []
            round_pks = []
            for i in testtypes:
                type_args = i.split('_')
                if type_args[0] == 'T':
                    type_pks.append(type_args[1])
                else:
                    round_pks.append(type_args[1])

            searchterm = form.get('keywords','')
            if searchterm is None or searchterm == u'':
                keywords = []
            else:
                keywords = searchterm.split(' ')
#########TAGS
            tag_list = form.getlist('tag')

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

            sol_opts = form.get('sol_opts','')
            if sol_opts == "sols":
                P = Problem.objects.exclude(solutions = None)
            elif sol_opts == "nosols":
                P = Problem.objects.filter(solutions = None)
            else:
                P = Problem.objects.all()
            P = P.filter(problem_number__gte = probbegin,problem_number__lte = probend).filter(year__gte = yearbegin,year__lte = yearend)
            if len(type_pks) + len(round_pks) > 0:
                P = P.filter(Q(type_new__pk__in = type_pks)|Q(round__pk__in=round_pks))
            if len(tag_list) > 0:
                every_tag = []
                for t in tag_list:
                    every_tag += list(NewTag.objects.filter(tag__startswith = t))
                tag_pks = [t.pk for t in every_tag]
                P = P.filter(newtags__in = NewTag.objects.filter(pk__in = tag_pks)).distinct()



#            if 'solutionsearch' in form:
#                if round_or_type == "T":
#                    S = Solution.objects.filter(parent_problem__problem_number__gte = probbegin,parent_problem__problem_number__lte = probend).filter(parent_problem__year__gte = yearbegin,parent_problem__year__lte = yearend).filter(parent_problem__type_new__pk = rt_pk).distinct()
#                else:
#                    S = Solution.objects.filter(parent_problem__problem_number__gte = probbegin,parent_problem__problem_number__lte = probend).filter(parent_problem__year__gte = yearbegin,parent_problem__year__lte = yearend).filter(parent_problem__round__pk = rt_pk).distinct()
#                for i in keywords:
#                    S = S.filter(solution_text__contains = i)
#                for i in keywords:
#                    P = P.filter(Q(problem_text__contains = i)|Q(mc_problem_text__contains = i)|Q(label = i)|Q(test_label = i))
#                P = Problem.objects.filter(Q(id__in = S.values('parent_problem_id'))|Q(id__in=P))
#            else:
#                for i in keywords:
#                    P = P.filter(Q(problem_text__contains = i)|Q(mc_problem_text__contains = i)|Q(label = i)|Q(test_label = i))

            for i in keywords:
                P = P.filter(Q(problem_text__contains = i)|Q(mc_problem_text__contains = i)|Q(label = i)|Q(test_label = i))
            P = list(P)
            P = sorted(P,key = lambda x:(x.problem_number,x.year))
            owned_groups = userprofile.problem_groups.all()
            editable_groups = userprofile.editable_problem_groups.all()
            probgroups = list(chain(owned_groups,editable_groups))
            paginator = Paginator(P,25)
            page = request.GET.get('page')
            try:
                prows = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                prows = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                prows = paginator.page(paginator.num_pages)
            template = loader.get_template('search/searchresults.html')
            context={'nbar' : 'search', 'rows' : prows, 'searchterm': searchterm, 'current_url' : current_url,'matchnums':len(P), 'probgroups' : probgroups,'request' : request, 'tags':NewTag.objects.exclude(tag='root')}
            return HttpResponse(template.render(context,request))

@login_required
def add_to_group(request):
    problem_groups = [(d,p) for d, p in request.POST.items() if d.startswith('problemgroup')]
    for i in problem_groups:
        problem_pk=i[0].split('_')[1]
        prob=get_object_or_404(Problem,pk=problem_pk)
        p_group = get_object_or_404(ProblemGroup,pk=i[1])
        if p_group.problems.filter(pk=problem_pk).exists():
            return JsonResponse({'prob_pk':problem_pk,'status':1})
        p_group.problems.add(prob)
        p_group.save()
    return JsonResponse({'prob_pk':problem_pk,'status':0})

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
    return JsonResponse({'prob_pk':problem_pk,'status':0,'tag_list':render_to_string("search/tag_snippet.html",{'prob':prob})})


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
    response_string="<label for=\"tag-list-"+str(prob.pk)+"\">Current Tags</label>\n<ul id=\"tag-list-"+str(prob.pk)+"\">\n"
    L= prob.newtags.all()
    response_string = render_to_string("search/tag_snippet.html",{'prob':prob})
    return JsonResponse({'prob_pk':problem_pk,'tag_list':response_string,'tag_count':prob.newtags.count()})
