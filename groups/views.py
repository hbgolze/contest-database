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
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from django.conf import settings

from subprocess import Popen,PIPE
import tempfile
import os

import logging
logger = logging.getLogger(__name__)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from randomtest.models import Problem, Tag, Type, Test, UserProfile, QuestionType,get_or_create_up,UserResponse,Sticky,TestCollection,Folder,UserTest,ProblemGroup,NewTag,NewResponse,ProblemGroupObject,AdvancedSearchPreset, Round,Solution
from randomtest.utils import newtexcode
from .forms import GroupModelForm,AddProblemsForm,EditProblemGroupNameForm,EditProblemGroupDescriptionForm

from random import shuffle
import time
from datetime import datetime,timedelta
from itertools import chain

# Create your views here.

@login_required
def tableview(request):
    userprofile = get_or_create_up(request.user)

    owned_pgs =  userprofile.problem_groups.all()
    co_owned_pgs =  userprofile.owned_problem_groups.all()
    editor_pgs =  userprofile.editable_problem_groups.all()
    readonly_pgs =  userprofile.readonly_problem_groups.all()

    template=loader.get_template('groups/tableview.html')
    group_inst = ProblemGroup(name='')##
    form = GroupModelForm(instance=group_inst)##
    context = {}
    context['form'] = form
    context['nbar'] = 'groups'
    context['owned_pgs'] = owned_pgs
    context['co_owned_pgs'] = co_owned_pgs
    context['editor_pgs'] = editor_pgs
    context['readonly_pgs'] = readonly_pgs
    context['archived'] = False
    return HttpResponse(template.render(context,request))

@login_required
def archivedtableview(request):
    userprofile = get_or_create_up(request.user)

    owned_pgs =  userprofile.archived_problem_groups.all()
    co_owned_pgs =  userprofile.archived_owned_problem_groups.all()
    editor_pgs =  userprofile.archived_editable_problem_groups.all()
    readonly_pgs =  userprofile.archived_readonly_problem_groups.all()

    template = loader.get_template('groups/tableview.html')
    context = {}
    context['nbar'] = 'groups'
    context['owned_pgs'] = owned_pgs
    context['co_owned_pgs'] = co_owned_pgs
    context['editor_pgs'] = editor_pgs
    context['readonly_pgs'] = readonly_pgs
    context['archived'] = True
    return HttpResponse(template.render(context,request))

@login_required
def tagtableview(request):
    userprofile = get_or_create_up(request.user)
    tags = NewTag.objects.all().exclude(tag = 'root').order_by('tag')
    template = loader.get_template('groups/tagtableview.html')
    context = {}
    context['nbar'] = 'groups'
    context['tags'] =  tags
    return HttpResponse(template.render(context,request))

@login_required
def viewproblemgroup(request,pk):
    userprofile = get_or_create_up(request.user)
    prob_group = get_object_or_404(ProblemGroup,pk=pk)
    if prob_group not in userprofile.problem_groups.all() and prob_group not in userprofile.owned_problem_groups.all() and prob_group not in userprofile.editable_problem_groups.all() and prob_group not in userprofile.readonly_problem_groups.all() and prob_group not in userprofile.archived_problem_groups.all() and prob_group not in userprofile.archived_owned_problem_groups.all() and prob_group not in userprofile.archived_editable_problem_groups.all() and prob_group not in userprofile.archived_readonly_problem_groups.all():
        return HttpResponse('Unauthorized', status=401)
    context = {}
    context['nbar'] = 'groups'
    context['prob_group'] = prob_group
    context['request'] = request
    owned_groups = userprofile.problem_groups.exclude(pk = pk)
    editable_groups = userprofile.editable_problem_groups.exclude(pk = pk)
    probgroups = list(chain(owned_groups,editable_groups))
    context['prob_groups'] = probgroups
    context['form'] = AddProblemsForm(userprofile=userprofile)
    if prob_group in userprofile.problem_groups.all() or prob_group in userprofile.owned_problem_groups.all() or  prob_group in userprofile.editable_problem_groups.all() or prob_group in userprofile.archived_problem_groups.all() or prob_group in userprofile.archived_owned_problem_groups.all() or  prob_group in userprofile.archived_editable_problem_groups.all():
        context['can_delete'] = 1
    if prob_group in userprofile.problem_groups.all() or prob_group in userprofile.archived_problem_groups.all():
        context['can_edit'] = 1
    template = loader.get_template('groups/probgroupview.html')
    return HttpResponse(template.render(context,request))



@login_required
def viewtaggroup(request,pk):
    userprofile = get_or_create_up(request.user)
    tag = get_object_or_404(NewTag,pk = pk)
    if request.method == 'POST':
        if request.POST.get("newtest"):
            form = request.POST

            if "chk" in form:
                checked = form.getlist("chk")
                if len(checked) > 0:
#                P = prob_group.problems.all()
                    testname = form.get('testname','')
                
                    t = Test(name = testname)
                    t.save()
                    for i in checked:
                        po = ProblemGroupObject.objects.get(pk = i)
                        t.problems.add(po.problem)###
                    t.save()
                    userprofile.tests.add(t)
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
    template = loader.get_template('groups/taggroupview.html')
    return HttpResponse(template.render(context,request))

@login_required
def edit_pg_view(request,pk):
    userprofile = get_or_create_up(request.user)
    prob_group = get_object_or_404(ProblemGroup,pk=pk)
    if prob_group not in userprofile.problem_groups.all() and prob_group not in userprofile.owned_problem_groups.all() and prob_group not in userprofile.editable_problem_groups.all() and prob_group not in userprofile.readonly_problem_groups.all() and prob_group not in userprofile.archived_problem_groups.all() and prob_group not in userprofile.archived_owned_problem_groups.all() and prob_group not in userprofile.archived_editable_problem_groups.all() and prob_group not in userprofile.archived_readonly_problem_groups.all():
        return HttpResponse('Unauthorized', status=401)

    problems = prob_group.problem_objects.all()

    paginator = Paginator(problems,50)
    page = request.GET.get('page')
    try:
        prows = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        prows = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        prows = paginator.page(paginator.num_pages)

    userprofile = request.user.userprofile
    owned_groups = userprofile.problem_groups.all()
    editable_groups = userprofile.editable_problem_groups.all()
    probgroups = list(chain(owned_groups,editable_groups))

    template = loader.get_template('groups/typetagview.html')
    context = {
        'rows' : prows,
        'nbar' : 'groups',
        'typelabel' : 'Problem Groups',
        'tag' : 'Problem Group: '+str(prob_group.name),
        'tags' : NewTag.objects.exclude(tag='root'),
        'probgroups':probgroups,
        }
    return HttpResponse(template.render(context,request))

@login_required
def newproblemgroup(request):
    userprofile = request.user.userprofile
    if request.method == 'POST':
        group_form = GroupModelForm(request.POST)
        if group_form.is_valid():
            group = group_form.save()
            userprofile.problem_groups.add(group)
            userprofile.save()
            return JsonResponse({'group-row':render_to_string('groups/grouptablerow.html',{'pg':group,'sharing_type':'own'})})

