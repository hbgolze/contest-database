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
from django.contrib.admin.models import LogEntry
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.views.generic import DetailView

from subprocess import Popen,PIPE
import tempfile
import os

import logging
logger = logging.getLogger(__name__)

from .models import Problem, Tag, Type, Test, UserProfile, Response, Responses, QuestionType,Dropboxurl,get_or_create_up,UserResponse,Sticky,TestCollection,TestTimeStamp,Folder,UserTest,Solution,ProblemApproval,NewTest,SortableProblem,NewTag
from .forms import TestForm,UserForm,UserProfileForm,TestModelForm

from .utils import parsebool,pointsum

from random import shuffle
import time
from datetime import datetime,timedelta

# Create your views here.

from django.views import generic
from .forms import LoginForm

#Not in use (need to figure out how to redirect...) Also, login2.html has been deleted.
class LoginView(generic.FormView):
    form_class = LoginForm
    success_url = reverse_lazy('tableview')
    template_name = 'registration/login2.html'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(self.request, user)
            return super(LoginView, self).form_valid(form)
        else:
            return self.form_invalid(form)
    def get_initial(self):
        initial = super(LoginView, self).get_initial()
        redirect_field_name = 'name'#self.get_redirect_field_name()
        if (redirect_field_name in self.request.GET and
            redirect_field_value in self.request.GET):
            initial.update({
                    "redirect_field_name": redirect_field_name,
                    "redirect_field_value": self.request.REQUEST.get(
                        'next'),
                    })
        return initial


class TestDelete(DeleteView):
    model = Test
    success_url = reverse_lazy('tableview')

@login_required
def deletetestresponses(request,pk):
    test = get_object_or_404(Test, pk=pk)
    isreserved=0
    TC=TestCollection.objects.all()
    userprofile = get_or_create_up(request.user)
    for i in TC:
        if test in i.tests.all():
            isreserved=1
    if test.responses_set.count()<=1 and isreserved==0:
        test.delete()
    else:
        testresponses = Responses.objects.filter(test=test).filter(user_profile=userprofile)
        if testresponses.count()>=1:
            testresponses.delete()
        userprofile.tests.remove(test)
    a= userprofile.timestamps.filter(test_pk=pk)
    if a.count() >0:
        a.delete()        
    return redirect('/')

@login_required
def deletestudenttestresponses(request,username,pk):
    test = get_object_or_404(Test, pk=pk)
    user = get_object_or_404(User,username=username)
    isreserved=0
    TC=TestCollection.objects.all()
    userprofile = get_or_create_up(user)
    for i in TC:
        if test in i.tests.all():
            isreserved=1
    if test.responses_set.count()<=1 and isreserved==0:
        test.delete()
    else:
        testresponses = Responses.objects.filter(test=test).filter(user_profile=userprofile)
        if testresponses.count()>=1:
            testresponses.delete()
        userprofile.tests.remove(test)
    a= userprofile.timestamps.filter(test_pk=pk)
    if a.count() >0:
        a.delete()        
    return redirect('../../')


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
                P=P.filter(newtags__in=NewTag.objects.filter(tag__startswith=tag)).distinct()
            else:
                P=Problem.objects.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend).filter(types__type=testtype).distinct()

            excludetestpks = form.getlist('excludetests')
            excludetests = Test.objects.filter(pk__in=excludetestpks)
#            excludeprobs = Problem.objects.filter(test_list__in=excludetests)
#            print(excludeprobs)
            for extest in excludetests:
                P=P.exclude(pk__in=extest.problems.all())
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
                r=Response(response='',problem_label=P[i].label,problem=P[i])
                r.save()
                R.responses.add(r)
            R.save()
            U.allresponses.add(R)
            T.types.add(Type.objects.get(type=testtype))
            T.save()
            ut=UserTest(test = T,responses = R,num_probs = len(P),num_correct = 0)
            ut.save()
            U.usertests.add(ut)
            U.save()
            return redirect('/test/'+str(ut.pk)+'/')
        else:
            return testview(request,int(form.get('startform','')))
    else:
        up,boolcreated = UserProfile.objects.get_or_create(user=request.user)
        types = up.user_type_new.allowed_types.order_by('label')
        tags=sorted(list(NewTag.objects.exclude(label='root')),key=lambda x:x.tag)
        usertests=up.usertests.all()
        template = loader.get_template('randomtest/startform2.html')
        context={'nbar' : 'newtest', 'types' : types, 'tags' : tags, 'usertests' : usertests}
        return HttpResponse(template.render(context,request))


