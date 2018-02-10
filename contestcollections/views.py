from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.template.loader import render_to_string
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

from django.views.generic import DetailView

from subprocess import Popen,PIPE
import tempfile
import os

from randomtest.models import Problem, Tag, Type, Test, UserProfile,  QuestionType,Dropboxurl,get_or_create_up,UserResponse,Sticky,TestCollection

from randomtest.utils import parsebool,newtexcode,newsoltexcode

from random import shuffle
import time
from datetime import datetime,timedelta
import random

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
    userprofile,boolcreated = UserProfile.objects.get_or_create(user=request.user)
    test = get_object_or_404(Test, pk=pk)
    P=list(test.problems.all())
    P=sorted(P,key=lambda x:(x.problem_number_prefix,x.problem_number,x.year))
    return render(request, 'contestcollections/testview.html',{'rows': P,'pk' : pk,'nbar': 'contestcollection', 'name':test.name})

@login_required
def solutionview(request,testpk,pk):
    prob = get_object_or_404(Problem, pk=pk)
    test = get_object_or_404(Test, pk=testpk)
    context={}
    context['prob']=prob
    context['testpk']=testpk
    context['testname']=test.name
    context['nbar']='contestcollection'
    return render(request, 'contestcollections/solview.html', context)

#@login_required
#def load_solution(request,testpk,pk):
#    prob = get_object_or_404(Problem, pk=pk)
#    test = get_object_or_404(Test, pk=testpk)
#    context={}
#    context['prob']=prob
#    return HttpResponse(render_to_string('contestcollections/load_sol.html', context))

class SolutionView(DetailView):
    model = Problem
    template_name = 'contestcollections/load_sol.html'

    def dispatch(self, *args, **kwargs):
        self.item_id = kwargs['pk']
        return super(SolutionView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Problem, pk=self.item_id)


@login_required
def test_as_pdf(request,**kwargs):
    test = get_object_or_404(Test, pk=kwargs['pk'])
    P=list(test.problems.all())
    rows=[]
    if 'opts' in kwargs:
        options = kwargs['opts']
        include_problem_labels = options['pl'] 
        include_answer_choices = options['ac']
        randomize = options['r']
    else:
        include_problem_labels = False
        include_answer_choices = True
        randomize = False
    if randomize:
        seed = options['seed']
        random.Random(seed).shuffle(P)
    else:
        seed = 0
    for i in range(0,len(P)):
        ptext=''
        if P[i].question_type_new.question_type=='multiple choice' or P[i].question_type_new.question_type=='multiple choice short answer':
            ptext=P[i].mc_problem_text
            rows.append((P[i],ptext,P[i].readable_label,P[i].answers()))
        else:
            ptext=P[i].problem_text
            rows.append((P[i],ptext,P[i].readable_label,''))
#    if request.method == "GET":
#        if request.GET.get('problemlabels')=='no':
#            include_problem_labels = False
    context = Context({
            'name':test.name,
            'rows':rows,
            'pk':kwargs['pk'],
            'include_problem_labels':include_problem_labels,
            })
    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('randomtest/my_latex_template.tex')
    rendered_tpl = template.render(context).encode('utf-8')
    with tempfile.TemporaryDirectory() as tempdir:
        fa=open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        context = Context({
                'name':test.name,
                'rows':rows,
                'pk':kwargs['pk'],
                'include_problem_labels':include_problem_labels,
                'include_answer_choices':include_answer_choices,
                'randomize': randomize,
                'seed': seed,
                'tempdirect':tempdir,
                })
        template = get_template('randomtest/my_latex_template.tex')
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
            if L[i][-4:]=='.asy':
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
                stdin=PIPE,
                stdout=PIPE,
                cwd = tempdir,
            )
            stdout_value = process2.communicate()[0]

        if 'texput.pdf' in os.listdir(tempdir):
            with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
                pdf = f.read()
                r = HttpResponse(content_type='application/pdf')
                r.write(pdf)
                r['Content-Disposition'] = 'attachment;filename="'+test.name.replace(' ','')+'.pdf"'
                return r
        else:
            with open(os.path.join(tempdir, 'texput.log')) as f:
                error_text = f.read()
                return render(request,'randomtest/latex_errors.html',{'nbar':'randomtest','name':test.name,'error_text':error_text})#####Perhaps the error page needs to be customized...