@login_required
def delete_group(request):
    pk = request.POST.get('pk','')
    pg = get_object_or_404(ProblemGroup, pk=pk)
    userprofile = request.user.userprofile
    if pg in userprofile.problem_groups.all():
        pg.delete()
    if pg in userprofile.archived_problem_groups.all():
        pg.delete()
    return JsonResponse({})


@login_required
def remove_group(request):
    pk = request.POST.get('pk','')
    pg = get_object_or_404(ProblemGroup, pk=pk)
    userprofile = request.user.userprofile
    if pg in userprofile.owned_problem_groups.all():
        userprofile.owned_problem_groups.remove(pg)
        userprofile.save()
    elif pg in userprofile.editable_problem_groups.all():
        userprofile.editable_problem_groups.remove(pg)
        userprofile.save()
    elif pg in userprofile.readonly_problem_groups.all():
        userprofile.readonly_problem_groups.remove(pg)
        userprofile.save()
    if pg in userprofile.archived_owned_problem_groups.all():
        userprofile.archived_owned_problem_groups.remove(pg)
        userprofile.save()
    elif pg in userprofile.archived_editable_problem_groups.all():
        userprofile.archived_editable_problem_groups.remove(pg)
        userprofile.save()
    elif pg in userprofile.archived_readonly_problem_groups.all():
        userprofile.archived_readonly_problem_groups.remove(pg)
        userprofile.save()
    return JsonResponse({})

@login_required
def archive_group(request):
    pk = request.POST.get('pk','')
    pg = get_object_or_404(ProblemGroup, pk=pk)
    userprofile = request.user.userprofile
    if pg in userprofile.problem_groups.all():
        userprofile.problem_groups.remove(pg)
        userprofile.archived_problem_groups.add(pg)
        userprofile.save()
    elif pg in userprofile.owned_problem_groups.all():
        userprofile.owned_problem_groups.remove(pg)
        userprofile.archived_owned_problem_groups.add(pg)
        userprofile.save()
    elif pg in userprofile.editable_problem_groups.all():
        userprofile.editable_problem_groups.remove(pg)
        userprofile.archived_editable_problem_groups.add(pg)
        userprofile.save()
    elif pg in userprofile.readonly_problem_groups.all():
        userprofile.readonly_problem_groups.remove(pg)
        userprofile.archived_readonly_problem_groups.add(pg)
        userprofile.save()
    return JsonResponse({})

@login_required
def unarchive_group(request):
    pk = request.POST.get('pk','')
    pg = get_object_or_404(ProblemGroup, pk=pk)
    userprofile = request.user.userprofile
    if pg in userprofile.archived_problem_groups.all():
        userprofile.archived_problem_groups.remove(pg)
        userprofile.problem_groups.add(pg)
        userprofile.save()
    elif pg in userprofile.archived_owned_problem_groups.all():
        userprofile.archived_owned_problem_groups.remove(pg)
        userprofile.owned_problem_groups.add(pg)
        userprofile.save()
    elif pg in userprofile.archived_editable_problem_groups.all():
        userprofile.archived_editable_problem_groups.remove(pg)
        userprofile.editable_problem_groups.add(pg)
        userprofile.save()
    elif pg in userprofile.archived_readonly_problem_groups.all():
        userprofile.archived_readonly_problem_groups.remove(pg)
        userprofile.readonly_problem_groups.add(pg)
        userprofile.save()
    return JsonResponse({})

#use post to select problems for test...
#also edit search and 'contest collection' to allow adding to problemgroup...
#get templates and urls ready
#add to installed apps
#migrations


###change problems to problem_objects
@login_required
def savegroup(request,**kwargs):
    form = request.POST
    prob_group = get_object_or_404(ProblemGroup,pk = form.get('startform'))
    userprofile = request.user.userprofile
    if prob_group in userprofile.problem_groups.all() or prob_group in userprofile.owned_problem_groups.all() or prob_group in userprofile.editable_problem_groups.all() or prob_group in userprofile.archived_problem_groups.all() or prob_group in userprofile.archived_owned_problem_groups.all() or prob_group in userprofile.archived_editable_problem_groups.all():
        P = prob_group.problem_objects.all()
        checked = form.getlist("probs")
        for i in P:
            if str(i.pk) not in checked:
                i.delete()###careful
            else:
                i.order = checked.index(str(i.pk))+1
                i.save()
#                prob_group.problem_objects.remove(i)
    return JsonResponse({})


##is not putting problems in correct order...but I think this is because the 'test' object doesn't do this.
@login_required
def create_test(request,**kwargs):
    form = request.POST
    userprofile = request.user.userprofile
    if "chk" in form:
        checked = form.getlist("chk")
        if len(checked) > 0:
            testname = form.get('testname','')
            t = Test(name = testname)
            t.save()
            prob_objs = ProblemGroupObject.objects.filter(pk__in=checked)
            tpks = []
            for i in prob_objs:
                tpks.append(i.problem.type_new.pk)
            types = Type.objects.filter(pk__in=tpks)
            for i in types:
                t.types.add(i)
            userprofile.tests.add(t)
            ut = UserTest(test = t,num_probs = prob_objs.count(),num_correct = 0,userprof = userprofile)
            ut.save()
            for i in checked:
                po = ProblemGroupObject.objects.get(pk=i)
                p = po.problem
                t.problems.add(p)
                r = NewResponse(response = '',problem_label = p.label,problem = p,usertest = ut)
                r.save()
            t.save()
            userprofile.save()
            return JsonResponse({'url':'/randomtest/test/'+str(ut.pk)+'/'})
    return JsonResponse({'error-message':'No problems checked!'})

@login_required
def load_sharing_modal(request,**kwargs):
    userprofile = request.user.userprofile
    context={}
    pk = request.POST.get('pk','')
    problemgroup = get_object_or_404(ProblemGroup,pk=pk)
    context['pg'] = problemgroup
    owners = problemgroup.userprofiles.all()
    coowners = problemgroup.owneruserprofiles.all()
    editors = problemgroup.editoruserprofiles.all()
    readers = problemgroup.readeruserprofiles.all()
    context['owners'] = owners
    context['coowners'] = coowners
    context['editors'] = editors
    context['read_only_users'] = readers
    context['collaborators'] = userprofile.collaborators.exclude(userprofile__pk__in=owners.values_list('pk')).exclude(userprofile__pk__in=editors.values_list('pk')).exclude(userprofile__pk__in=readers.values_list('pk')).exclude(userprofile__pk__in=coowners.values_list('pk'))
    if userprofile in owners or userprofile in coowners:
        context['is_owner'] = 1
    context['userprofile'] = userprofile
    return JsonResponse({'modal-html' : render_to_string('groups/modals/edit-sharing.html',context)})