@login_required
def newstartform(request):
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
                P=P.filter(newtags__in=NewTag.objects.filter(tag__startswith=tag)).distinct()
            else:
                P=Problem.objects.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend).filter(types__type=testtype).distinct()

            excludetestpks = form.getlist('excludetests')
            excludetests = Test.objects.filter(pk__in=excludetestpks)
            for extest in excludetests:
                P=P.exclude(pk__in=extest.problems.all())
            
            P=list(P)
            shuffle(P)
            P=P[0:num]
            P=sorted(P,key=lambda x:(x.problem_number,x.year))
            T=NewTest(name=testname,num_problems=num)
            T.save()
            for i in range(0,len(P)):
                sp=SortableProblem(problem=P[i],order=i+1,newtest_pk=T.pk)
                sp.save()
                T.problems.add(sp)
            T.types.add(Type.objects.get(type=testtype))
            T.save()
            return redirect('/newtest/'+str(T.pk)+'/')
        else:
            return testview(request,int(form.get('startform','')))
    else:
        up,boolcreated = UserProfile.objects.get_or_create(user=request.user)
        types = up.user_type_new.allowed_types.order_by('label')
        tags=sorted(list(NewTag.objects.exclude(label='root')),key=lambda x:x.tag)
        usertests=up.usertests.all()
        template = loader.get_template('randomtest/startform2.html')
        context={'nbar' : 'newtest', 'types' : types, 'tags' : tags, 'usertests' : usertests}
        return HttpResponse(template.render(context,request))

@login_required
def editnewtestview(request,pk):
    T=get_object_or_404(NewTest,pk=pk)
    Tprobs=T.problems.all()
    if request.method == "POST":
        if 'save' in request.POST:
            form=request.POST
            if 'probleminput' in form:
                P=list(T.problems.all())
                P=sorted(P,key=lambda x:x.order)
                probinputs=form.getlist('probleminput')#could be an issue if no problems
                for prob in P:
                    if 'problem_'+str(prob.pk) not in probinputs:
                        prob.delete()
                for i in range(0,len(probinputs)):
                    prob=T.problems.get(pk=probinputs[i].split('_')[1])
                    prob.order=i+1
                    prob.save()
        if 'addproblems' in request.POST:
            form=request.POST
            testtype = form.get('testtype','')
            searchterm = form.get('keywords','')
            if searchterm is None or searchterm==u'':
                keywords=[]
            else:
                keywords=searchterm.split(' ')

            num=form.get('numproblems','')
            if num is None or num==u'':
                num=10
            else:
                num=int(num)

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
                P=P.filter(newtags__in=NewTag.objects.filter(tag__startswith=tag)).distinct()
            else:
                P=Problem.objects.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend).filter(types__type=testtype).distinct()
            for i in keywords:
                P=P.filter(Q(problem_text__contains=i)|Q(mc_problem_text__contains=i)|Q(label=i)|Q(test_label=i))
            blocked_probs = Tprobs.values('problem_id')
            P=P.exclude(id__in=blocked_probs)
            P=list(P)
            shuf
            shuffle(P)
            P=P[0:min(50,num)]
            t=Tprobs.count()
            for i in range(t,t+len(P)):
                sp=SortableProblem(problem=P[i-t],order=i+1,newtest_pk=T.pk)
                sp.save()
                T.problems.add(sp)
            T.num_problems=T.problems.count()
            T.save()
    userprofile = get_or_create_up(request.user)
    types = userprofile.user_type_new.allowed_types.order_by('label')
    tags=sorted(list(NewTag.objects.exclude(label='root')),key=lambda x:x.tag)
    P=list(Tprobs)
    P=sorted(P,key=lambda x:x.order)
    return render(request, 'randomtest/newtesteditview.html',{'sortableproblems': P,'nbar': 'viewmytests','test':T,'types':types,'tags':tags})



