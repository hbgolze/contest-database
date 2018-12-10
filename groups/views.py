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

from subprocess import Popen,PIPE
import tempfile
import os

import logging
logger = logging.getLogger(__name__)

from randomtest.models import Problem, Tag, Type, Test, UserProfile, QuestionType,get_or_create_up,UserResponse,Sticky,TestCollection,Folder,UserTest,ProblemGroup,NewTag,NewResponse
from randomtest.utils import newtexcode
from .forms import GroupModelForm

from random import shuffle
import time
from datetime import datetime,timedelta

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
    if prob_group not in userprofile.problem_groups.all() and prob_group not in userprofile.owned_problem_groups.all() and prob_group not in userprofile.editable_problem_groups.all() and prob_group not in userprofile.readonly_problem_groups.all():
        return HttpResponse('Unauthorized', status=401)
    context = {}
    context['nbar'] = 'groups'
    context['prob_group'] = prob_group
    if prob_group in userprofile.problem_groups.all() or prob_group in userprofile.owned_problem_groups.all() or  prob_group in userprofile.editable_problem_groups.all():
        context['can_delete'] = 1
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
def delete_group(request):
    pk = request.POST.get('pk','')
    pg = get_object_or_404(ProblemGroup, pk=pk)
    userprofile = request.user.userprofile
    if pg in userprofile.problem_groups.all():
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
    return JsonResponse({})

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
    if prob_group in userprofile.problem_groups.all() or prob_group in userprofile.owned_problem_groups.all() or prob_group in userprofile.editable_problem_groups.all():
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
            P = Problem.objects.filter(label__in=checked)
            types = Type.objects.filter(pk__in=P.values('type_new'))
            for i in types:
                t.types.add(i)
            userprofile.tests.add(t)
            ut = UserTest(test = t,num_probs = P.count(),num_correct = 0,userprof = userprofile)
            ut.save()
            for i in P:
                t.problems.add(i)
                r = NewResponse(response = '',problem_label = i.label,problem = i,usertest = ut)
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
    if problemgroup in userprofile.problem_groups.all() or problemgroup in userprofile.owned_problem_groups.all():
        if sharing_type == 'read':
            if problemgroup not in share_target_up.editable_problem_groups.all() and problemgroup not in share_target_up.owned_problem_groups.all() and problemgroup not in share_target_up.problem_groups.all():
                share_target_up.readonly_problem_groups.add(problemgroup)
                share_target_up.save()
            return JsonResponse({'user-row' : render_to_string('groups/modals/user-row.html',{'sharing_type': 'reader','shared_user' : share_target_up, 'is_owner' : 1}),'col': share_target.pk,'sharing_type': 'read'})
        elif sharing_type == 'edit':
            if problemgroup not in share_target_up.problem_groups.all() and problemgroup not in share_target_up.owned_problem_groups.all():
                share_target_up.editable_problem_groups.add(problemgroup)
                share_target_up.save()
            if problemgroup in share_target_up.readonly_problem_groups.all():
                share_target_up.readonly_problem_groups.remove(problemgroup)
                share_target_up.save()
            return JsonResponse({'user-row' : render_to_string('groups/modals/user-row.html',{'sharing_type': 'editor','shared_user' : share_target_up, 'is_owner' : 1}),'col': share_target.pk,'sharing_type': 'edit'})
        elif sharing_type == 'own':
            share_target_up.owned_problem_groups.add(problemgroup)
            share_target_up.save()
            if problemgroup in share_target_up.readonly_problem_groups.all():
                share_target_up.readonly_problem_groups.remove(problemgroup)
                share_target_up.save()
            if problemgroup in share_target_up.editable_problem_groups.all():
                share_target_up.editable_problem_groups.remove(problemgroup)
                share_target_up.save()
            return JsonResponse({'user-row' : render_to_string('groups/modals/user-row.html',{'sharing_type': 'coowner','shared_user' : share_target_up, 'is_owner' : 1}),'col': share_target.pk,'sharing_type': 'own'})