@login_required
def share_with_user(request, **kwargs):#check permission...
    userprofile = request.user.userprofile
    form = request.POST
    pk = form.get('problemgrouppk','')
    problemgroup = get_object_or_404(ProblemGroup,pk = pk)
    share_target = get_object_or_404(User,pk = form.get('collaborator',''))
    share_target_up = share_target.userprofile
    sharing_type = form.get('sharing-type','')
    if problemgroup in userprofile.problem_groups.all() or problemgroup in userprofile.owned_problem_groups.all() or problemgroup in userprofile.archived_problem_groups.all() or problemgroup in userprofile.archived_owned_problem_groups.all():
        if sharing_type == 'read':
            if problemgroup not in share_target_up.editable_problem_groups.all() and problemgroup not in share_target_up.owned_problem_groups.all() and problemgroup not in share_target_up.problem_groups.all():
                share_target_up.readonly_problem_groups.add(problemgroup)
                share_target_up.save()
                problemgroup.is_shared = True
                problemgroup.save()
            return JsonResponse({'user-row' : render_to_string('groups/modals/user-row.html',{'sharing_type': 'reader','shared_user' : share_target_up, 'is_owner' : 1}),'col': share_target.pk,'sharing_type': 'read', 'group-row' : render_to_string('groups/grouptablerow.html',{'pg':problemgroup,'sharing_type':'own'}),'pk':problemgroup.pk})
        elif sharing_type == 'edit':
            if problemgroup not in share_target_up.problem_groups.all() and problemgroup not in share_target_up.owned_problem_groups.all():
                share_target_up.editable_problem_groups.add(problemgroup)
                share_target_up.save()
                problemgroup.is_shared = True
                problemgroup.save()
            if problemgroup in share_target_up.readonly_problem_groups.all():
                share_target_up.readonly_problem_groups.remove(problemgroup)
                share_target_up.save()
            return JsonResponse({'user-row' : render_to_string('groups/modals/user-row.html',{'sharing_type': 'editor','shared_user' : share_target_up, 'is_owner' : 1}),'col': share_target.pk,'sharing_type': 'edit', 'group-row' : render_to_string('groups/grouptablerow.html',{'pg':problemgroup,'sharing_type':'own'}),'pk':problemgroup.pk})
        elif sharing_type == 'own':
            share_target_up.owned_problem_groups.add(problemgroup)
            share_target_up.save()
            problemgroup.is_shared = True
            problemgroup.save()
            if problemgroup in share_target_up.readonly_problem_groups.all():
                share_target_up.readonly_problem_groups.remove(problemgroup)
                share_target_up.save()
            if problemgroup in share_target_up.editable_problem_groups.all():
                share_target_up.editable_problem_groups.remove(problemgroup)
                share_target_up.save()
            return JsonResponse({'user-row' : render_to_string('groups/modals/user-row.html',{'sharing_type': 'coowner','shared_user' : share_target_up, 'is_owner' : 1}),'col': share_target.pk,'sharing_type': 'own', 'group-row' : render_to_string('groups/grouptablerow.html',{'pg':problemgroup,'sharing_type':'own'}),'pk':problemgroup.pk})

@login_required
def change_permission(request):
    userprofile = request.user.userprofile
    form = request.POST
    sharing_type = form.get('sharing_type','')
    pk = form.get('problemgrouppk','')
    problemgroup = get_object_or_404(ProblemGroup,pk = pk)
    share_target_up = get_object_or_404(UserProfile,pk = form.get('pk',''))
    if share_target_up.problem_groups.filter(pk = problemgroup.pk).exists()==False:#if target not an original owner...
        if problemgroup in userprofile.problem_groups.all() or problemgroup in userprofile.owned_problem_groups.all() or problemgroup in userprofile.archived_problem_groups.all() or problemgroup in userprofile.archived_owned_problem_groups.all():#if owner....
            if sharing_type == 'read':
                share_target_up.owned_problem_groups.remove(problemgroup)
                share_target_up.editable_problem_groups.remove(problemgroup)
                share_target_up.readonly_problem_groups.add(problemgroup)
                share_target_up.save()
                return JsonResponse({'user-row' : render_to_string('groups/modals/user-row.html',{'sharing_type': 'reader','shared_user' : share_target_up, 'is_owner' : 1}),'sharing_type': 'read', 'group-row' : render_to_string('groups/grouptablerow.html',{'pg':problemgroup,'sharing_type':'own'}),'pk':problemgroup.pk})
            elif sharing_type == 'edit':
                share_target_up.owned_problem_groups.remove(problemgroup)
                share_target_up.editable_problem_groups.add(problemgroup)
                share_target_up.readonly_problem_groups.remove(problemgroup)
                share_target_up.save()
                return JsonResponse({'user-row' : render_to_string('groups/modals/user-row.html',{'sharing_type': 'editor','shared_user' : share_target_up, 'is_owner' : 1}),'sharing_type': 'edit', 'group-row' : render_to_string('groups/grouptablerow.html',{'pg':problemgroup,'sharing_type':'own'}),'pk':problemgroup.pk})
            elif sharing_type == 'own':
                share_target_up.owned_problem_groups.add(problemgroup)
                share_target_up.editable_problem_groups.remove(problemgroup)
                share_target_up.readonly_problem_groups.remove(problemgroup)
                share_target_up.save()
                return JsonResponse({'user-row' : render_to_string('groups/modals/user-row.html',{'sharing_type': 'coowner','shared_user' : share_target_up, 'is_owner' : 1}),'sharing_type': 'own', 'group-row' : render_to_string('groups/grouptablerow.html',{'pg':problemgroup,'sharing_type':'own'}),'pk':problemgroup.pk})
            elif sharing_type == 'del':
                share_target_up.owned_problem_groups.remove(problemgroup)
                share_target_up.editable_problem_groups.remove(problemgroup)
                share_target_up.readonly_problem_groups.remove(problemgroup)
                share_target_up.save()
                if problemgroup.userprofiles.count() + problemgroup.owneruserprofiles.count() + problemgroup.editoruserprofiles.count() + problemgroup.readeruserprofiles.count() <= 1:
                    problemgroup.is_shared = False
                    problemgroup.save()
                return JsonResponse({'sharing_type':'del', 'group-row' : render_to_string('groups/grouptablerow.html',{'pg':problemgroup,'sharing_type':'own'}),'pk':problemgroup.pk})
            

@login_required
def test_as_pdf(request,**kwargs):
    form = request.GET
    context = {}
    if 'include-acs' in form:
        include_answer_choices = True
    else:
        include_answer_choices = False
    if 'include-pls' in form:
        include_problem_labels = True
    else:
        include_problem_labels = False
    if 'include-tags' in form:
        include_tags = True
    else:
        include_tags = False
    if 'include-sols' in form:
        include_sols = True
    else:
        include_sols = False
    if 'include-ans' in form:
        include_ans = True
    else:
        include_ans = False
    if 'include-nts' in form:
        include_nts = True
    else:
        include_nts = False
    print(include_nts)
    prob_group = get_object_or_404(ProblemGroup, pk=kwargs['pk'])

    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('groups/my_latex_template.tex')
    rendered_tpl = template.render(context).encode('utf-8')
    with tempfile.TemporaryDirectory() as tempdir:
        fa = open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        context = {
            'group' : prob_group,
            'include_problem_labels' : include_problem_labels,
            'include_answer_choices':include_answer_choices,
            'include_tags' : include_tags,
            'include_sols' : include_sols,
            'include_ans' : include_ans,
            'include_nts' : include_nts,
            'tempdirect' : tempdir,
            }
        template = get_template('groups/my_latex_template.tex')
        rendered_tpl = template.render(context).encode('utf-8')
        ftex = open(os.path.join(tempdir,'texput.tex'),'wb')
        ftex.write(rendered_tpl)
        ftex.close()
        for i in range(1):
            process = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process.communicate()[0]
        L=os.listdir(tempdir)

        for i in range(0,len(L)):
            if L[i][-4:] == '.asy':
                process1 = Popen(
                    ['asy', L[i]],
                    stdin = PIPE,
                    stdout = PIPE,
                    cwd = tempdir,
                    )
                stdout_value = process1.communicate()[0]
        for i in range(2):
            process2 = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process2.communicate()[0]

        if 'texput.pdf' in os.listdir(tempdir):
            with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
                pdf = f.read()
                r = HttpResponse(content_type='application/pdf')
                r.write(pdf)
                r['Content-Disposition'] = 'attachment;filename="'+prob_group.name.replace(' ','')+'.pdf"'
                return r
        else:
            with open(os.path.join(tempdir, 'texput.log')) as f:
                error_text = f.read()
                return render(request,'randomtest/latex_errors.html',{'nbar':'groups','name':prob_group.name,'error_text':error_text})#####Perhaps the error page needs to be customized...