@login_required
def tagcounts(request):
    types=list(Type.objects.all())
    tags=list(NewTag.objects.exclude(label='root'))
    tags=sorted(tags,key=lambda x:x.tag)
    tagcounts=[]
    typeheaders=[]
    for i in range(0,len(types)):
        tagcounts.append([])
        typeheaders.append(types[i].type)
    for i in range(0,len(tags)):
        t=tags[i].problems.all()
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
    tags=list(NewTag.objects.exclude(label='root'))
    tags=sorted(tags,key=lambda x:x.tag)
    tagcounts=[]# will be a #types x #tags array
    typeheaders=[]
    for i in range(0,len(types)):
        tagcounts.append([])
        Dcounts={}
        typeheaders.append(types[i].type)
        p=Problem.objects.filter(types__type=types[i].type)
        for j in p:
            for k in j.newtags.all():
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
def tableview(request,**kwargs):
    context={}
    curruserprof = get_or_create_up(request.user)
    if 'username' in kwargs:#if looking at a student
        username = kwargs['username']
        user=get_object_or_404(User,username=username)
        if user not in curruserprof.students.all():
            return HttpResponse('Unauthorized', status=401)
        userprof = get_or_create_up(user)
        context['username'] = username
        currusertests = curruserprof.usertests.all()
        usertests = userprof.usertests.all()
        currtests = Test.objects.filter(id__in=currusertests.values('test_id'))
        context['currusertests'] = currtests.exclude(id__in=usertests.values('test_id'))
    else:
        userprof = get_or_create_up(request.user)

    template=loader.get_template('randomtest/tableview.html')
    usertests=userprof.usertests.all()
    folders=userprof.folders.all()
    frows=[]
    for k in range(0,folders.count()):
        ftests=folders[k].tests.all()
        total_probs=0
        for i in ftests:
            total_probs+=i.problems.count()
        correct_probs=0
        for i in range(0,ftests.count()):
            if Responses.objects.filter(test=ftests[i],user_profile=userprof).exists() == False:
                allresponses=Responses(test=ftests[i],num_problems_correct=0)
                allresponses.save()
                P=ftests[i].problems.all()
                for j in range(0,P.count()):
                    r=Response(response='',problem_label=P[j].label,problem=P[j])
                    r.save()
                    allresponses.responses.add(r)
                allresponses.save()
                userprof.allresponses.add(allresponses)
                userprof.save()
            else:
                allresponses=Responses.objects.get(test=ftests[i],user_profile=userprof)
            correct_probs+=allresponses.num_problems_correct
        frows.append((folders[k].name,int(correct_probs*100/max(1,total_probs)),correct_probs,total_probs))


    weekofresponses = userprof.responselog.filter(modified_date__date__gte=datetime.today().date()-timedelta(days=7)).filter(correct=1)
    daycorrect=[((datetime.today().date()-timedelta(days=i)).strftime('%A, %B %d'),str(weekofresponses.filter(modified_date__date=datetime.today().date()-timedelta(days=i)).count()),pointsum(weekofresponses.filter(modified_date__date=datetime.today().date()-timedelta(days=i)))) for i in range(1,7)]

    todaycorrect=str(userprof.responselog.filter(modified_date__date=datetime.today().date()).filter(correct=1).count())
    pointtoday=str(pointsum(userprof.responselog.filter(modified_date__date=datetime.today().date()).filter(correct=1)))

    context['nbar'] = 'viewmytests'
    context['usertests'] =  usertests
    context['testcount'] = len(usertests)
    context['frows'] = frows
    context['todaycorrect'] = todaycorrect
    context['weekcorrect'] = daycorrect
    context['pointtoday'] = pointtoday
    context['stickies'] = userprof.stickies.all().order_by('-sticky_date')
    context['responselog'] = userprof.responselog.all().order_by('-modified_date')[0:50]
    return HttpResponse(template.render(context,request))

@login_required
def addtestview(request,**kwargs):#pk
    pk=kwargs['pk']
    curruserprof = get_or_create_up(request.user)
    if 'username' in kwargs:#if looking at a student
        username = kwargs['username']
        user=get_object_or_404(User,username=username)
        if user not in curruserprof.students.all():
            return HttpResponse('Unauthorized', status=401)
        userprof = get_or_create_up(user)
    else:
        userprof = get_or_create_up(request.user)
    test = get_object_or_404(Test,pk=pk)
    allresponses=Responses(test = test,num_problems_correct=0)
    allresponses.save()
    P=test.problems.all()
    for j in P:
        r=Response(response='',problem_label=j.label,problem=P[j])
        r.save()
        allresponses.responses.add(r)
    allresponses.save()
    userprof.allresponses.add(allresponses)
    ut=UserTest(test = test,responses = allresponses,num_probs = P.count(),num_correct = 0)
    ut.save()
    userprof.usertests.add(ut)
    userprof.save()
    if 'username' in kwargs:
        return redirect('../../')
    else:
        return redirect('/test/'+str(ut.pk))

@login_required
def addfolderview(request,pk):
    userprof = get_or_create_up(request.user)
    fold = Folder.objects.get(pk=pk)
    for t in fold.tests.all():
        test = get_object_or_404(Test,pk=t.pk)
        allresponses=Responses(test = test,num_problems_correct=0)
        allresponses.save()
        P=test.problems.all()
        for j in P:
            r=Response(response='',problem_label=j.label,problem=j)
            r.save()
            allresponses.responses.add(r)
        allresponses.save()
        userprof.allresponses.add(allresponses)
        ut=UserTest(test = test,responses = allresponses,num_probs = P.count(),num_correct = 0)
        ut.save()
        userprof.usertests.add(ut)
        userprof.save()
    userprof.folders.add(fold)
    userprof.save()
    return redirect('/')
    

