from django.shortcuts import render,render_to_response, get_object_or_404,redirect
#from django.template import loader,RequestContext,Context

from django.template.loader import get_template

#from django.contrib.auth import authenticate,login,logout
#from django.contrib.auth.admin import User
from django.contrib.auth.decorators import login_required
#from django.conf import settings
#from django.contrib.admin.models import LogEntry
#from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#from subprocess import Popen,PIPE
#import tempfile
#import os

# Create your views here.

@login_required
def handouteditview(request,pk):
    h=get_object_or_404(Handout,pk=pk)
#    if request.method == "POST":
#        if 'save' in request.POST:
#            form=request.POST
#            if 'probleminput' in form:
#                P=list(T.problems.all())
#                P=sorted(P,key=lambda x:x.order)
#                probinputs=form.getlist('probleminput')#could be an issue if no problems             
#                for prob in P:
#                    if 'problem_'+str(prob.pk) not in probinputs:
#                        prob.delete()
#                for i in range(0,len(probinputs)):
#                    prob=T.problems.get(pk=probinputs[i].split('_')[1])
#                    prob.order=i+1
#                    prob.save()
    doc_elements = list(h.document_elements.all())
    doc_elements = sorted(doc_elements,key=lambda x:x.order)
    return render(request, 'handouts/handouteditview.html',{'doc_elements': doc_elements,'nbar': 'viewmytests','handout':h})    