@login_required
def outline_test_as_pdf(request,**kwargs):
    form = request.GET
    context = {}
    if 'include-acs' in form:
        include_answer_choices = True
    else:
        include_answer_choices = False
    if 'include-pls' in form:
        include_problem_labels = True
    else:
        include_problem_labels = False
    if 'include-tags' in form:
        include_tags = True
    else:
        include_tags = False
    if 'include-sols' in form:
        include_sols = True
    else:
        include_sols = False
    if 'include-ans' in form:
        include_ans = True
    else:
        include_ans = False
    if 'include-nts' in form:
        include_nts = True
    else:
        include_nts = False
    print(include_nts)
    prob_group = get_object_or_404(ProblemGroup, pk=kwargs['pk'])

    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('groups/my_latex_outline_template.tex')
    rendered_tpl = template.render(context).encode('utf-8')
    with tempfile.TemporaryDirectory() as tempdir:
        fa = open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        context = {
            'group' : prob_group,
            'include_problem_labels' : include_problem_labels,
            'include_answer_choices':include_answer_choices,
            'include_tags' : include_tags,
            'include_sols' : include_sols,
            'include_ans' : include_ans,
            'include_nts' : include_nts,
            'tempdirect' : tempdir,
            }
        template = get_template('groups/my_latex_outline_template.tex')
        rendered_tpl = template.render(context).encode('utf-8')
        ftex = open(os.path.join(tempdir,'texput.tex'),'wb')
        ftex.write(rendered_tpl)
        ftex.close()
        for i in range(1):
            process = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process.communicate()[0]
        L=os.listdir(tempdir)

        for i in range(0,len(L)):
            if L[i][-4:] == '.asy':
                process1 = Popen(
                    ['asy', L[i]],
                    stdin = PIPE,
                    stdout = PIPE,
                    cwd = tempdir,
                    )
                stdout_value = process1.communicate()[0]
        for i in range(2):
            process2 = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process2.communicate()[0]

        if 'texput.pdf' in os.listdir(tempdir):
            with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
                pdf = f.read()
                r = HttpResponse(content_type='application/pdf')
                r.write(pdf)
                r['Content-Disposition'] = 'attachment;filename="'+prob_group.name.replace(' ','')+'.pdf"'
                return r
        else:
            with open(os.path.join(tempdir, 'texput.log')) as f:
                error_text = f.read()
                return render(request,'randomtest/latex_errors.html',{'nbar':'groups','name':prob_group.name,'error_text':error_text})#####Perhaps the error page needs to be customized...  