@login_required
def highscore(request,**kwargs):
#    pk=kwargs['pk']
    context={}
    if 'username' in kwargs:
        curruserprof=get_or_create_up(request.user)
        user=get_object_or_404(User,username=kwargs['username'])
        if  user not in curruserprof.students.all():
            return HttpResponse('Unauthorized', status=401)
        userprof = get_or_create_up(user)
        context['username']=kwargs['username']
    else:
        userprof = get_or_create_up(request.user)
    weekofresponses = userprof.responselog.filter(modified_date__date__gte=datetime.today().date()-timedelta(days=50)).filter(correct=1)
    daycorrect=[((datetime.today().date()-timedelta(days=i)).strftime('%A, %B %d'),str(weekofresponses.filter(modified_date__date=datetime.today().date()-timedelta(days=i)).count()),pointsum(weekofresponses.filter(modified_date__date=datetime.today().date()-timedelta(days=i)))) for i in range(0,50)]
    daycorrect=sorted(daycorrect,key=lambda x:-x[2])[0:10]
    template=loader.get_template('randomtest/highscores.html')
    context['daycorrect'] = daycorrect
    context['nbar'] = 'viewmytests'
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
            rows.append(r)
        allresponses.num_problems_correct=num_correct
        allresponses.show_answer_marks=1
        allresponses.save()
        usertest.num_correct = num_correct
        usertest.save()
        R=allresponses.responses
    else:
        R=allresponses.responses
        rows=R.all()
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
            r=Response(response='',problem_label=P[i].label,problem=P[i])
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
    taglist=sorted(list(NewTag.objects.exclude(label='root')),key=lambda x:x.tag)
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
                    matches=matches.filter(newtags__in=NewTag.objects.filter(tag__startswith=tag))
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
                    r=Response(response='',problem_label=matches[i].label,problem=matches[i])
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
    context['problem']=prob
    context['testpk']=testpk
    context['testname']=usertest.test.name
    context['nbar']='viewmytests'
    return render(request, 'randomtest/solview.html', context)

@login_required
def archiveview(request,tpk):
    userprof=get_or_create_up(request.user)
    test = get_object_or_404(Test, pk=tpk) 
    userprof.archived_tests.add(test)
    userprof.tests.remove(test)
    tists=userprof.timestamps.filter(test_pk=test.pk)
    if tists.count()==0:
        ti=TestTimeStamp(test_pk=test.pk)
    else:
        ti=userprof.timestamps.get(test_pk=test.pk)
        ti.date_added=timezone.now()
    ti.save()
    userprof.timestamps.add(ti)
    return redirect('../../')

@login_required
def archivestudentview(request,username,tpk):
    user = get_object_or_404(User,username=username)
    userprof=get_or_create_up(user)
    test = get_object_or_404(Test, pk=tpk) 
    userprof.archived_tests.add(test)
    userprof.tests.remove(test)
    tists=userprof.timestamps.filter(test_pk=test.pk)
    if tists.count()==0:
        ti=TestTimeStamp(test_pk=test.pk)
    else:
        ti=userprof.timestamps.get(test_pk=test.pk)
        ti.date_added=timezone.now()
    ti.save()
    userprof.timestamps.add(ti)
    return redirect('../../')

@login_required
def unarchiveview(request,tpk):
    userprof=get_or_create_up(request.user)
    test = get_object_or_404(Test, pk=tpk) 
    userprof.archived_tests.remove(test)
    userprof.tests.add(test)
    tists=userprof.timestamps.filter(test_pk=test.pk)
    if tists.count()==0:
        ti=TestTimeStamp(test_pk=test.pk)
    else:
        ti=userprof.timestamps.get(test_pk=test.pk)
        ti.date_added=timezone.now()
    ti.save()
    userprof.timestamps.add(ti)
    return redirect('../../')

@login_required
def unarchivestudentview(request,username,tpk):
    user = get_object_or_404(User,username=username)
    userprof=get_or_create_up(user)
    test = get_object_or_404(Test, pk=tpk) 
    userprof.archived_tests.remove(test)
    userprof.tests.add(test)
    tists=userprof.timestamps.filter(test_pk=test.pk)
    if tists.count()==0:
        ti=TestTimeStamp(test_pk=test.pk)
    else:
        ti=userprof.timestamps.get(test_pk=test.pk)
        ti.date_added=timezone.now()
    ti.save()
    userprof.timestamps.add(ti)
    return redirect('../../')

