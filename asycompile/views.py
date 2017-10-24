from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.template import loader,RequestContext,Context

from django.template.loader import get_template

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from formtools.wizard.views import SessionWizardView

from randomtest.models import Problem, Tag, Type, Test, UserProfile, Solution,Comment,QuestionType,ProblemApproval
from .forms import AsyForm
from randomtest.utils import goodtag,goodurl,newtexcode,newsoltexcode

from django.conf import settings

from subprocess import Popen,PIPE
import subprocess
import tempfile
import os,os.path


# Create your views here.
@login_required
def asytestview(request):
    if request.method == "POST":
        if request.POST.get("save"):
            asylist=request.POST.getlist('asy_code')
            asy_code=asylist[0]
            fnamelist=request.POST.getlist('filename')
            filename=fnamelist[0]
            context = Context({
                    'asy_code':asy_code,
                    'filename':filename,
                    })
            template = get_template('asycompile/my_asy_template.asy')
            rendered_tpl = template.render(context).encode('utf-8')
#            print(settings.MEDIA_ROOT)
#            print(rendered_tpl)
            with tempfile.TemporaryDirectory() as tempdir:
                process = Popen(
                    ['asy', '-o', os.path.join(tempdir,filename+'.pdf')],
                    stdin=PIPE,
                    stdout=PIPE,
                    )
                process.communicate(rendered_tpl)
                L=os.listdir(tempdir)
#                print(L)
                for i in L:
                    if 'pdf' in i:
                        print(i)
                        command = "convert -density 150 -quality 95 %s/%s %s%s" % (tempdir, i, settings.MEDIA_ROOT, i.replace('.pdf','.jpg'))
                        print(command)
                        proc = subprocess.Popen(command,
                                                shell=True,
                                                stdin=subprocess.PIPE,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE,
                                                )
                        stdout_value = proc.communicate()[0]
            return redirect('/')
    form = AsyForm()
    breadcrumbs=[('../','Home'),]
    return render(request, 'asycompile/editasy.html', {'form': form, 'nbar': 'viewmytests',})