@login_required
def change_permission(request):
    userprofile = request.user.userprofile
    form = request.POST
    sharing_type = form.get('sharing_type','')
    pk = form.get('problemgrouppk','')
    problemgroup = get_object_or_404(ProblemGroup,pk = pk)
    share_target_up = get_object_or_404(UserProfile,pk = form.get('pk',''))
    if share_target_up.problem_groups.filter(pk = problemgroup.pk).exists()==False:#if target not an original owner...
        if problemgroup in userprofile.problem_groups.all() or problemgroup in userprofile.owned_problem_groups.all():#if owner....
            if sharing_type == 'read':
                share_target_up.owned_problem_groups.remove(problemgroup)
                share_target_up.editable_problem_groups.remove(problemgroup)
                share_target_up.readonly_problem_groups.add(problemgroup)
                share_target_up.save()
                return JsonResponse({'user-row' : render_to_string('groups/modals/user-row.html',{'sharing_type': 'reader','shared_user' : share_target_up, 'is_owner' : 1}),'sharing_type': 'read'})
            elif sharing_type == 'edit':
                share_target_up.owned_problem_groups.remove(problemgroup)
                share_target_up.editable_problem_groups.add(problemgroup)
                share_target_up.readonly_problem_groups.remove(problemgroup)
                share_target_up.save()
                return JsonResponse({'user-row' : render_to_string('groups/modals/user-row.html',{'sharing_type': 'editor','shared_user' : share_target_up, 'is_owner' : 1}),'sharing_type': 'edit'})
            elif sharing_type == 'own':
                share_target_up.owned_problem_groups.add(problemgroup)
                share_target_up.editable_problem_groups.remove(problemgroup)
                share_target_up.readonly_problem_groups.remove(problemgroup)
                share_target_up.save()
                return JsonResponse({'user-row' : render_to_string('groups/modals/user-row.html',{'sharing_type': 'coowner','shared_user' : share_target_up, 'is_owner' : 1}),'sharing_type': 'own'})
            elif sharing_type == 'del':
                share_target_up.owned_problem_groups.remove(problemgroup)
                share_target_up.editable_problem_groups.remove(problemgroup)
                share_target_up.readonly_problem_groups.remove(problemgroup)
                share_target_up.save()
                return JsonResponse({'sharing_type':'del'})
            

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
    prob_group = get_object_or_404(ProblemGroup, pk=kwargs['pk'])
    P = list(prob_group.problems.all())
    rows=[]

    for i in range(0,len(P)):
        ptext=''
        if P[i].question_type_new.question_type == 'multiple choice' or P[i].question_type_new.question_type == 'multiple choice short answer':
            ptext = P[i].mc_problem_text
            rows.append((P[i],ptext,P[i].readable_label,P[i].answers()))
        else:
            ptext = P[i].problem_text
            rows.append((P[i],ptext,P[i].readable_label,''))
    context = Context({
            'name' : prob_group.name,
            'rows' : rows,
            'pk' : kwargs['pk'],
            'include_problem_labels' : include_problem_labels,
            'include_answer_choices' : include_answer_choices,
            'include_tags' : include_tags,
            'include_sols' : include_sols,
            'include_ans' : include_ans,
            })
    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('groups/my_latex_template.tex')
    rendered_tpl = template.render(context).encode('utf-8')
    with tempfile.TemporaryDirectory() as tempdir:
        fa = open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        context = Context({
                'name' : prob_group.name,
                'rows' : rows,
                'pk' : kwargs['pk'],
                'include_problem_labels' : include_problem_labels,
                'include_answer_choices':include_answer_choices,
                'include_tags' : include_tags,
                'include_sols' : include_sols,
                'include_ans' : include_ans,
                'tempdirect' : tempdir,
                })
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
                return render(request,'randomtest/latex_errors.html',{'nbar':'problemgroup','name':prob_group.name,'error_text':error_text})#####Perhaps the error page needs to be customized...  