@login_required
def urltest(request):
    context={}
    if request.method=='GET':
        form=request.GET
        L=form.getlist('p')
        rows=[]
        for i in range(0,len(L)):
            if Problem.objects.filter(pk=L[i]).exists():
                p=Problem.objects.get(pk=L[i])
                if p.question_type_new.question_type=='multiple choice' or p.question_type_new.question_type=='multiple choice short answer':
                    rows.append((p.display_problem_text,p.readable_label))
                else:
                    rows.append((p.display_problem_text,p.readable_label))
    context['rows'] = rows
    context['nbar'] = 'viewmytests'
#    context['name'] = test.name
    return render(request, 'randomtest/urltest.html',context)


@login_required
def urllatexview(request):
    if request.method=='GET':
        form=request.GET
        L=form.getlist('p')
        rows=[]
        for i in range(0,len(L)):
            if Problem.objects.filter(pk=L[i]).exists():
                p=Problem.objects.get(pk=L[i])
                ptext=''
                if p.question_type_new.question_type=='multiple choice' or p.question_type_new.question_type=='multiple choice short answer':
                    ptext=p.mc_problem_text
                    rows.append((ptext,p.readable_label,p.answers()))
                else:
                    ptext=p.problem_text
                    rows.append((ptext,p.readable_label,''))
    return render(request, 'randomtest/latexview.html',{'rows': rows,'nbar': 'viewmytests', 'include_problem_labels' : True})

@login_required
def urllatexsolview(request):
    if request.method=='GET':
        form=request.GET
        L=form.getlist('p')
        rows=[]
        for i in range(0,len(L)):
            if Problem.objects.filter(pk=L[i]).exists():
                p=Problem.objects.get(pk=L[i])
                ptext=''
                if p.question_type_new.question_type=='multiple choice' or p.question_type_new.question_type=='multiple choice short answer':
                    ptext=p.mc_problem_text
                    rows.append((ptext,p.readable_label,p.answers(),p.solutions.all()))
                else:
                    ptext=p.problem_text
                    rows.append((ptext,p.readable_label,'',p.solutions.all()))
    return render(request, 'randomtest/latexsolview.html',{'rows': rows,'nbar': 'viewmytests', 'include_problem_labels' : True})

@login_required
def urltemptest(request):
    proburl=''
    latexurl=''
    sollatexurl=''
    labeltext=''
    if request.method=='POST':
        form=request.POST
        labeltext = form.get('labels','')
        labels = labeltext.split(',')
        labels = [labels[i].rstrip().lstrip().upper() for i in range(0,len(labels))]
        s='?'
        for i in range(0,len(labels)):
            if Problem.objects.filter(label=labels[i]).exists():
                p=Problem.objects.get(label=labels[i])
                s+='&p='+str(p.pk)
        proburl='test'+s
        latexurl='latex'+s
        sollatexurl='latexsol'+s
    return render(request,'randomtest/temptest.html',{'proburl' : proburl, 'latexurl' : latexurl, 'sollatexurl' : sollatexurl,'labeltext' : labeltext,'nbar':'viewmytests'})

@login_required
def profileview(request,username):
    user = get_object_or_404(User, username=username)
    log = LogEntry.objects.filter(user_id = user.id).filter(change_message__contains="problemeditor")
    linkedlog=[]
    for i in log:
        if i.content_type.name=='problem':
            if Problem.objects.filter(pk=i.object_id).exists():
                linkedlog.append((i,True))
            else:
                linkedlog.append((i,False))
        if i.content_type.name=='solution':
            if Solution.objects.filter(pk=i.object_id).exists():
                linkedlog.append((i,True))
            else:
                linkedlog.append((i,False))
        if i.content_type.name=='problem approval':
            if ProblemApproval.objects.filter(pk=i.object_id).exists():
                linkedlog.append((i,True))
            else:
                linkedlog.append((i,False))


    paginator=Paginator(linkedlog,50)
    page = request.GET.get('page')
    try:
        plog=paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.                                             
        plog = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.                         
        plog = paginator.page(paginator.num_pages)
    return render(request,'randomtest/activity_log.html',{'log':plog,'nbar':'viewmytests','username':username})


class SolutionView(DetailView):
    model = Problem
    template_name = 'randomtest/load_sol.html'

    def dispatch(self, *args, **kwargs):
        self.item_id = kwargs['ppk']
        return super(SolutionView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Problem, pk=self.item_id)