@login_required
def outline_test_as_tex(request,**kwargs):
    form = request.GET
    context = {}
    if 'include-acs' in form:
        include_answer_choices = True
    else:
        include_answer_choices = False
    if 'include-pls' in form:
        include_problem_labels = True
    else:
        include_problem_labels = False
    if 'include-tags' in form:
        include_tags = True
    else:
        include_tags = False
    if 'include-sols' in form:
        include_sols = True
    else:
        include_sols = False
    if 'include-ans' in form:
        include_ans = True
    else:
        include_ans = False
    if 'include-nts' in form:
        include_nts = True
    else:
        include_nts = False
    print(include_nts)
    prob_group = get_object_or_404(ProblemGroup, pk=kwargs['pk'])
    context = {
        'group' : prob_group,
        'include_problem_labels' : include_problem_labels,
        'include_answer_choices':include_answer_choices,
        'include_tags' : include_tags,
        'include_sols' : include_sols,
        'include_ans' : include_ans,
        'include_nts' : include_nts,
    }
    template = get_template('groups/my_latex_outline_template.tex')
    rendered_tpl = template.render(context).encode('utf-8')
    filename = "texput.tex"
    response = HttpResponse(rendered_tpl, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response

@login_required
def twoatatime_test_as_pdf(request,**kwargs):
    form = request.GET
    context = {}
    if 'include-acs' in form:
        include_answer_choices = True
    else:
        include_answer_choices = False
    if 'include-pls' in form:
        include_problem_labels = True
    else:
        include_problem_labels = False
    if 'include-tags' in form:
        include_tags = True
    else:
        include_tags = False
    if 'include-sols' in form:
        include_sols = True
    else:
        include_sols = False
    if 'include-ans' in form:
        include_ans = True
    else:
        include_ans = False
    if 'include-nts' in form:
        include_nts = True
    else:
        include_nts = False
    print(include_nts)
    prob_group = get_object_or_404(ProblemGroup, pk=kwargs['pk'])

    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('groups/my_latex_twoatatime_template.tex')
    rendered_tpl = template.render(context).encode('utf-8')
    with tempfile.TemporaryDirectory() as tempdir:
        fa = open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        context = {
            'group' : prob_group,
            'include_problem_labels' : include_problem_labels,
            'include_answer_choices':include_answer_choices,
            'include_tags' : include_tags,
            'include_sols' : include_sols,
            'include_ans' : include_ans,
            'include_nts' : include_nts,
            'tempdirect' : tempdir,
            }
        template = get_template('groups/my_latex_twoatatime_template.tex')
        rendered_tpl = template.render(context).encode('utf-8')
        ftex = open(os.path.join(tempdir,'texput.tex'),'wb')
        ftex.write(rendered_tpl)
        ftex.close()
        for i in range(1):
            process = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process.communicate()[0]
        L=os.listdir(tempdir)

        for i in range(0,len(L)):
            if L[i][-4:] == '.asy':
                process1 = Popen(
                    ['asy', L[i]],
                    stdin = PIPE,
                    stdout = PIPE,
                    cwd = tempdir,
                    )
                stdout_value = process1.communicate()[0]
        for i in range(2):
            process2 = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process2.communicate()[0]

        if 'texput.pdf' in os.listdir(tempdir):
            with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
                pdf = f.read()
                r = HttpResponse(content_type='application/pdf')
                r.write(pdf)
                r['Content-Disposition'] = 'attachment;filename="'+prob_group.name.replace(' ','')+'.pdf"'
                return r
        else:
            with open(os.path.join(tempdir, 'texput.log')) as f:
                error_text = f.read()
                return render(request,'randomtest/latex_errors.html',{'nbar':'groups','name':prob_group.name,'error_text':error_text})#####Perhaps the error page needs to be customized...  


@login_required
def latex_view(request,**kwargs):
    form = request.GET
    context = {}
    if 'include-acs' in form:
        include_answer_choices = True
    else:
        include_answer_choices = False
    if 'include-pls' in form:
        include_problem_labels = True
    else:
        include_problem_labels = False
    if 'include-sols' in form:
        include_sols = True
    else:
        include_sols = False
    if 'include-ans' in form:
        include_ans = True
    else:
        include_ans = False
    prob_group = get_object_or_404(ProblemGroup, pk=kwargs['pk'])
    P = prob_group.problems.all()
    context = {
        'pk' : kwargs['pk'],
        'include_problem_labels' : include_problem_labels,
        'include_answer_choices' : include_answer_choices,
        'include_sols' : include_sols,
        'include_ans' : include_ans,
        'nbar' : 'groups',
        'group' : prob_group,
        }
    return render(request, 'groups/latex_view.html',context)

@login_required
def drill_test_as_pdf(request,**kwargs):
    form = request.GET
    context = {}
    if 'include-acs' in form:
        include_answer_choices = True
    else:
        include_answer_choices = False
    if 'include-pls' in form:
        include_problem_labels = True
    else:
        include_problem_labels = False
    if 'include-tags' in form:
        include_tags = True
    else:
        include_tags = False
    if 'include-sols' in form:
        include_sols = True
    else:
        include_sols = False
    if 'include-ans' in form:
        include_ans = True
    else:
        include_ans = False
    if 'include-nts' in form:
        include_nts = True
    else:
        include_nts = False
    print(include_nts)
    prob_group = get_object_or_404(ProblemGroup, pk=kwargs['pk'])

    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('groups/my_latex_drill_template.tex')
    rendered_tpl = template.render(context).encode('utf-8')
    with tempfile.TemporaryDirectory() as tempdir:
        fa = open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        context = {
            'group' : prob_group,
            'include_problem_labels' : include_problem_labels,
            'include_answer_choices':include_answer_choices,
            'include_tags' : include_tags,
            'include_sols' : include_sols,
            'include_ans' : include_ans,
            'include_nts' : include_nts,
            'tempdirect' : tempdir,
            }
        template = get_template('groups/my_latex_drill_template.tex')
        rendered_tpl = template.render(context).encode('utf-8')
        ftex = open(os.path.join(tempdir,'texput.tex'),'wb')
        ftex.write(rendered_tpl)
        ftex.close()
        for i in range(1):
            process = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process.communicate()[0]
        L=os.listdir(tempdir)

        for i in range(0,len(L)):
            if L[i][-4:] == '.asy':
                process1 = Popen(
                    ['asy', L[i]],
                    stdin = PIPE,
                    stdout = PIPE,
                    cwd = tempdir,
                    )
                stdout_value = process1.communicate()[0]
        for i in range(2):
            process2 = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process2.communicate()[0]

        if 'texput.pdf' in os.listdir(tempdir):
            with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
                pdf = f.read()
                r = HttpResponse(content_type='application/pdf')
                r.write(pdf)
                r['Content-Disposition'] = 'attachment;filename="'+prob_group.name.replace(' ','')+'.pdf"'
                return r
        else:
            with open(os.path.join(tempdir, 'texput.log')) as f:
                error_text = f.read()
                return render(request,'randomtest/latex_errors.html',{'nbar':'groups','name':prob_group.name,'error_text':error_text})#####Perhaps the error page needs to be customized...  

            
@login_required
def group_answer_key_as_pdf(request, **kwargs):
    prob_group = get_object_or_404(ProblemGroup, pk=kwargs['pk'])
    P = list(prob_group.problem_objects.all())
    rows = []

    for i in range(0,len(P)):
        rows.append(P[i].problem)
    with tempfile.TemporaryDirectory() as tempdir:
        context = {
            'rows':rows,
            'pk':kwargs['pk'],
            'tempdirect':tempdir,
            }
        template = get_template('groups/my_latex_answerkey_template.tex')
        rendered_tpl = template.render(context).encode('utf-8')
        ftex=open(os.path.join(tempdir,'texput.tex'),'wb')
        ftex.write(rendered_tpl)
        ftex.close()
        for i in range(2):
            process = Popen(
                ['pdflatex', 'texput.tex'],
                stdin=PIPE,
                stdout=PIPE,
                cwd = tempdir,
            )
            stdout_value = process.communicate()[0]
        L=os.listdir(tempdir)
        if 'texput.pdf' in os.listdir(tempdir):
            with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
                pdf = f.read()
                r = HttpResponse(content_type='application/pdf')
                r.write(pdf)
                r['Content-Disposition'] = 'attachment;filename="'+prob_group.name.replace(' ','')+'answerkey.pdf"'

                return r
        else:
            with open(os.path.join(tempdir, 'texput.log')) as f:
                error_text = f.read()
                return render(request,'randomtest/latex_errors.html',{'nbar':'groups','name':prob_group.name,'error_text':error_text})


@login_required
def add_to_group(request):
    form = request.POST
    userprofile = request.user.userprofile
    if "chk" in form:
        checked = form.getlist("chk")
        if len(checked) > 0:
            first = ProblemGroupObject.objects.get(pk = checked[0])
            pg = first.problemgroup
            prob_objs = pg.problem_objects.filter(pk__in = checked)
            problem_groups = [(d,p) for d, p in request.POST.items() if d.startswith('add_to_problemgroup')]
            for i in problem_groups:
                p_group = get_object_or_404(ProblemGroup,pk = i[1])
                problems_all_in_group = 1
                for po in prob_objs:
                    prob = po.problem
                    if p_group.problem_objects.filter(problem = prob).exists() == False:
                        problems_all_in_group = 0
                        p_group.add_to_end(prob)
                if problems_all_in_group == 1:
                    return JsonResponse({'status':0,'name':p_group.name})
            return JsonResponse({'status':2,'name':p_group.name})
    return JsonResponse({'status':1})#no problems checked


@login_required
def fetch_problems(request):
    pk = request.GET.get('pk')
    userprofile = request.user.userprofile
    prob_group = get_object_or_404(ProblemGroup,pk=pk)

    if prob_group not in userprofile.problem_groups.all():########FIX Permissions!
        return HttpResponse('Unauthorized', status=401)
    form = request.GET
    try:
        prob_num_low = int(form.get('prob_num_low',''))
    except ValueError:
        prob_num_low = 0
    try:
        prob_num_high = int(form.get('prob_num_high',''))
    except ValueError:
        prob_num_high = 100
    try:
        year_low = int(form.get('year_low',''))
    except ValueError:
        year_low = 0
    try:
        year_high = int(form.get('year_high',''))
    except ValueError:
        year_high = 20000
    try:
        num_problems = int(form.get('num_problems',''))
    except ValueError:
        num_problems = 10
    tag = form.get('desired_tag','')
    if tag == "Unspecified":#desired_tag
        tag = ''

    testtype = form.get('contest_type','')
    type_args = testtype.split('_')
    round_or_type = type_args[0]
    rt_pk = type_args[1]

#    if desired_tag == 'Unspecified':
#        problems = Problem.objects.filter(type_new__type=form.get('contest_type','')).filter(year__gte=year_low).filter(year__lte=year_high).filter(problem_number__gte=prob_num_low).filter(problem_number__lte=prob_num_high)
#    else:
#        problems = Problem.objects.filter(type_new__type=form.get('contest_type','')).filter(year__gte=year_low).filter(year__lte=year_high).filter(problem_number__gte=prob_num_low).filter(problem_number__lte=prob_num_high).filter(newtags__in=NewTag.objects.filter(tag__startswith=desired_tag)).distinct()
    P = Problem.objects.all()
    if len(tag)>0:
        if round_or_type == "T":
            P = P.filter(problem_number__gte=prob_num_low,problem_number__lte=prob_num_high).filter(year__gte=year_low,year__lte=year_high).filter(type_new__pk=rt_pk)
        else:
            P = P.filter(problem_number__gte=prob_num_low,problem_number__lte=prob_num_high).filter(year__gte=year_low,year__lte=year_high).filter(round__pk=rt_pk)
        P = P.filter(newtags__in=NewTag.objects.filter(tag__startswith=tag)).distinct()
    else:
        if round_or_type == "T":
            P = P.filter(problem_number__gte = prob_num_low,problem_number__lte = prob_num_high).filter(year__gte = year_low,year__lte = year_high).filter(type_new__pk = rt_pk).distinct()
        else:
            P = P.filter(problem_number__gte = prob_num_low,problem_number__lte = prob_num_high).filter(year__gte = year_low,year__lte = year_high).filter(round__pk = rt_pk).distinct()



    pks = []

    for i in prob_group.problem_objects.all():
        pks.append(i.problem.pk)
    problems = P.exclude(pk__in=pks)
    prob_list = list(problems)
    shuffle(prob_list)
    prob_list = prob_list[0:num_problems]
    prob_code = []
    base_num = prob_group.problem_objects.count()
    can_delete = 0
    if prob_group in userprofile.problem_groups.all() or prob_group in userprofile.owned_problem_groups.all() or  prob_group in userprofile.editable_problem_groups.all() or prob_group in userprofile.archived_problem_groups.all() or prob_group in userprofile.archived_owned_problem_groups.all() or  prob_group in userprofile.archived_editable_problem_groups.all():
        can_delete = 1
    for i in range(0,len(prob_list)):
        pg_object = ProblemGroupObject(problemgroup = prob_group,problem = prob_list[i],order = base_num + i + 1)
        pg_object.save()
        prob_code.append(render_to_string('groups/probgroup_problem_object.html',{'po':pg_object,'forcount':base_num+i+1,'can_delete':can_delete}))
#    prob_group.save()
    data = {
        'prob_list': prob_code,
        }
    return JsonResponse(data)



@login_required
def editprobgroupname(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    prob_group = get_object_or_404(ProblemGroup,pk=pk)
    if prob_group in userprofile.problem_groups.all() or prob_group in userprofile.archived_problem_groups.all():
        form = EditProblemGroupNameForm(instance = prob_group)
        return JsonResponse({'modal-html':render_to_string('groups/modals/modal-edit-prob_group-name.html',{'form':form})})
    return JsonResponse({})

@login_required
def saveprobgroupname(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    prob_group = get_object_or_404(ProblemGroup,pk=pk)
    if prob_group in userprofile.problem_groups.all() or prob_group in userprofile.archived_problem_groups.all():
        form = EditProblemGroupNameForm(request.POST,instance = prob_group)
        form.save()
        return JsonResponse({'prob_group-name':form.instance.name})
    return JSonResponse({})

@login_required
def editprobgroupdescription(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    prob_group = get_object_or_404(ProblemGroup,pk=pk)
    if prob_group in userprofile.problem_groups.all() or prob_group in userprofile.archived_problem_groups.all():
        form = EditProblemGroupDescriptionForm(instance = prob_group)
        return JsonResponse({'modal-html':render_to_string('groups/modals/modal-edit-prob_group-description.html',{'form':form})})
    return JsonResponse({})

@login_required
def saveprobgroupdescription(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    prob_group = get_object_or_404(ProblemGroup,pk=pk)
    print(prob_group)
    if prob_group in userprofile.problem_groups.all() or prob_group in userprofile.archived_problem_groups.all():
        form = EditProblemGroupDescriptionForm(request.POST,instance = prob_group)
        form.save()
        return JsonResponse({'prob_group-description':form.instance.description})
    return JSonResponse({})




###Search views
@login_required
def searchform(request,pk):
    form = request.GET
    pg = get_object_or_404(ProblemGroup,pk=pk)
    advanced = False
    if 'advanced' in form:
        advanced = True
    userprofile = get_or_create_up(request.user)
    types = userprofile.user_type_new.allowed_types.all()
    tags = sorted(list(NewTag.objects.exclude(label='root')),key=lambda x:x.tag)
    template = loader.get_template('groups/searchform.html')
    context = {'nbar' : 'groups', 'types' : types,'tags' : tags, 'advanced': advanced,
               'userprofile':userprofile,
               'presets':AdvancedSearchPreset.objects.all(),
               'prob_group': pg,
    }
    if 'advanced' in form:
        owned_pgs =  userprofile.problem_groups.all()
        co_owned_pgs =  userprofile.owned_problem_groups.all()
        editor_pgs =  userprofile.editable_problem_groups.all()
        readonly_pgs =  userprofile.readonly_problem_groups.all()
        pgs = list(owned_pgs)+list(co_owned_pgs)+list(editor_pgs)+list(readonly_pgs)
        context['probgroups'] = pgs
    return HttpResponse(template.render(context,request))

@login_required
def searchresults(request,pk):
    userprofile = get_or_create_up(request.user)
    prob_group = get_object_or_404(ProblemGroup,pk=pk)
    if request.method=='GET':
        page = request.GET.get('page')
        z = request.GET.copy()
        if 'page' in z:
            del(z['page'])
        current_url = z.urlencode()
        form = request.GET
        types = userprofile.user_type_new.allowed_types.all()
        type_pks = []
        for i in types:
            type_pks.append(i.pk)
        if form.get('searchform','') == "start":
            testtype = form.get('tp','')
            type_args = testtype.split('_')
            if len(type_args) > 1:
                round_or_type = type_args[0]
                rt_pk = type_args[1]
            else:
                round_or_type = ''
                rt_pk = ''

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
                elif round_or_type == '':
                    P = P.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend)
                    P = P.filter(type_new__pk__in = type_pks)
                else:
                    P = P.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend).filter(round__pk=rt_pk)#
                P = P.filter(newtags__in=NewTag.objects.filter(tag__startswith=tag)).distinct()

            else:
                if round_or_type == "T":
                    P = P.filter(problem_number__gte = probbegin,problem_number__lte = probend).filter(year__gte = yearbegin,year__lte = yearend).filter(type_new__pk = rt_pk).distinct()#
                elif round_or_type == '':
                    P = P.filter(problem_number__gte = probbegin,problem_number__lte = probend).filter(year__gte = yearbegin,year__lte = yearend).distinct()
                    P = P.filter(type_new__pk__in = type_pks)
                else:
                    P = P.filter(problem_number__gte = probbegin,problem_number__lte = probend).filter(year__gte = yearbegin,year__lte = yearend).filter(round__pk = rt_pk).distinct()#

#            if form.get('solution_search','') is not None:
#                S = Solution.objects.filter(parent_problem__problem_number__gte = probbegin,parent_problem__problem_number__lte = probend).filter(parent_problem__year__gte = yearbegin,parent_problem__year__lte = yearend).filter(parent_problem__types__type = testtype).distinct()
#                for i in keywords:
#                    S = S.filter(solution_text__contains = i)
#                P2 = Problem.objects.filter(id__in = S.values('parent_problem_id'))
            if 'solutionsearch' in form:
                if round_or_type == "T":
                    S = Solution.objects.filter(parent_problem__problem_number__gte = probbegin,parent_problem__problem_number__lte = probend).filter(parent_problem__year__gte = yearbegin,parent_problem__year__lte = yearend).filter(parent_problem__type_new__pk = rt_pk).filter(parent_problem__id__in=P).distinct()
                elif round_or_type == '':
                    S = Solution.objects.filter(parent_problem__problem_number__gte = probbegin,parent_problem__problem_number__lte = probend).filter(parent_problem__year__gte = yearbegin,parent_problem__year__lte = yearend).filter(parent_problem__id__in=P).distinct()
                    S = S.filter(parent_problem__type_new__pk__in = type_pks)
                else:
                    S = Solution.objects.filter(parent_problem__problem_number__gte = probbegin,parent_problem__problem_number__lte = probend).filter(parent_problem__year__gte = yearbegin,parent_problem__year__lte = yearend).filter(parent_problem__round__pk = rt_pk).filter(parent_problem__id__in=P).distinct()
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
            template = loader.get_template('groups/searchresults.html')
            context={'nbar' : 'search', 'rows' : prows, 'searchterm': searchterm, 'current_url' : current_url,'matchnums':len(P), 'probgroups' : probgroups,'request' : request, 'tags':NewTag.objects.exclude(tag='root')}
            if tag != "":
                context['tag_list'] = [tag]
            if round_or_type == 'T':
                context['testtypes'] = [Type.objects.get(pk=rt_pk)]
            elif round_or_type == '':
                context['testtypes'] = []
            else:
                context['testtypes'] = [Round.objects.get(pk=rt_pk)]
            context['prob_group'] = prob_group
            return HttpResponse(template.render(context,request))

@login_required
def advanced_searchresults(request,pk):
    userprofile = get_or_create_up(request.user)
    prob_group = get_object_or_404(ProblemGroup,pk=pk)
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

            probbegin = form.get('probbegin','')
            if probbegin is None or probbegin == u'':
                probbegin = 0
            else:
                probbegin = int(probbegin)

            probend = form.get('probend','')
            if probend is None or probend == u'':
                probend = 10000
            else:
                probend = int(probend)

            yearbegin = form.get('yearbegin','')
            if yearbegin is None or yearbegin == u'':
                yearbegin = 0
            else:
                yearbegin = int(yearbegin)

            yearend = form.get('yearend','')
            if yearend is None or yearend == u'':
                yearend = 10000
            else:
                yearend = int(yearend)

            P = Problem.objects.filter(type_new__pk__in=userprofile.user_type_new.allowed_types.all())
            sol_opts = form.get('sol_opts','')
            if sol_opts == "sols":
                P = P.exclude(solutions = None)
            elif sol_opts == "nosols":
                P = P.filter(solutions = None)

            P = P.filter(problem_number__gte = probbegin,problem_number__lte = probend).filter(year__gte = yearbegin,year__lte = yearend)
            if len(type_pks) + len(round_pks) > 0:
                P = P.filter(Q(type_new__pk__in = type_pks)|Q(round__pk__in = round_pks))

            union = request.GET.get('unionintersection')
            if union == None or union == 'union':
                if len(tag_list) > 0:
                    every_tag = []
                    for t in tag_list:
                        every_tag += list(NewTag.objects.filter(tag__startswith = t))
                    tag_pks = [t.pk for t in every_tag]
                    P = P.filter(newtags__in = NewTag.objects.filter(pk__in = tag_pks)).distinct()
            else:
                if len(tag_list) > 0:
                    every_tag = []
                    for t in tag_list:
                        every_tag += list(NewTag.objects.filter(tag__startswith = t))
                    tag_pks = [t.pk for t in every_tag]
                    for i in tag_pks:
                        P = P.filter(newtags__in = NewTag.objects.filter(pk__in = [i])).distinct()
                

            for i in keywords:
                P = P.filter(Q(problem_text__contains = i)|Q(mc_problem_text__contains = i)|Q(label = i)|Q(test_label = i))

            if 'solutionsearch' in form:
                S = Solution.objects.filter(parent_problem__problem_number__gte = probbegin,parent_problem__problem_number__lte = probend).filter(parent_problem__year__gte = yearbegin,parent_problem__year__lte = yearend)
                if len(type_pks) > 0 or len(round_pks) > 0:
                    S = S.filter(Q(parent_problem__type_new__pk__in = type_pks)|Q(parent_problem__round__pk__in = round_pks)).distinct()
                for i in keywords:
                    S = S.filter(solution_text__contains = i)
                P = Problem.objects.filter(Q(id__in = S.values('parent_problem_id'))|Q(id__in=P))
            if 'prob_group' in form:
                pgs = form.getlist('prob_group','')
                exclude_pg_list = ProblemGroup.objects.filter(pk__in = pgs)
                exclude_prob_pks = []
                for pg in exclude_pg_list:
                    for po in pg.problem_objects.all():
                        exclude_prob_pks.append(po.problem.pk)
                P = P.exclude(pk__in=exclude_prob_pks)

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
            template = loader.get_template('groups/searchresults.html')
            context={'nbar' : 'search', 'rows' : prows, 'searchterm': searchterm, 'current_url' : current_url,'matchnums':len(P), 'probgroups' : probgroups,'request' : request, 'tags':NewTag.objects.exclude(tag='root')}
            if len(tag_list) > 0:
                context['tag_list'] = tag_list
            types = Type.objects.filter(pk__in=type_pks)
            rounds = Round.objects.filter(pk__in=round_pks)
            type_names = []
            for i in types:
                type_names.append(i.label)
            for i in rounds:
                type_names.append(i.name)
            type_names.sort()
            context['testtypes'] = type_names
            context['prob_group'] = prob_group
            return HttpResponse(template.render(context,request))


#@login_required
#def view_presets(request):
#    context = {}
#    context['presets'] = AdvancedSearchPreset.objects.all()
#    context['types'] = request.user.userprofile.user_type_new.allowed_types.all()
#    return render(request,'search/view_presets.html',context)

@login_required
def add_to_this_group(request,pk):
#    prob_group = get_object_or_404(ProblemGroup,pk=pk)
#    objs = [(d,p) for d,p in request.POST.items() if d.startswith('addtothisproblemgroup')]
    problem_pk = request.POST.get("problem_id")#objs[0][0].split('_')[1]
    prob = get_object_or_404(Problem,pk = problem_pk)
    p_group = get_object_or_404(ProblemGroup,pk = pk)
    if p_group.problem_objects.filter(problem = prob).exists():
        return JsonResponse({'prob_pk':problem_pk,'status':1})
    p_group.add_to_end(prob)
    return JsonResponse({'prob_pk':problem_pk,'status':0})


@login_required
def search_add_to_group(request,pk):
    problem_groups = [(d,p) for d, p in request.POST.items() if d.startswith('problemgroup')]
    prob_group = get_object_or_404(ProblemGroup,pk=pk)
    for i in problem_groups:
        problem_pk = i[0].split('_')[1]
        prob = get_object_or_404(Problem,pk = problem_pk)
        p_group = get_object_or_404(ProblemGroup,pk = i[1])
        if p_group.problem_objects.filter(problem = prob).exists():
            return JsonResponse({'prob_pk':problem_pk,'status':1})
        p_group.add_to_end(prob)
    return JsonResponse({'prob_pk':problem_pk,'status':0})






@login_required
def add_tag(request):
    tags = [(d,p) for d, p in request.POST.items() if d.startswith('addtag')]
    for i in tags:
        problem_pk = i[0].split('_')[1]
        prob = get_object_or_404(Problem,pk = problem_pk)
        tag = get_object_or_404(NewTag,pk = i[1])
        if tag.problems.filter(pk = problem_pk).exists():
            return JsonResponse({'prob_pk':problem_pk,'status':1,'tag_count':prob.newtags.count()})
        prob.newtags.add(tag)
        prob.save()
    return JsonResponse({'prob_pk':problem_pk,'status':0,'tag_list':render_to_string("search/tag_snippet.html",{'prob':prob})})


@login_required
def delete_tag(request):
    delete_tag = request.POST.get('problem_tag_id','')
    del_list = delete_tag.split('_')
    problem_pk = del_list[1]
    prob = get_object_or_404(Problem,pk = problem_pk)
    tag_pk = del_list[2]
    tag = get_object_or_404(NewTag,pk = tag_pk)
    prob.newtags.remove(tag)
    prob.save()
    response_string = "<label for=\"tag-list-"+str(prob.pk)+"\">Current Tags</label>\n<ul id=\"tag-list-"+str(prob.pk)+"\">\n"
    L = prob.newtags.all()
    response_string = render_to_string("search/tag_snippet.html",{'prob':prob})
    return JsonResponse({'prob_pk':problem_pk,'tag_list':response_string,'tag_count':prob.newtags.count()})

@login_required
def load_sols(request,pk):
    prob = get_object_or_404(Problem,pk=pk)
    return JsonResponse({'modal-html': render_to_string("randomtest/load_sol.html",{'object' : prob})})


@login_required
def viewproblemgroup_intersection(request,pk,target_pk):
    userprofile = get_or_create_up(request.user)
    prob_group = get_object_or_404(ProblemGroup,pk=pk)
    target_prob_group = get_object_or_404(ProblemGroup,pk=target_pk)
    if prob_group not in userprofile.problem_groups.all() and prob_group not in userprofile.owned_problem_groups.all() and prob_group not in userprofile.editable_problem_groups.all() and prob_group not in userprofile.readonly_problem_groups.all() and prob_group not in userprofile.archived_problem_groups.all() and prob_group not in userprofile.archived_owned_problem_groups.all() and prob_group not in userprofile.archived_editable_problem_groups.all() and prob_group not in userprofile.archived_readonly_problem_groups.all():
        return HttpResponse('Unauthorized', status=401)
    context = {}
    context['nbar'] = 'groups'
    context['prob_group'] = prob_group
    context['target_prob_group'] = target_prob_group
    target_pks = []
    intersecting_problems = []
    for po in target_prob_group.problem_objects.all():
        target_pks.append(po.problem.pk)
    for po in prob_group.problem_objects.all():
        if po.problem.pk in target_pks:
            intersecting_problems.append(po.problem)
    context['request'] = request
    context['intersecting_problems'] = intersecting_problems
    owned_groups = userprofile.problem_groups.exclude(pk = pk)
    editable_groups = userprofile.editable_problem_groups.exclude(pk = pk)
    probgroups = list(chain(owned_groups,editable_groups))
    context['prob_groups'] = probgroups
    #context['form'] = AddProblemsForm(userprofile=userprofile)
    if prob_group in userprofile.problem_groups.all() or prob_group in userprofile.owned_problem_groups.all() or  prob_group in userprofile.editable_problem_groups.all() or prob_group in userprofile.archived_problem_groups.all() or prob_group in userprofile.archived_owned_problem_groups.all() or  prob_group in userprofile.archived_editable_problem_groups.all():
        context['can_delete'] = 1
    if prob_group in userprofile.problem_groups.all() or prob_group in userprofile.archived_problem_groups.all():
        context['can_edit'] = 1
    template = loader.get_template('groups/probgroupintersectionview.html')
    return HttpResponse(template.render(context,request))

@login_required
def viewproblemgroup_without(request,pk,target_pk):
    userprofile = get_or_create_up(request.user)
    prob_group = get_object_or_404(ProblemGroup,pk=pk)
    target_prob_group = get_object_or_404(ProblemGroup,pk=target_pk)
    if prob_group not in userprofile.problem_groups.all() and prob_group not in userprofile.owned_problem_groups.all() and prob_group not in userprofile.editable_problem_groups.all() and prob_group not in userprofile.readonly_problem_groups.all() and prob_group not in userprofile.archived_problem_groups.all() and prob_group not in userprofile.archived_owned_problem_groups.all() and prob_group not in userprofile.archived_editable_problem_groups.all() and prob_group not in userprofile.archived_readonly_problem_groups.all():
        return HttpResponse('Unauthorized', status=401)
    context = {}
    context['nbar'] = 'groups'
    context['prob_group'] = prob_group
    context['target_prob_group'] = target_prob_group
    target_pks = []
    intersecting_problems = []
    for po in target_prob_group.problem_objects.all():
        target_pks.append(po.problem.pk)
    without_problems = []
    for po in prob_group.problem_objects.all():
        if po.problem.pk not in target_pks:
            without_problems.append(po.problem)
    context['request'] = request
    context['without_problems'] = without_problems
    owned_groups = userprofile.problem_groups.exclude(pk = pk)
    editable_groups = userprofile.editable_problem_groups.exclude(pk = pk)
    probgroups = list(chain(owned_groups,editable_groups))
    context['prob_groups'] = probgroups
    #context['form'] = AddProblemsForm(userprofile=userprofile)
    if prob_group in userprofile.problem_groups.all() or prob_group in userprofile.owned_problem_groups.all() or  prob_group in userprofile.editable_problem_groups.all() or prob_group in userprofile.archived_problem_groups.all() or prob_group in userprofile.archived_owned_problem_groups.all() or  prob_group in userprofile.archived_editable_problem_groups.all():
        context['can_delete'] = 1
    if prob_group in userprofile.problem_groups.all() or prob_group in userprofile.archived_problem_groups.all():
        context['can_edit'] = 1
    template = loader.get_template('groups/probgroupwithoutview.html')
    return HttpResponse(template.render(context,request))