@login_required
def test_sol_as_pdf(request,**kwargs):
    test = get_object_or_404(Test, pk=kwargs['pk'])
    P=list(test.problems.all())
    rows=[]
    if 'opts' in kwargs:
        options = kwargs['opts']
        include_problem_labels = options['pl'] 
        include_answer_choices = options['ac']
        include_problem_notes = options['pn']
        randomize = options['r']
    else:
        include_problem_labels = False
        include_answer_choices = True
        include_problem_notes = False
        randomize = False
    if randomize:
        seed = options['seed']
        random.Random(seed).shuffle(P)
    else:
        seed = 0
    for i in range(0,len(P)):
        ptext=''
        if P[i].question_type_new.question_type=='multiple choice' or P[i].question_type_new.question_type=='multiple choice short answer':
            ptext=P[i].mc_problem_text
            rows.append((P[i],ptext,P[i].readable_label,P[i].answers(),P[i].solutions.all()))
        else:
            ptext=P[i].problem_text
            rows.append((P[i],ptext,P[i].readable_label,'',P[i].solutions.all()))
    if request.method == "GET":
        if request.GET.get('problemlabels')=='no':
            include_problem_labels = False
    context = Context({
            'name':test.name,
            'rows':rows,
            'pk':kwargs['pk'],
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
        context = Context({
                'name':test.name,
                'rows':rows,
                'pk':kwargs['pk'],
                'include_problem_labels':include_problem_labels,
                'include_problem_notes':include_problem_notes,
                'include_answer_choices':include_answer_choices,
                'randomize': randomize,
                'seed': seed,
                'tempdirect':tempdir,
                })
        template = get_template('randomtest/my_latex_sol_template.tex')
        rendered_tpl = template.render(context).encode('utf-8')
        ftex=open(os.path.join(tempdir,'texput.tex'),'wb')
        ftex.write(rendered_tpl)
        ftex.close()
        for i in range(1):
            process = Popen(
                ['pdflatex', 'texput.tex'],
                stdin=PIPE,
                stdout=PIPE,
                cwd = tempdir,
            )
            stdout_value = process.communicate()[0]
        L=os.listdir(tempdir)
        for i in range(0,len(L)):
            if L[i][-4:]=='.asy':
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
                stdin=PIPE,
                stdout=PIPE,
                cwd = tempdir,
            )
            stdout_value = process2.communicate()[0]

        if 'texput.pdf' in os.listdir(tempdir):
            with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
                pdf = f.read()
                r = HttpResponse(content_type='application/pdf')
                r.write(pdf)
                r['Content-Disposition'] = 'attachment;filename="'+test.name.replace(' ','')+'solutions.pdf"'
                return r
        else:
            with open(os.path.join(tempdir, 'texput.log')) as f:
                error_text = f.read()
                return render(request,'randomtest/latex_errors.html',{'nbar':'randomtest','name':test.name,'error_text':error_text})

@login_required
def test_answer_key_as_pdf(request, **kwargs):
    test = get_object_or_404(Test, pk=kwargs['pk'])
    P = list(test.problems.all())
    rows=[]
    if 'opts' in kwargs:
        options = kwargs['opts']
        include_problem_labels = options['pl'] 
        include_answer_choices = options['ac']
        randomize = options['r']
    else:
        include_problem_labels = False
        include_answer_choices = True
        randomize = False
    if randomize:
        seed = options['seed']
        random.Random(seed).shuffle(P)
    else:
        seed = 0

    for i in range(0,len(P)):
        rows = P
    # Python3 only. For python2 check out the docs!                                                  
    with tempfile.TemporaryDirectory() as tempdir:
        # Create subprocess, supress output with PIPE and
        # run latex twice to generate the TOC properly.
        # Finally read the generated pdf.
        context = Context({
                'name':test.name,
                'rows':rows,
                'pk':kwargs['pk'],
                'include_problem_labels':include_problem_labels,
                'randomize': randomize,
                'seed':seed,
                'tempdirect':tempdir,
                })
        template = get_template('randomtest/my_latex_answerkey_template.tex')
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
                r['Content-Disposition'] = 'attachment;filename="'+test.name.replace(' ','')+'answerkey.pdf"'

                return r
        else:
            with open(os.path.join(tempdir, 'texput.log')) as f:
                error_text = f.read()
                return render(request,'randomtest/latex_errors.html',{'nbar':'randomtest','name':test.name,'error_text':error_text})

@login_required
def testpdfoptions(request,pk):
    test = get_object_or_404(Test,pk=pk)
    return render(request,'contestcollections/pdfcreator.html',{'test':test,'nbar':'contestcollection'})

@login_required
def problempdf(request,pk):
    form = request.GET
    context = {}
    if 'include-acs' in form:
        context['ac'] = 1
    else:
        context['ac'] = 0
    if 'include-pls' in form:
        context['pl'] = 1
    else:
        context['pl'] = 0
    if 'randomize' in form:
        context['r'] = 1
        if 'random-seed' in form:
            context['seed'] = int(form.get('random-seed',''))
        else:
            context['seed'] = 0
    else:
        context['r'] = 0
    return test_as_pdf(request,pk=pk,opts = context)

@login_required
def solutionpdf(request,pk):
    form = request.GET
    context = {}
    context['ac'] = 1
    if 'include-pls' in form:
        context['pl'] = 1
    else:
        context['pl'] = 0
    if 'include-pn' in form:
        context['pn'] = 1
    else:
        context['pn'] = 0
    if 'randomize' in form:
        context['r'] = 1
        if 'random-seed' in form:
            context['seed'] = int(form.get('random-seed',''))
        else:
            context['seed'] = 0
    else:
        context['r'] = 0
    return test_sol_as_pdf(request,pk=pk,opts = context)


@login_required
def answerkeypdf(request,pk):
    form = request.GET
    context = {}
    context['ac'] = 1
    if 'include-pls' in form:
        context['pl'] = 1
    else:
        context['pl'] = 0
    if 'randomize' in form:
        context['r'] = 1
        if 'random-seed' in form:
            context['seed'] = int(form.get('random-seed',''))
        else:
            context['seed'] = 0
    else:
        context['r'] = 0
    return test_answer_key_as_pdf(request,pk=pk,opts = context)
