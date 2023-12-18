from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.template import loader

from django.template.loader import get_template,render_to_string
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.admin import User
from django.contrib.auth.decorators import login_required
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.db.models import Q

from django.utils import timezone
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import urllib

from .models import Contest,ContestYear,IndivProb_format1,Site,Organization
# Create your views here.

@login_required
def all_contests(request):
    return render(request,'results/all_contests.html',{'all_contests':Contest.objects.all()})

@login_required
def contest_view(request,contest_name):
    contest = get_object_or_404(Contest,name=contest_name)
    return render(request,'results/contest_view.html',{'contest':contest})

def fix_ranks(ranks):#t
#    ranks = [L[i][0] for i in range(0,len(L))]
    if ranks == []:
        return ranks
    new_ranks = [1]
    current_old_rank = ranks[0]
    current_rank = 1
    for i in range(1,len(ranks)):
        if ranks[i] > current_old_rank:
            new_ranks.append(i+1)
            current_old_rank = ranks[i]
            current_rank = i+1
        else:
            new_ranks.append(current_rank)
    return new_ranks

@login_required
def contestyear_view(request,contest_name,year):
    contest = get_object_or_404(Contest,name=contest_name)
    year = get_object_or_404(ContestYear,contest = contest, year=year)
    valid_divisions = []
    valid_sites = []
    divs = []
    site_pk = []
    for t in year.teams.all():
        divs.append(t.division)
        if t.new_site:
            site_pk.append(t.new_site.pk)
    divs = sorted(list(set(divs)))
    site_pk = list(set(site_pk))
    sites = Site.objects.filter(pk__in=site_pk)
    for i in sites:
        valid_sites.append([i,1])
    for i in divs:
        valid_divisions.append([i,1])
    multiple_divisions = False
    if len(valid_divisions) > 1:
        multiple_divisions = True
    multiple_sites = False
    if len(valid_sites) > 1:
        multiple_sites = True
    if request.method=='GET':
        if 'refresh' in request.GET:
            form = request.GET
            sites = form.getlist('site')
            divs = form.getlist('div')
            for i in valid_sites:
                if i[0].letter in sites:
                    i[1] = 1
                else:
                    i[1] = 0
            for i in valid_divisions:
                if i[0] in divs:
                    i[1] = 1
                else:
                    i[1] = 0
    checked_sites = []
    for i in valid_sites:
        if i[1] == 1:
            checked_sites.append(i[0].pk)
    checked_divs = []
    for i in valid_divisions:
        if i[1] == 1:
            checked_divs.append(i[0])
    if valid_sites == []:
        teams = year.teams.all()
    else:
        teams = year.teams.filter(new_site__pk__in = checked_sites)
    if valid_divisions != []:
        teams = teams.filter(division__in = checked_divs)
    teams = list(teams)
    new_ranks = fix_ranks([teams[i].overall_rank for i in range(0,len(teams))])
    results = [(new_ranks[i],teams[i]) for i in range(0,len(teams))]
#    results = sorted(teams,key = lambda x:(-x.total_score,-x.total_team_score,-x.total_relay_score,-x.total_indiv_score))
    
    return render(request,'results/contestyear_view.html',{'contest':contest,'year':year,'valid_divisions':valid_divisions,'valid_sites':valid_sites,'multiple_divisions':multiple_divisions,'multiple_sites': multiple_sites,'results':results})

#        print(sites)
#        print(divs)


@login_required
def organization_view(request,contest_name):
    contest = get_object_or_404(Contest,name=contest_name)
    orgs = contest.organizations.order_by('-last_year','name')
    return render(request,'results/organization_view.html',{'contest':contest,'orgs':orgs})

@login_required
def organization_team_view(request,contest_name,org_pk):
    contest = get_object_or_404(Contest,name=contest_name)
    org = get_object_or_404(Organization,pk = org_pk)
    teams = org.teams.order_by('year')
    return render(request,'results/organization_team_view.html',{'contest':contest,'org':org,'teams':teams})

@login_required
def individual_ranks(request,contest_name):
    contest = get_object_or_404(Contest, name=contest_name)
    indivs = IndivProb_format1.objects.order_by('perc_correct')
    return render(request,'results/indiv_view.html',{'contest':contest,'indivs':indivs})
