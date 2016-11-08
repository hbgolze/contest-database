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


from .models import Problem, Tag, Type, Test, UserProfile, Response, Responses, QuestionType,Dropboxurl,get_or_create_up
from .forms import TestForm,UserForm,UserProfileForm,TestModelForm

from .utils import parsebool
from random import shuffle
import time

# Create your views here.

class TestDelete(DeleteView):
    model = Test
    success_url = reverse_lazy('tableview')

@login_required
def deletetestresponses(request,pk):
    test = get_object_or_404(Test, pk=pk)
    if test.responses_set.count()<=1:
        test.delete()
    else:
        userprofile = get_or_create_up(request.user)
        testresponses = Responses.objects.filter(test=test).filter(user_profile=userprofile)
        if testresponses.count()>=1:
            testresponses.delete()
        userprofile.tests.remove(test)
    return redirect('/')

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
            U.save()
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
            U.save()
            T.types.add(Type.objects.get(type=testtype))
            T.save()
#            return testview(request,T.pk)
            return redirect('/test/'+str(T.pk)+'/')
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
def tagcounts(request):
    types=list(Type.objects.all())
    tags=list(Tag.objects.all())
    tags=sorted(tags,key=lambda x:x.tag)
    tagcounts=[]
    typeheaders=[]
    for i in range(0,len(types)):
        tagcounts.append([])
        typeheaders.append(types[i].type)
    for i in range(0,len(tags)):
        t=Problem.objects.filter(tags__in=[tags[i]])
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

@login_required
def tableview(request):
    template=loader.get_template('randomtest/tableview.html')
    userprof = get_or_create_up(request.user)
    tests=list(userprof.tests.all())
    rows=[]
    for i in range(0,len(tests)):
#        if userprof.tests.filter(pk=tests[i].pk).count()==0:
#        userprof.tests.add(tests[i])#this line was indented
#        userprof.save()
#        testresponses = Responses.objects.filter(test=tests[i]).filter(user_profile=userprof)
        testresponses=userprof.allresponses.filter(test=tests[i])
        if testresponses.count()==0:
            allresponses=Responses(test=tests[i],num_problems_correct=0)
            allresponses.save()
            P=list(tests[i].problems.all())
            for j in range(0,len(P)):
                r=Response(response='',problem_label=P[j].label)
                r.save()
                allresponses.responses.add(r)
            allresponses.save()
            userprof.allresponses.add(allresponses)
            userprof.save()
        else:
            allresponses=Responses.objects.get(test=tests[i],user_profile=userprof)
        rows.append((tests[i].pk,tests[i].name,tests[i].types.all(),allresponses.num_problems_correct,tests[i].problems.count(),tests[i].created_date))
    context= {'testcount':len(tests),'rows': rows, 'nbar': 'viewmytests'}
    return HttpResponse(template.render(context,request))

@login_required
def testview(request,pk):
    test = get_object_or_404(Test, pk=pk)
    userprofile = get_or_create_up(request.user)
    if userprofile.tests.filter(pk=pk).count()==0:
        userprofile.tests.add(test)
    userprofile.save()
    testresponses = Responses.objects.filter(test=test).filter(user_profile=userprofile)
    if testresponses.count()==0:
        allresponses=Responses(test=test,num_problems_correct=0)
        allresponses.save()
        P=list(test.problems.all())
        for i in range(0,len(P)):
            r=Response(response='',problem_label=P[i].label)
            r.save()
            allresponses.responses.add(r)
        allresponses.save()
        userprofile.allresponses.add(allresponses)
        userprofile.save()
    else:
        allresponses=Responses.objects.get(test=test,user_profile=userprofile)
    
    dropboxpath = list(Dropboxurl.objects.all())[0].url
    if request.method == "POST":
        form=request.POST
        P=list(test.problems.all())
        P=sorted(P,key=lambda x:(x.problem_number,x.year))
        num_correct=0
        for i in range(0,len(P)):
            r=allresponses.responses.get(problem_label=P[i].label)
            r.response = form.get('answer'+P[i].label)
            if r.response==None:
                r.response=''
            r.save()
            if r.response==P[i].answer and P[i].question_type.filter(question_type='proof').count()==0:
                num_correct+=1
        allresponses.num_problems_correct=num_correct
        allresponses.show_answer_marks=1
        allresponses.save()
        R=allresponses.responses
        rows=[]
        for i in range(0,len(P)):
            rows.append((P[i].label,str(P[i].answer),R.get(problem_label=P[i].label).response,list(P[i].question_type.all())[0]))
    else:
        P=list(test.problems.all())
        P=sorted(P,key=lambda x:(x.problem_number,x.year))
        R=allresponses.responses
        rows=[]
        for i in range(0,len(P)):
            rows.append((P[i].label,str(P[i].answer),R.get(problem_label=P[i].label).response,list(P[i].question_type.all())[0]))
    return render(request, 'randomtest/testview.html',{'rows': rows,'pk' : pk,'nbar': 'viewmytests', 'dropboxpath': dropboxpath,'name':test.name,'show_marks':allresponses.show_answer_marks})



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
                    matches=Problem.objects.filter(problem_number__gte=probbegin,problem_number__lte=probend).filter(year__gte=yearbegin,year__lte=yearend).filter(types__type=testtype)
                    if boo=='or':
                        matches=matches.filter(Q(tags__in=Tag.objects.filter(tag__in=taglist)) | Q(test_label__in=taglist) | Q(label__in=taglist))
                    else:
                        for t in taglist:
                            matches=matches.filter(tags__in=Tag.objects.filter(tag__in=[t]))#this doesn't account for test/problem tags at the moment...(problem tags unnecessary with AND).
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
    return render(request, 'randomtest/testeditview.html',{'rows': rows,'pk' : pk,'nbar': 'viewmytests','msg':msg, 'dropboxpath': dropboxpath, 'testrows' : testrows})

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
        rows.append((P[i].problem_text,P[i].readable_label,P[i].answer_choices))
    if request.method == "GET":
        if request.GET.get('problemlabels')=='no':
            include_problem_labels = False
    return render(request, 'randomtest/latexview.html',{'name': test.name,'rows': rows,'pk' : pk,'nbar': 'viewmytests', 'include_problem_labels' : include_problem_labels})

@login_required
def readme(request):
    return render(request,'randomtest/readme.html',{'nbar':'newtest'})
