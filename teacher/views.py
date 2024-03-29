from django.shortcuts import render, get_object_or_404,redirect
from django.views.generic import UpdateView,DetailView,ListView,CreateView
from django.template.loader import get_template,render_to_string
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,Http404,HttpResponse

from django.contrib.auth.models import User
from django.template import loader

from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from datetime import datetime,timedelta,time
from django.utils import timezone
from django.conf import settings
import pytz

from randomtest.utils import newtexcode,compileasy,compiletikz,pointsum,newsoltexcode
from randomtest.models import QuestionType,ProblemGroup,Problem,NewTag,NewResponse,Solution,UserProfile

from teacher.models import Class,PublishedClass,Unit,ProblemSet,SlideGroup,UnitObject,ProblemObject,Slide,SlideObject,TextBlock,Proof,Theorem,ImageModel,ExampleProblem,Test
from teacher.models import PublishedUnit,PublishedProblemSet,PublishedSlideGroup,PublishedUnitObject,PublishedProblemObject,PublishedSlide,PublishedSlideObject,PublishedTest,SolutionObject
from teacher.forms import NewProblemObjectMCForm, NewProblemObjectSAForm, NewProblemObjectPFForm,PointValueForm,SearchForm,AddProblemsForm,TheoremForm,ProofForm,TextBlockForm,ImageForm,LabelForm,NewExampleProblemMCForm,NewExampleProblemSAForm,NewExampleProblemPFForm
from teacher.forms import BlankPointValueForm,EditClassNameForm,EditUnitNameForm,EditProblemSetNameForm,EditTestNameForm,EditSlideGroupNameForm,EditSlideTitleForm,NewSolutionObjectForm,EditSolutionObjectForm
from groups.forms import GroupModelForm
from student.models import UserClass,UserUnit,UserProblemSet,UserUnitObject,UserSlides,Response

from subprocess import Popen,PIPE
import tempfile
import os

from itertools import chain
from random import shuffle
#from teacher.forms import UnitForm
# Create your views here.

#Should I allow syncing of a class to its parents???
@login_required
def teacherview(request):
    userprofile=request.user.userprofile
    if request.method == "POST":
        form=request.POST
        if "newclass" in form:
            c=Class(name=form.get("class-name",""))
            c.save()
            userprofile.my_classes.add(c)
            userprofile.save()
            return JsonResponse({"newrow":render_to_string("teacher/editingtemplates/editclassrow.html",{'cls':c,'sharing_type': 'own'})})
#reorder sections in post...
    owned_cls =  userprofile.my_classes.all()
    co_owned_cls =  userprofile.owned_my_classes.all()
    editor_cls =  userprofile.editable_my_classes.all()
    readonly_cls =  userprofile.readonly_my_classes.all()
    context={}
#    context['my_classes'] = userprofile.my_classes
    context['my_published_classes'] = userprofile.my_published_classes
    context['my_TA_classes'] = userprofile.my_TA_classes
    context['my_students'] = userprofile.students
    context['nbar'] = 'teacher'

    context['owned_cls'] = owned_cls
    context['co_owned_cls'] = co_owned_cls
    context['editor_cls'] = editor_cls
    context['readonly_cls'] = readonly_cls
    return render(request, 'teacher/teacherview.html',context)

@login_required
def get_permission_level(request,cls):
    userprofile = request.user.userprofile
    if userprofile.my_classes.filter(pk=cls.pk).exists():
        return "own"
    if userprofile.owned_my_classes.filter(pk=cls.pk).exists():
        return "coown"
    if userprofile.editable_my_classes.filter(pk=cls.pk).exists():
        return "edit"
    if userprofile.readonly_my_classes.filter(pk=cls.pk).exists():
        return "read"
    return "none"

@login_required
def publishview(request,pk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if get_permission_level(request,my_class) == "none":#userprofile.my_classes.filter(pk=pk).exists()==False:##########Currently means "actual owners" are the only people who can 
        raise Http404("Unauthorized.")
    p = my_class.publish(userprofile)
    return JsonResponse({'newrow':render_to_string('teacher/publishedclasses/publishedclassrow.html',{'cls':p})})

@login_required
def confirm_delete_class(request):
    pk = request.POST.get('pk','')
    cls = get_object_or_404(Class, pk=pk)
    context = {}
    context['cls'] = cls
    return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/modals/modal-delete-class.html',context)})
@login_required
def confirm_remove_class(request):
    pk = request.POST.get('pk','')
    cls = get_object_or_404(Class, pk=pk)
    context = {}
    context['cls'] = cls
    return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/modals/modal-remove-class.html',context)})

@login_required
def delete_class(request):
    pk = request.POST.get('pk','')
    cls = get_object_or_404(Class, pk=pk)
    userprofile = request.user.userprofile
    if cls in userprofile.my_classes.all():
        cls.delete()
    return JsonResponse({'s':1})

@login_required
def remove_class(request):
    pk = request.POST.get('pk','')
    cls = get_object_or_404(Clas, pk=pk)
    userprofile = request.user.userprofile
    if cls in userprofile.owned_my_classes.all():
        userprofile.owned_my_classes.remove(cls)
        userprofile.save()
    elif cls in userprofile.editable_my_classes.all():
        userprofile.editable_my_classes.remove(cls)
        userprofile.save()
    elif cls in userprofile.readonly_my_classes.all():
        userprofile.readonly_my_classes.remove(cls)
        userprofile.save()
    return JsonResponse({'s':1})

@login_required
def sync_class(request, pk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(PublishedClass,pk=pk)
    if userprofile.my_published_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    try:
        my_class.sync_to_parent()
        return JsonResponse({"error":0})
    except:
        return JsonResponse({"error":1})
    

@login_required
def rosterview(request,pk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(PublishedClass,pk=pk)
    if userprofile.my_published_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    student_classes = my_class.userclass_set.all()
    return render(request,'teacher/publishedclasses/rosterview.html',{'student_classes':student_classes,'my_class':my_class,'nbar':'teacher'})

@login_required
def assignmentview(request,pk,ppk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(PublishedClass,pk=pk)
    problemset = get_object_or_404(PublishedProblemSet,pk = ppk)
    if userprofile.my_published_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    if problemset.unit_object.unit not in my_class.publishedunit_set.all():##########
        raise Http404("Unauthorized.")
    student_problemsets = problemset.userproblemset_set.all()
    return render(request,'teacher/publishedclasses/roster/assignmentview.html',{'nbar': 'teacher','my_class':my_class,'student_problemsets': student_problemsets,'problemset':problemset})

@login_required
def studentoneclassview(request,**kwargs):
    userprofile = request.user.userprofile

    student_username = kwargs['username']
    pk = kwargs['pk']
    user = get_object_or_404(User,username = student_username)
    my_class = get_object_or_404(PublishedClass, pk=pk)
    if userprofile.my_published_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    if user not in userprofile.students.all():
        raise Http404("Unauthorized.")
    student_userprofile = user.userprofile
    try:
        student_class = my_class.userclass_set.get(userprofile = student_userprofile)
    except UserClass.DoesNotExist:
        raise Http404("Student is not properly enrolled.")
    weekofresponses = student_userprofile.student_responselog.filter(modified_date__date__gte=datetime.today().date()-timedelta(days=7)).filter(correct=1).filter(user_problemset__userunitobject__user_unit__user_class=student_class)
    daycorrect=[((datetime.today().date()-timedelta(days=i)).strftime('%A, %B %d'),str(weekofresponses.filter(modified_date__date=datetime.today().date()-timedelta(days=i)).count()),pointsum(weekofresponses.filter(modified_date__date=datetime.today().date()-timedelta(days=i)))) for i in range(1,7)]

    today_responselog = student_userprofile.student_responselog.filter(modified_date__date=datetime.today().date()).filter(correct=1).filter(user_problemset__userunitobject__user_unit__user_class=student_class)
    todaycorrect=str(today_responselog.count())
    pointtoday=str(pointsum(today_responselog))
    context={}
    context['nbar'] = 'teacher'

    context['todaycorrect'] = todaycorrect
    context['weekcorrect'] = daycorrect
    context['pointtoday'] = pointtoday
    context['stickies'] = student_userprofile.student_stickies.filter(problemset__userunitobject__user_unit__user_class=student_class).order_by('-sticky_date')
    context['responselog'] = student_userprofile.student_responselog.filter(user_problemset__userunitobject__user_unit__user_class=student_class).order_by('-modified_date')[0:50]
    context['class'] = student_class
    context['username'] = student_username

    return render(request,'teacher/students/studentoneclassview.html',context)


@login_required
def studentclassview(request,**kwargs):
    userprofile = request.user.userprofile

    student_username = kwargs['username']
    user = get_object_or_404(User,username = student_username)
    
    if user not in userprofile.students.all():
        raise Http404("Unauthorized.")
    student_userprofile = user.userprofile
    my_published_classes = userprofile.my_published_classes.all()

    classes = student_userprofile.userclasses.filter(published_class__pk__in=my_published_classes)

    weekofresponses = student_userprofile.student_responselog.filter(modified_date__date__gte=datetime.today().date()-timedelta(days=7)).filter(correct=1)
    daycorrect=[((datetime.today().date()-timedelta(days=i)).strftime('%A, %B %d'),str(weekofresponses.filter(modified_date__date=datetime.today().date()-timedelta(days=i)).count()),pointsum(weekofresponses.filter(modified_date__date=datetime.today().date()-timedelta(days=i)))) for i in range(1,7)]

    todaycorrect=str(student_userprofile.student_responselog.filter(modified_date__date=datetime.today().date()).filter(correct=1).count())
    pointtoday=str(pointsum(student_userprofile.student_responselog.filter(modified_date__date=datetime.today().date()).filter(correct=1)))
    context={}
    context['nbar'] = 'teacher'

    context['todaycorrect'] = todaycorrect
    context['weekcorrect'] = daycorrect
    context['pointtoday'] = pointtoday
    context['stickies'] = student_userprofile.student_stickies.all().order_by('-sticky_date')
    context['responselog'] = student_userprofile.student_responselog.all().order_by('-modified_date')[0:50]
    context['classes'] = classes
    context['username'] = student_username
    return render(request,'teacher/students/studentview.html',context)

def studentproblemsetview(request,**kwargs):
    context={}
    if 'pk' in kwargs:
        context['oneclass'] = True
    userprofile=request.user.userprofile
#    pk = kwargs['pk']
#    my_class = get_object_or_404(PublishedClass,pk=pk)
#    if userprofile.my_published_classes.filter(pk=pk).exists()==False:
#        raise Http404("Unauthorized.")
    student_username = kwargs['username']
    user = get_object_or_404(User,username = student_username)
#    if user not in my_class.enrolled_students.all():
#        raise Http404("Unauthorized.")
    student_userprofile = user.userprofile
    upk = kwargs['upk']
    user_problemset = get_object_or_404(UserProblemSet, pk=upk)
    if user_problemset.userunitobject.user_unit.user_class.userprofile != student_userprofile:
        return HttpResponse('Unauthorized', status=401)
    if user_problemset.userunitobject.user_unit.user_class.published_class not in userprofile.my_published_classes.all():
        raise Http404("Unauthorized.")
    if user_problemset.is_initialized == 0:
        user_problemset.response_initialize()
    rows = user_problemset.response_set.all()
    context['rows'] = rows
    response_rows = []
    for i in range(0,int((rows.count()+14)/15)):
        response_rows.append((rows[15*i:15*(i+1)],15*i))
    context['response_rows'] = response_rows
    context['problemset'] = user_problemset
    context['pk'] = upk
    context['nbar'] = 'teacher'
    context['username'] = student_username
    return render(request, 'teacher/publishedclasses/problemsetview.html',context)

class SolutionView(DetailView):
    model = PublishedProblemObject
    template_name = 'teacher/publishedclasses/load_sol.html'

    def dispatch(self, *args, **kwargs):
        self.item_id = kwargs['ppk']
        return super(SolutionView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(PublishedProblemObject, pk=self.item_id)

@login_required
def load_grade(request,**kwargs):
    context={}
    resp_pk = request.GET.get('resp_pk','')
    resp = get_object_or_404(Response,pk=resp_pk)
    context['resp'] = resp
    po = resp.publishedproblem_object
    if po.isProblem:
        if po.question_type == "multiple choice":
            problem_display = po.problem.display_mc_problem_text
        else:
            problem_display = po.problem.display_problem_text
        context['readable_label'] = po.problem.readable_label
    else:
        problem_display = po.problem_display
    context['problem_display'] = problem_display
    pts=[]
    for i in range(0,po.point_value+1):
        pts.append(i)
    context['pts'] = pts
    return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/modals/modal-edit-grade.html',context)})

@login_required
def save_grade(request,**kwargs):
    resp_pk = request.GET.get('eg-pk','')
    resp = get_object_or_404(Response,pk=resp_pk)
    resp.points = request.GET.get('grade-value','')
    resp.is_graded = 1
    resp.save()
    return JsonResponse({'points': resp.points,'pk':resp.pk,'point_value':resp.point_value})

@login_required
def change_grade(request,**kwargs):
    resp_pk = request.GET.get('eg-pk','')
    resp = get_object_or_404(Response,pk=resp_pk)
    selected_grade = request.GET.get('changegrade_'+resp_pk,'')
    if selected_grade == "":
        resp.points = 0
        resp.is_graded = 0
        resp.save()
        return JsonResponse({'points': resp.points,'pk':resp.pk,'point_value':resp.point_value})
    else:
        resp.points = selected_grade
        resp.is_graded = 1
        resp.save()
        return JsonResponse({'points': resp.points,'pk':resp.pk,'point_value':resp.point_value,'graded':1})

@login_required
def slidesview(request,**kwargs):
    context = {}
    userprofile = request.user.userprofile
    if 'pk' in kwargs:
        pk = kwargs['pk']
        spk = kwargs['spk']
        slidegroup = get_object_or_404(PublishedSlideGroup, pk = spk)
        pub_class = get_object_or_404(PublishedClass, pk = pk)
        if userprofile not in pub_class.userprofiles.all():
            return HttpResponse('Unauthorized', status = 401)
    if 'uspk' in kwargs:
        user_slides = get_object_or_404(UserSlides,pk=kwargs['uspk'])
        student_user = get_object_or_404(User,username=kwargs['username'])
        student_userprofile = student_user.userprofile
        slidegroup = user_slides.published_slides
        context['user_slides'] = user_slides
        if student_user not in userprofile.students.all():
            return HttpResponse('Unauthorized', status = 401)
        if user_slides.userunitobject.user_unit.user_class.userprofile != student_userprofile:
            return HttpResponse('Unauthorized', status = 401)
        pub_class = user_slides.userunitobject.user_unit.user_class.published_class
    slides = slidegroup.slides.all()
    paginator = Paginator(slides,1)
    page = request.GET.get('page')
    try:
        rows = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        rows = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        rows = paginator.page(paginator.num_pages)
    context['slides'] = slidegroup
    context['rows'] = rows
    context['class'] = pub_class
    context['nbar'] = 'teacher'
    return render(request,'teacher/publishedclasses/slidesview.html',context)

def teacherproblemsetview(request,**kwargs):
    context={}
    my_class = get_object_or_404(PublishedClass, pk = kwargs['pk'])
    userprofile=request.user.userprofile
    problemset = get_object_or_404(PublishedProblemSet, pk = kwargs['pspk'])##
    if my_class not in userprofile.my_published_classes.all():
        raise Http404("Unauthorized.")
    if problemset.unit_object.unit not in my_class.publishedunit_set.all():
        raise Http404("Unauthorized.")
    rows = problemset.problem_objects.all()
    expanded_rows = []
    for po in rows:
        resps = po.response_set.all()
        atts = resps.filter(attempted=1)
        grds = atts.filter(is_graded=1)
        expanded_rows.append((po,atts.count(),grds.count()))
    context['rows'] = expanded_rows
    po_rows = []
    for i in range(0,int((rows.count()+14)/15)):
        po_rows.append((rows[15*i:15*(i+1)],15*i))
    context['po_rows'] = po_rows
    context['problemset'] = problemset
    context['nbar'] = 'teacher'
    context['class'] = my_class
    return render(request, 'teacher/publishedclasses/teacherproblemsetview.html',context)

def teachertestview(request,**kwargs):
    context={}
    my_class = get_object_or_404(PublishedClass, pk = kwargs['pk'])
    userprofile=request.user.userprofile
    test = get_object_or_404(PublishedTest, pk = kwargs['tpk'])
    if my_class not in userprofile.my_published_classes.all():
        raise Http404("Unauthorized.")
    if test.unit_object.unit not in my_class.publishedunit_set.all():
        raise Http404("Unauthorized.")
    rows = test.problem_objects.all()
    context['rows'] = rows
#    expanded_rows = []
#    for po in rows:
#        resps = po.response_set.all()
#        atts = resps.filter(attempted=1)
#        grds = atts.filter(is_graded=1)
#        expanded_rows.append((po,atts.count(),grds.count()))
#    context['rows'] = expanded_rows
    po_rows = []
    for i in range(0,int((rows.count()+14)/15)):
        po_rows.append((rows[15*i:15*(i+1)],15*i))
    context['po_rows'] = po_rows
    context['test'] = test
    context['nbar'] = 'teacher'
    context['class'] = my_class
    return render(request, 'teacher/publishedclasses/teachertestview.html',context)

@login_required
def getstudentlist(request,pk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(PublishedClass,pk=pk)
    if userprofile.my_published_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    students = userprofile.students.exclude(pk__in=my_class.enrolled_students.all())
    return JsonResponse({'students':render_to_string('teacher/publishedclasses/roster/roster-studentselect.html',{'students':students})})

@login_required
def addstudenttoclass(request,pk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(PublishedClass,pk=pk)
    if userprofile.my_published_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    if request.method == "POST":
        form = request.POST
        student = get_object_or_404(User,pk=form.get("student_id",""))
#        my_class.enrolled_students.add(student)
#        my_class.save()
#        user_class = UserClass(published_class = my_class,userprofile=student.userprofile,total_points=my_class.total_points,points_earned=0,num_problems = my_class.num_problems)
#        user_class.save()
#        for unit in my_class.publishedunit_set.all():
#            user_unit = UserUnit(published_unit = unit,user_class = user_class,total_points=unit.total_points, points_earned=0,order = unit.order,num_problems = unit.num_problems)
#            user_unit.save()
#            num_psets = 0
#            for unit_object in unit.unit_objects.all():
#                user_unitobject = UserUnitObject(order = unit_object.order, user_unit = user_unit)
#                user_unitobject.save()
#                try:
#                    pset = unit_object.publishedproblemset
#                    user_problemset = UserProblemSet(published_problemset=unit_object.publishedproblemset,total_points=unit_object.publishedproblemset.total_points,points_earned=0,order=unit_object.order,num_problems = unit_object.publishedproblemset.num_problems,userunitobject = user_unitobject)
#                    user_problemset.save()
#                    num_psets +=1
#                except:
#                    user_slides = UserSlides(published_slides=unit_object.publishedslidegroup,order=unit_object.order,userunitobject = user_unitobject,num_slides = unit_object.publishedslidegroup.slides.count())
#                    user_slides.save()
#            user_unit.num_problemsets = num_psets
#            user_unit.save()
        return JsonResponse({'student':render_to_string('teacher/publishedclasses/roster/roster-studentrow.html',{'student_class':my_class.add_student(student)})})

##############################
##Class Editing Views
##############################
@login_required
def classeditview(request,pk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none':
        raise Http404("Unauthorized.")
    if request.method == "POST":
        form = request.POST
        if 'save' in form:
            U = list(my_class.unit_set.all())
            U = sorted(U,key=lambda x:x.order)
            unit_inputs = form.getlist('unitinput')
            for u in U:
                deleted = 0
                if 'unit_'+str(u.pk) not in unit_inputs:
                    u.delete()
                    deleted = 1                
            for i in range(0,len(unit_inputs)):
                u = my_class.unit_set.get(pk=unit_inputs[i].split('_')[1])
                u.order = i+1
                u.save()
                u.increment_version()
                deleted = 0
            if deleted == 1:
                my_class.increment_version()
            return JsonResponse({'unit-list' : render_to_string('teacher/editingtemplates/unit-list.html',{'my_class':my_class})})
    context={}
    context['my_class'] = my_class
    context['sharing_type'] = sharing_type
    context['nbar'] = 'teacher'
    return render(request, 'teacher/editingtemplates/editclassview.html',context)


@login_required
def newunitview(request,pk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    if request.method == "POST":
        form=request.POST
        u=Unit(name=form.get("unit-name",""),order=my_class.unit_set.count()+1,the_class=my_class)
        u.save()
        my_class.increment_version()
        return HttpResponse(render_to_string('teacher/editingtemplates/unitsnippet.html',{'unit':u,'forcount':my_class.unit_set.count()}))
    return HttpResponse('')

@login_required
def editclassname(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    my_class = get_object_or_404(Class,pk=pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    form = EditClassNameForm(instance = my_class)
    return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/modals/modal-edit-class-name.html',{'form':form})})

@login_required
def saveclassname(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    my_class = get_object_or_404(Class,pk=pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    form = EditClassNameForm(request.POST,instance = my_class)
    form.save()
    my_class.increment_version()
    return JsonResponse({'class-name':form.instance.name})

@login_required
def uniteditview(request,pk,upk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")

    if request.method == "POST":
        form = request.POST
        if 'save' in form:
            unit_objs = list(unit.unit_objects.all())
            unit_objs = sorted(unit_objs,key = lambda x:x.order)###
            unit_obj_inputs = form.getlist('unitobjectinput')
            deleted = 0
            for u in unit_objs:
                if 'unitobject_'+str(u.pk) not in unit_obj_inputs:
                    u.delete()
                    deleted = 1
            for i in range(0,len(unit_obj_inputs)):
                u = unit.unit_objects.get(pk = unit_obj_inputs[i].split('_')[1])
                u.order = i+1
                u.save()
                u.increment_version()
                deleted = 0
            if deleted == 1:
                unit.increment_version()
            return JsonResponse({'unit-object-list' : render_to_string('teacher/editingtemplates/unitobjectlist.html',{'unit':unit})})
    context = {}
    context['my_class'] = my_class
    context['unit'] = unit
    context['nbar'] = 'teacher'
    context['minuterange'] = [5*i for i in range(0,12)]
    context['default_hours'] = 1
    context['sharing_type'] = sharing_type
    return render(request, 'teacher/editingtemplates/editunitview.html',context)

@login_required
def editunitname(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    unit = get_object_or_404(Unit,pk=pk)
    my_class = unit.the_class
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    form = EditUnitNameForm(instance = unit)
    return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/modals/modal-edit-unit-name.html',{'form':form})})

@login_required
def saveunitname(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    unit = get_object_or_404(Unit,pk=pk)
    my_class = unit.the_class
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    form = EditUnitNameForm(request.POST,instance = unit)
    form.save()
    unit.increment_version()
    return JsonResponse({'unit-name':form.instance.name})

@login_required
def newproblemsetview(request,pk,upk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.unit_set.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    if request.method == "POST":
        form = request.POST
        u = UnitObject(unit=unit,order=unit.unit_objects.count()+1)
        u.save()
        p = ProblemSet(name = form.get("problemset-name",""),default_point_value = form.get("problemset-default_point_value",""),unit_object = u)
        p.save()
        unit.increment_version()
        return HttpResponse(render_to_string('teacher/editingtemplates/unitobjectsnippet.html',{'unitobj':u,'forcount':unit.unit_objects.count()},request=request))
    return HttpResponse('')

@login_required
def newtestview(request,pk,upk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    if request.method == "POST":
        form = request.POST
        u = UnitObject(unit = unit,order = unit.unit_objects.count() + 1)
        u.save()
        minutes = request.POST.get('minutes')
        hours = request.POST.get('hours')
        time_limit = time(hour = int(hours),minute = int(minutes))
        t = Test(name = form.get("test-name",""),default_point_value = form.get("test-default_point_value",""),default_blank_value = form.get("test-default_blank_value",""),unit_object = u,time_limit = time_limit)
        t.save()
        unit.increment_version()
        return HttpResponse(render_to_string('teacher/editingtemplates/unitobjectsnippet.html',{'unitobj':u,'forcount':unit.unit_objects.count()},request=request))
    return HttpResponse('')

@login_required
def newslidesview(request,pk,upk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    if request.method == "POST":
        form = request.POST
        u = UnitObject(unit = unit,order = unit.unit_objects.count() + 1)
        u.save()
        s = SlideGroup(name = form.get("slides-name",""),unit_object = u)
        s.save()
        unit.increment_version()
        return HttpResponse(render_to_string('teacher/editingtemplates/unitobjectsnippet.html',{'unitobj':u,'forcount':unit.unit_objects.count()}))
    return HttpResponse('')

@login_required
def latexpsetview(request,pk,upk,ppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    pset = get_object_or_404(ProblemSet,pk=ppk)
    if pset.unit_object.unit != unit:
        raise Http404("No such problem set in this unit")
    include_problem_labels = True
    if request.method == "GET":
        if request.GET.get('problemlabels') == 'no':
            include_problem_labels = False
    context = {}
    context['include_problem_labels'] = include_problem_labels

    context['my_class'] = my_class
    context['unit'] = unit
    context['nbar'] = 'teacher'
    context['pset'] = pset
    return render(request, 'teacher/editingtemplates/latexpsetview.html',context)

@login_required
def newlatexpsetview(request,pk,upk,ppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    pset = get_object_or_404(ProblemSet,pk=ppk)
    if pset.unit_object.unit != unit:
        raise Http404("No such problem set in this unit")
    form = request.GET
    context = {}
    include_problem_labels = 0
    if 'include-acs' in form:
        include_answer_choices = True
    else:
        include_answer_choices = False
    if 'include-pls' in form:
        include_problem_labels = int(form['include-pls'])
    if 'include-sols' in form:
        include_sols = True
    else:
        include_sols = False
    context = {
        'pset' : pset,
        'problem_labels' : include_problem_labels,
        'include_answer_choices':include_answer_choices,
        'include_sols' : include_sols,
        }
    context['my_class'] = my_class
    context['unit'] = unit
    context['nbar'] = 'teacher'
    context['pset'] = pset
    filename = pset.name.replace(' ','') + '.tex'
    response = HttpResponse(render_to_string('teacher/editingtemplates/newlatexpsetview.html',context), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response


@login_required
def latexpsetanswerkeyview(request,pk,upk,ppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    pset = get_object_or_404(ProblemSet,pk=ppk)
    if pset.unit_object.unit != unit:
        raise Http404("No such problem set in this unit")
    context = {}

    context['my_class'] = my_class
    context['unit'] = unit
    context['nbar'] = 'teacher'
    context['pset'] = pset
    filename = pset.name.replace(' ','') + 'AnswerKey.tex'
    response = HttpResponse(render_to_string('teacher/editingtemplates/newlatexpsetanswerkeyview.html',context), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response

@login_required
def latexslidesview(request,pk,upk,ppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    slidegroup = get_object_or_404(SlideGroup,pk=ppk)
    if unit.unit_objects.filter(slidegroup__isnull=False).filter(slidegroup__pk=slidegroup.pk).exists()==False:
        raise Http404("No such problem set in this unit")
    context = {}

    context['my_class'] = my_class
    context['unit'] = unit
    context['slides'] = slidegroup
    filename = slidegroup.name+".tex"
    response = HttpResponse(render_to_string('teacher/editingtemplates/latexslidesview.tex',context), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response

@login_required
def latexclassview(request,pk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    dc = request.GET.get('dc')
    if sharing_type == 'none':
        raise Http404("Unauthorized.")
    form = request.GET
    include_sols = False
    include_problem_labels = False
    if 'include-sols' in form:
        include_sols = True
    if 'include-pls' in form:
        include_problem_labels = True

    context = {}
    context['my_class'] = my_class
    context['dc'] = dc
    context['include_sols'] = include_sols
    context['include_problem_labels'] = include_problem_labels
    filename = my_class.name+".tex"
    response = HttpResponse(render_to_string('teacher/editingtemplates/latexclassview.tex',context), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response


@login_required
def class_as_pdf(request,pk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    dc = request.GET.get('dc')
    if dc == None:
        dc = 'article'
    if sharing_type == 'none':
        raise Http404("Unauthorized.")
    filename = my_class.name+".pdf"


    form = request.GET
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
    context = {
        'my_class' : my_class,
        'dc' : dc,
        'include_problem_labels' : include_problem_labels,
        'include_answer_choices' : include_answer_choices,
        'include_tags' : include_tags,
        'include_sols' : include_sols,
        'include_ans' : include_ans,
        }
    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('teacher/editingtemplates/latexclassview.tex')
    rendered_tpl = template.render(context).encode('utf-8')
    with tempfile.TemporaryDirectory() as tempdir:
        fa = open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        context = {
            'my_class' : my_class,
            'dc' : dc,
            'include_problem_labels' : include_problem_labels,
            'include_answer_choices':include_answer_choices,
            'include_tags' : include_tags,
            'include_sols' : include_sols,
            'include_ans' : include_ans,
            'tempdirect' : tempdir,
            }
        template = get_template('teacher/editingtemplates/latexclassview.tex')
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
                r['Content-Disposition'] = 'attachment;filename="'+my_class.name.replace(' ','')+'.pdf"'
                return r
        else:
            with open(os.path.join(tempdir, 'texput.log')) as f:
                error_text = f.read()
                error_lines = error_text.split('\n')
                error_inds = []
                for i in range(0,len(error_lines)):
                    if len(error_lines[i]) > 0 and error_lines[i][0] == '!':
                        error_inds.append(i)
                errors_only = ''
                for i in range(0,len(error_inds)):
                    errors_only += error_lines[error_inds[i]]+'\n'
                    errors_only += error_lines[error_inds[i]+1]+'\n'
#                    errors_only += error_lines[error_inds[i]+2]+'\n'
                return render(request,'randomtest/latex_errors.html',{'nbar':'teacher','name':my_class.name,'error_text':'Attempt to Parse Errors Only:\n'+errors_only+'\n\n\nFull Log\n'+error_text})#####Perhaps the error page needs to be customized...              



@login_required
def problemseteditview(request,pk,upk,ppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk = ppk)
    if unit.unit_objects.filter(problemset__isnull=False).filter(problemset__pk = problemset.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
    if request.method == "POST":
        form = request.POST
        if 'save' in form:
            prob_objs = list(problemset.problem_objects.all())
            prob_objs = sorted(prob_objs,key = lambda x:x.order)###
            prob_obj_inputs = form.getlist('problemobjectinput')#could be an issue if no units
            deleted = 0
            for p in prob_objs:
                if 'problemobject_' + str(p.pk) not in prob_obj_inputs:
                    p.delete()
                    deleted = 1
            for i in range(0,len(prob_obj_inputs)):
                p = problemset.problem_objects.get(pk = prob_obj_inputs[i].split('_')[1])
                p.order = i+1
                p.save()
                p.increment_version()
                deleted = 0
            if deleted == 1:
                problemset.increment_version()
            return JsonResponse({'problemobject-list':render_to_string('teacher/editingtemplates/problemobjectlist.html',{'problemset':problemset})})
    co_owned_pgs =  userprofile.owned_problem_groups.all()
    editor_pgs =  userprofile.editable_problem_groups.all()
    readonly_pgs =  userprofile.readonly_problem_groups.all()
    owned_pgs = userprofile.problem_groups.all()
    probgroups = list(chain(owned_pgs,co_owned_pgs,editor_pgs,readonly_pgs))

    problemset_list = []
    for uo in unit.unit_objects.exclude(pk = problemset.unit_object.pk):
        try:
            ps = uo.problemset
            problemset_list.append(('p','Problem Set: '+ps.name,ps.pk))
        except ProblemSet.DoesNotExist:
            try:
                ts = uo.test
                problemset_list.append(('t','Test: '+ts.name,ts.pk))
            except Test.DoesNotExist:
                pass
    context = {}
    context['probgroups'] = probgroups
    context['my_class'] = my_class
    context['unit'] = unit
    context['problemset'] = problemset
    context['tags'] = NewTag.objects.exclude(tag='root')
    context['nbar'] = 'teacher'
    context['sharing_type'] = sharing_type
    context['problemset_list'] = problemset_list
    return render(request, 'teacher/editingtemplates/editproblemsetview.html',context)

@login_required
def move_problem(request):
    problem_pk = request.POST.get('po_pk')
    ps_pk = request.POST.get('ps_pk')
    #psets = [(d,p) for d, p in request.POST.items() if d.startswith('move-prob')]
    #problem_pk = i[0].split('_')[1]
    probobj = get_object_or_404(ProblemObject,pk=problem_pk)
    marker,pset = probobj.get_pset()
    pset_type = ps_pk.split('_')[0]
    pset_pk = ps_pk.split('_')[1]
    if pset_type =='p':
        pset_target = get_object_or_404(ProblemSet,pk = pset_pk)
        if probobj.isProblem:
            curr_problems = pset_target.problem_objects.filter(isProblem = 1)
            vals = curr_problems.values('problem_id')
            if probobj.problem.pk in [i['problem_id'] for i in vals]:
                return JsonResponse({'prob_pk':problem_pk,'status':0})#problem is already in problem set.
        pset.increment_version()
        probobj.problemset = pset_target
        probobj.order = pset_target.problem_objects.count()+1
        probobj.problemset.increment_version()
        if marker == 't':
            probobj.test = None
        probobj.save()
        prob_objs = list(pset.problem_objects.all())
        prob_objs = sorted(prob_objs,key = lambda x:x.order)
        for i in range(0,len(prob_objs)):
            p = prob_objs[i]
            p.order = i+1
            p.save()
        probobj.problemset.increment_version()
    elif pset_type == 't':
        pset_target = get_object_or_404(Test,pk = pset_pk)
        if probobj.isProblem:
            curr_problems = pset_target.problem_objects.filter(isProblem = 1)
            vals = curr_problems.values('problem_id')
            if probobj.problem.pk in [i['problem_id'] for i in vals]:
                return JsonResponse({'prob_pk':problem_pk,'status':0})#problem is already in problem set.
        pset.increment_version()
        probobj.test = pset_target
        probobj.order = pset_target.problem_objects.count()+1
        if marker == 'p':
            probobj.problemset = None
        probobj.save()
        prob_objs = list(pset.problem_objects.all())
        prob_objs = sorted(prob_objs,key = lambda x:x.order)
        for i in range(0,len(prob_objs)):
            p = prob_objs[i]
            p.order = i+1
            p.save()
        probobj.test.increment_version()
    else:
        return JsonResponse({'prob_pk':problem_pk,'status':2})#Rare...no problemset/test target exists
#                return JsonResponse({'prob_pk':problem_pk,'status':1,'tag_count':prob.newtags.count()})
    return JsonResponse({'prob_pk':problem_pk,'status':1})



@login_required
def copy_problem(request):###fill out
    problem_pk = request.POST.get('po_pk')
    ps_pk = request.POST.get('ps_pk')
    #psets = [(d,p) for d, p in request.POST.items() if d.startswith('move-prob')]
    #problem_pk = i[0].split('_')[1]
    probobj = get_object_or_404(ProblemObject,pk=problem_pk)
    marker,pset = probobj.get_pset()
    pset_type = ps_pk.split('_')[0]
    pset_pk = ps_pk.split('_')[1]
    if pset_type =='p':
        pset_target = get_object_or_404(ProblemSet,pk = pset_pk)
        if probobj.isProblem:
            curr_problems = pset_target.problem_objects.filter(isProblem = 1)
            vals = curr_problems.values('problem_id')
            if probobj.problem.pk in [i['problem_id'] for i in vals]:
                return JsonResponse({'prob_pk':problem_pk,'status':0})#problem is already in problem set.
        pset.increment_version()
        po = ProblemObject(problemset = pset_target,
                           order = pset_target.problem_objects.count()+1,
                           point_value = probobj.point_value,
                           blank_point_value = probobj.blank_point_value,
                           problem_code = probobj.problem_code,
                           problem_display = probobj.problem_display,
                           isProblem = probobj.isProblem,
                           problem = probobj.problem,
                           question_type = probobj.question_type,
                           mc_answer = probobj.mc_answer,
                           sa_answer = probobj.sa_answer,
                           answer_A = probobj.answer_A,
                           answer_B = probobj.answer_B,
                           answer_C = probobj.answer_C,
                           answer_D = probobj.answer_D,
                           answer_E = probobj.answer_E,
                           author = probobj.author,
                           created_date = probobj.created_date,
                           version_number = probobj.version_number)
        po.save()
        po.increment_version()
    elif pset_type == 't':
        pset_target = get_object_or_404(Test,pk = pset_pk)
        if probobj.isProblem:
            curr_problems = pset_target.problem_objects.filter(isProblem = 1)
            vals = curr_problems.values('problem_id')
            if probobj.problem.pk in [i['problem_id'] for i in vals]:
                return JsonResponse({'prob_pk':problem_pk,'status':0})#problem is already in problem set.
        pset.increment_version()
        po = ProblemObject(problemset = pset_target,
                           order = pset_target.problem_objects.count()+1,
                           point_value = probobj.point_value,
                           blank_point_value = probobj.blank_point_value,
                           problem_code = probobj.problem_code,
                           problem_display = probobj.problem_display,
                           isProblem = probobj.isProblem,
                           problem = probobj.problem,
                           question_type = probobj.question_type,
                           mc_answer = probobj.mc_answer,
                           sa_answer = probobj.sa_answer,
                           answer_A = probobj.answer_A,
                           answer_B = probobj.answer_B,
                           answer_C = probobj.answer_C,
                           answer_D = probobj.answer_D,
                           answer_E = probobj.answer_E,
                           author = probobj.author,
                           created_date = probobj.created_date,
                           version_number = probobj.version_number)
        po.save()
        po.increment_version()        
    else:
        return JsonResponse({'prob_pk':problem_pk,'status':2})#Rare...no problemset/test target exists
#                return JsonResponse({'prob_pk':problem_pk,'status':1,'tag_count':prob.newtags.count()})
    return JsonResponse({'prob_pk':problem_pk,'status':1})


@login_required
def editproblemsetname(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    problemset = get_object_or_404(ProblemSet,pk=pk)
    my_class = problemset.unit_object.unit.the_class
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none':
        raise Http404("Unauthorized.")
    form = EditProblemSetNameForm(instance = problemset)
    return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/modals/modal-edit-problemset-name.html',{'form':form})})

@login_required
def saveproblemsetname(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    problemset = get_object_or_404(ProblemSet,pk=pk)
    my_class = problemset.unit_object.unit.the_class
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    form = EditProblemSetNameForm(request.POST,instance = problemset)
    form.save()
    problemset.increment_version()
    return JsonResponse({'problemset-name':form.instance.name})

@login_required
def loadoriginalproblemform(request,**kwargs):
    qt = request.GET.get('qt','')
    po = ProblemObject()
    if qt == 'sa':
        form = NewProblemObjectSAForm(instance=po)
    if qt == 'mc':
        form = NewProblemObjectMCForm(instance=po)
    if qt == 'pf':
        form = NewProblemObjectPFForm(instance=po)
    return HttpResponse(render_to_string('teacher/editingtemplates/modals/originalproblemform.html',{'form':form}))

@login_required
def loadcqtoriginalproblemform(request,**kwargs):
    qt = request.GET.get('qt','')
    pk = request.GET.get('pk','')
    po = get_object_or_404(ProblemObject,pk=pk)
    qt_dict = {'mc' : 'multiple choice', 'sa' : 'short answer', 'pf' : 'proof'}
    answers = ''
    if po.isProblem==0:
        if qt == 'sa':
            form = NewProblemObjectSAForm(instance=po)
        if qt == 'mc':
            form = NewProblemObjectMCForm(instance=po)
            answers = po.answers()
        if qt == 'pf':
            form = NewProblemObjectPFForm(instance=po)

        return JsonResponse({'answer_code' : render_to_string('teacher/editingtemplates/edit-slide/modals/exampleproblem-answers.html', {'ep' : po, 'ep_qt' : qt_dict[qt]}), 'latex_display' : render_to_string('teacher/editingtemplates/edit-slide/modals/exampleproblem-latex.html', {'problem_display' : newtexcode(po.problem_code,'originalproblem_'+str(po.pk),answers)})})


@login_required
def loadoriginalexampleproblemform(request,**kwargs):
    qt = request.GET.get('qt','')
    ep = ExampleProblem()
    if qt == 'sa':
        form = NewExampleProblemSAForm(instance=ep)
    if qt == 'mc':
        form = NewExampleProblemMCForm(instance=ep)
    if qt == 'pf':
        form = NewExampleProblemPFForm(instance=ep)
    return JsonResponse({'latex-input' : render_to_string('teacher/editingtemplates/modals/originalproblemform.html',{'form':form})})

@login_required
def loadcqtexampleproblemform(request,**kwargs):
    qt = request.POST.get('qt','')
    pk = request.POST.get('pk','')
    ep = get_object_or_404(ExampleProblem,pk = pk)
    qt_dict = {'mc' : 'multiple choice', 'sa' : 'short answer', 'pf' : 'proof'}
    answers = ''
    if qt == 'mc':
        answers = ep.answers()
    return JsonResponse({'answer_code' : render_to_string('teacher/editingtemplates/edit-slide/modals/exampleproblem-answers.html', {'ep' : ep, 'ep_qt' : qt_dict[qt]}), 'latex_display' : render_to_string('teacher/editingtemplates/edit-slide/modals/exampleproblem-latex.html', {'problem_display' : newtexcode(ep.problem_code,'exampleproblem_'+str(ep.pk),answers)})})

@login_required
def addoriginalproblem(request,pk,upk,ppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk = ppk)
    if unit.unit_objects.filter(problemset__isnull = False).filter(problemset__pk = problemset.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
    if request.method == "POST":
        form = request.POST
        qt = form.get('question-type','')
        po = ProblemObject()
        problemset_list = []
        for uo in unit.unit_objects.exclude(pk = problemset.unit_object.pk):
            try:
                ps = uo.problemset
                problemset_list.append(('p','Problem Set: '+ps.name,ps.pk))
            except ProblemSet.DoesNotExist:
                try:
                    ts = uo.test
                    problemset_list.append(('t','Test: '+ts.name,ts.pk))
                except Test.DoesNotExist:
                    pass
        if qt == "multiple choice":
            pform = NewProblemObjectMCForm(request.POST, instance=po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),prob.answers())
                compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                compiletikz(prob.problem_code,'originalproblem_'+str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type=qt)
                prob.author = request.user
                prob.point_value = problemset.default_point_value
                prob.order = problemset.problem_objects.count()+1
                prob.problemset = problemset
                prob.save()
                problemset.increment_version()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':problemset.problem_objects.count(),'problemset_list':problemset_list}),'pk':prob.pk})
        elif qt == "short answer":
            pform = NewProblemObjectSAForm(request.POST, instance=po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                compiletikz(prob.problem_code,'originalproblem_'+str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type=qt)
                prob.author = request.user
                prob.point_value = problemset.default_point_value
                prob.order = problemset.problem_objects.count()+1
                prob.problemset = problemset
                prob.save()
                problemset.increment_version()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':problemset.problem_objects.count(),'problemset_list':problemset_list}),'pk':prob.pk})
        elif qt == "proof":
            pform = NewProblemObjectPFForm(request.POST, instance=po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                compiletikz(prob.problem_code,'originalproblem_'+str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type=qt)
                prob.author = request.user
                prob.point_value = problemset.default_point_value
                prob.order = problemset.problem_objects.count()+1
                prob.problemset = problemset
                prob.save()
                problemset.increment_version()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':problemset.problem_objects.count(),'problemset_list':problemset_list}),'pk':prob.pk})
    return JsonResponse({'problem_text':'','pk':'0'})

@login_required
def update_point_value(request,pk,upk,ppk,pppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk = ppk)
    if unit.unit_objects.filter(problemset__isnull = False).filter(problemset__pk = problemset.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
    po = get_object_or_404(ProblemObject,pk=pppk)
    if request.method == 'POST':
        form = PointValueForm(request.POST,instance=po)
        if form.is_valid():
            form.save()
            data = {
                'pk': pppk,
                'point_value':form.instance.point_value,
            }
            po.increment_version()
            return JsonResponse(data)
    form = PointValueForm(instance = po)
    return render(request,'teacher/editingtemplates/editpointvalueform.html',{'form':form,'pk':pk,'upk':upk,'ppk':ppk,'pppk':pppk})

@login_required
def loadeditquestiontype(request,**kwargs):
    userprofile = request.user.userprofile
#copied from slides....
    if request.method == "GET":
        form = request.GET
    elif request.method == "POST":
        form = request.POST
    po = get_object_or_404(ProblemObject,pk=form.get('popk'))
    if po.test != None:
        my_class = po.test.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    elif po.problemset!=None:
        my_class = po.problemset.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    else:
        raise Http404("Error: Problem does not belong to a valid class.")

    qt_dict = {'mc' : 'multiple choice', 'sa' : 'short answer', 'pf' : 'proof'}
    if request.method == "POST":
        qt = form.get('cqt-question-type','')
        if po.isProblem == 0:
            if qt == "mc":
                pform = NewProblemObjectMCForm(request.POST, instance = po)
                if pform.is_valid():
                    prob = pform.save()
                    prob.problem_display = newtexcode(prob.problem_code,'originalproblem_' + str(prob.pk),prob.answers())
                    compileasy(prob.problem_code,'originalproblem_' + str(prob.pk))
                    compiletikz(prob.problem_code,'originalproblem_' + str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type = qt_dict[qt])
                    prob.author = request.user
                    prob.save()
                    po.increment_version()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':prob}),'qt':qt_dict[qt]})
            elif qt == "sa":
                pform = NewProblemObjectSAForm(request.POST, instance = po)
                if pform.is_valid():
                    prob = pform.save()
                    prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                    compiletikz(prob.problem_code,'originalproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type = qt_dict[qt])
                    prob.save()
                    po.increment_version()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':prob}),'qt':qt_dict[qt]})
            elif qt == "pf":
                pform = NewProblemObjectPFForm(request.POST, instance = po)
                if pform.is_valid():
                    prob = pform.save()
                    prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                    compiletikz(prob.problem_code,'originalproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type = qt_dict[qt])
                    prob.save()
                    po.increment_version()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':prob}),'qt':qt_dict[qt]})
        else:
            po.question_type = QuestionType.objects.get(question_type = qt_dict[qt])
            po.save()
            po.increment_version()
            return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':po}),'qt':qt_dict[qt]})

    if po.isProblem == 0:
        return JsonResponse({'modal-html' : render_to_string('teacher/editingtemplates/edit-slide/modals/modal-edit-exampleproblem.html', {'ep' : po})})
    else:
        pqt =  po.problem.question_type_new.question_type
        qt =  po.question_type.question_type
        if pqt == 'multiple choice':
            qts=[1,0,1]
            qts=['mc','pf']
        if pqt == 'short answer':
            qts=[0,1,1]
            qts=['sa','pf']
        if pqt == 'multiple choice short answer':
            qts=[1,1,1]
            qts=['mc','sa','pf']
        if pqt == 'proof':
            qts=[0,0,1]
            qts=['pf']
        if qt == 'multiple choice':
            answers = po.answers()
            problem_display = newtexcode(po.problem.mc_problem_text,str(po.problem.label),answers)
        else:
            problem_display = po.problem.display_problem_text
        return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/edit-slide/modals/modal-edit-exampleproblem.html',{'ep':po,'qts':qts}), 'latex_display' : render_to_string('teacher/editingtemplates/edit-slide/modals/exampleproblem-latex.html', {'problem_display' : problem_display})})

@login_required
def load_new_solution_form(request,**kwargs):
    userprofile = request.user.userprofile
    po = get_object_or_404(ProblemObject,pk=request.POST.get('popk'))

    if po.test != None:
        my_class = po.test.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    elif po.problemset!=None:
        my_class = po.problemset.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    else:
        raise Http404("Error: Problem does not belong to a valid class.")
    
#    if po.test != None:
#        if po.test.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    elif po.problemset != None:
#        if po.problemset.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    else:
#        raise Http404("Problem does not belong to a valid class.")
    so = SolutionObject()
    form = NewSolutionObjectForm(instance = so)
    if po.isProblem:
        name = po.problem.readable_label
    else:
        name = "Problem "+str(po.pk)
    return JsonResponse({'form':render_to_string('teacher/editingtemplates/modals/originalproblemform.html',{'form':form}),'name':name,'popk':po.pk,'ptext':render_to_string('teacher/editingtemplates/modals/po-problem-text.html',{'po':po})})

@login_required
def save_new_solution(request,**kwargs):
    userprofile = request.user.userprofile
    po = get_object_or_404(ProblemObject,pk=request.POST.get('popk'))

    if po.test != None:
        my_class = po.test.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    elif po.problemset!=None:
        my_class = po.problemset.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    else:
        raise Http404("Error: Problem does not belong to a valid class.")

#    if po.test != None:
#        if po.test.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    elif po.problemset != None:
#        if po.problemset.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    else:
#        raise Http404("Problem does not belong to a valid class.")
    so = SolutionObject(problem_object = po, order = po.solution_objects.count()+1, solution_code = request.POST.get('solution_code'),author = request.user)#, version_number = 
    so.save()
    so.solution_display = newsoltexcode(so.solution_code, 'originalsolution_'+str(so.pk))
    so.save()
    po.increment_version()
    compileasy(so.solution_code,'originalsolution_'+str(so.pk))
    compiletikz(so.solution_code,'originalsolution_'+str(so.pk))
    return JsonResponse({});

@login_required
def load_manage_solutions(request,**kwargs):
    userprofile = request.user.userprofile
    po = get_object_or_404(ProblemObject,pk=request.POST.get('popk'))
    if po.test != None:
        my_class = po.test.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    elif po.problemset!=None:
        my_class = po.problemset.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    else:
        raise Http404("Error: Problem does not belong to a valid class.")

    
#    if po.test != None:
#        if po.test.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    elif po.problemset != None:
#        if po.problemset.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    else:
#        raise Http404("Problem does not belong to a valid class.")
    other_solutions = []
    if po.isProblem:
        S=[]
        for so in po.solution_objects.all():
            if so.isSolution:
                S.append(so.solution.pk)
        other_solutions = po.problem.solutions.exclude(id__in= S)

    return JsonResponse({'form': render_to_string('teacher/editingtemplates/modals/modal-manage-solutions.html',{'po':po, 'other_solutions': other_solutions})})

@login_required
def display_solution(request,**kwargs):
    userprofile = request.user.userprofile
    po = get_object_or_404(ProblemObject,pk=request.POST.get('popk'))
    if po.test != None:
        my_class = po.test.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    elif po.problemset!=None:
        my_class = po.problemset.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    else:
        raise Http404("Error: Problem does not belong to a valid class.")

#    if po.test != None:
#        if po.test.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    elif po.problemset != None:
#        if po.problemset.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    else:
#        raise Http404("Problem does not belong to a valid class.")
    sol = get_object_or_404(Solution,pk=request.POST.get('spk'))
    so = SolutionObject(problem_object = po, order = po.solution_objects.count()+1, solution = sol,author = request.user,isSolution = 1)
    so.save()
    po.increment_version()
    return JsonResponse({'sol': render_to_string('teacher/editingtemplates/modals/displayed-solution.html',{'sol':so})})

@login_required
def undisplay_solution(request,**kwargs):
    userprofile = request.user.userprofile
    so = get_object_or_404(SolutionObject,pk=request.POST.get('sopk'))
    po = so.problem_object
    if po.test != None:
        my_class = po.test.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    elif po.problemset!=None:
        my_class = po.problemset.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    else:
        raise Http404("Error: Problem does not belong to a valid class.")
#   if po.test != None:
#        if po.test.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    elif po.problemset != None:
#        if po.problemset.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    else:
#        raise Http404("Problem does not belong to a valid class.")
    s = so.solution
    po = so.problem_object
    so.delete()
    po.increment_version()
    return JsonResponse({'sol': render_to_string('teacher/editingtemplates/modals/other-solution.html',{'sol':s,'po': po})})

@login_required
def delete_solution(request,**kwargs):
    userprofile = request.user.userprofile
    so = get_object_or_404(SolutionObject,pk=request.POST.get('sopk'))
    po = so.problem_object
    if po.test != None:
        my_class = po.test.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    elif po.problemset!=None:
        my_class = po.problemset.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    else:
        raise Http404("Error: Problem does not belong to a valid class.")
#   if po.test != None:
#        if po.test.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    elif po.problemset != None:
#        if po.problemset.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    else:
#        raise Http404("Problem does not belong to a valid class.")

    so.delete()
    po.increment_version()
    return JsonResponse({})

@login_required
def load_edit_sol(request,**kwargs):
    userprofile = request.user.userprofile
#    popk = request.POST.get('popk','')
    sopk = request.POST.get('sopk','')
#    po =  get_object_or_404(ProblemObject,pk=popk)
    so =  get_object_or_404(SolutionObject,pk=sopk)
    po = so.problem_object
    if po.test != None:
        my_class = po.test.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    elif po.problemset!=None:
        my_class = po.problemset.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    else:
        raise Http404("Error: Problem does not belong to a valid class.")

#    if po.test != None:
#        if po.test.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    elif po.problemset != None:
#        if po.problemset.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    else:
#        raise Http404("Problem does not belong to a valid class.")

    form = EditSolutionObjectForm(instance=so)
    return JsonResponse({'sol_form':render_to_string('teacher/editingtemplates/modals/edit_sol_form.html',{'form':form})})

@login_required
def save_edited_solution(request,**kwargs):
    userprofile = request.user.userprofile
    sopk = request.POST.get('sopk','')
    so =  get_object_or_404(SolutionObject,pk=sopk)
    po = so.problem_object
    if po.test != None:
        my_class = po.test.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    elif po.problemset!=None:
        my_class = po.problemset.unit_object.unit.the_class
        sharing_type = get_permission_level(request,my_class)
        if sharing_type == 'none' or sharing_type == 'read':
            raise Http404("Unauthorized.")
    else:
        raise Http404("Error: Problem does not belong to a valid class.")

#    if po.test != None:
#        if po.test.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    elif po.problemset != None:
#        if po.problemset.unit_object.unit.the_class not in userprofile.my_classes.all():
#            raise Http404("Unauthorized.")
#    else:
#        raise Http404("Problem does not belong to a valid class.")
    so.solution_code = request.POST.get('solution_text')
    so.save()
    so.increment_version()
    so.solution_display = newsoltexcode(so.solution_code, 'originalsolution_'+str(so.pk))
    so.save()
    compileasy(so.solution_code,'originalsolution_'+str(so.pk))
    compiletikz(so.solution_code,'originalsolution_'+str(so.pk))
    return JsonResponse({'sol_code':render_to_string('teacher/editingtemplates/modals/so-sol-text.html',{'sol':so})})

@login_required
def numprobsmatching(request,pk,upk,ppk):#changing tag to pk
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk = ppk)
    if unit.unit_objects.filter(problemset__isnull = False).filter(problemset__pk = problemset.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
    form = request.GET
    typ = form.get('contest-type','')
    desired_tag = get_object_or_404(NewTag,pk = form.get('contest-tags',''))
    curr_problems = problemset.problem_objects.filter(isProblem = 1)
    P = Problem.objects.filter(type_new__type = typ).filter(newtags__in = NewTag.objects.filter(tag__startswith = desired_tag)).exclude(id__in = curr_problems.values('problem_id')).distinct()####check this once contest problems are in a problem set.
    return JsonResponse({'num':str(P.count())})

@login_required
def reviewmatchingproblems(request,pk,upk,ppk):#changing to GET request
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk = ppk)
    if unit.unit_objects.filter(problemset__isnull = False).filter(problemset__pk = problemset.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
    P = []
    desired_tag = ''
    if request.method == 'GET':
        form = request.GET
        typ = form.get('contest-type','')
        desired_tag = get_object_or_404(NewTag,pk = form.get('contest-tags',''))
        curr_problems = problemset.problem_objects.filter(isProblem = 1)
        P = Problem.objects.filter(type_new__type = typ).filter(newtags__in = NewTag.objects.filter(tag__startswith = desired_tag)).exclude(id__in = curr_problems.values('problem_id')).distinct().order_by("problem_number")
    if request.method == 'POST':
        form = request.POST
        if 'add-selected-problems' in form:
            checked = form.getlist("chk")
            top = problemset.problem_objects.count()
            if len(checked) > 0:
                for i in range(0,len(checked)):
                    p = Problem.objects.get(label = checked[i])
                    po = ProblemObject(order = top + i + 1,point_value = problemset.default_point_value,isProblem = 1,problem = p,question_type = p.question_type_new)
                    po.problemset = problemset
                    po.save()
                problemset.increment_version()
                return redirect('../')
            return redirect('../')
    context = {}
    context['my_class'] = my_class
    context['unit'] = unit
    context['problemset'] = problemset
    context['nbar'] = 'teacher'
    context['rows'] = P
    context['tag'] = desired_tag
    return render(request,'teacher/editingtemplates/add-tagged-problems.html',context)

@login_required
def reviewproblemgroup(request,pk,upk,ppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk = ppk)
    if unit.unit_objects.filter(problemset__isnull = False).filter(problemset__pk = problemset.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
    P = []
    desired_tag = ''
    if request.method == 'POST':
        form = request.POST
        if 'add-selected-problems' in form:
            checked = form.getlist("chk")
            top = problemset.problem_objects.count()
            if len(checked) > 0:
                for i in range(0,len(checked)):
                    p = Problem.objects.get(label = checked[i])
                    po = ProblemObject(order = top + i + 1,point_value = problemset.default_point_value,isProblem = 1,problem = p,question_type = p.question_type_new)
                    po.problemset = problemset
                    po.save()
                problemset.increment_version()
                return redirect('../')
            return redirect('../')
    if request.method == 'GET':
        form = request.GET
        prob_group = get_object_or_404(ProblemGroup,pk = form.get('problem-group',''))
        curr_problems = problemset.problem_objects.filter(isProblem = 1)
        P = prob_group.problem_objects.exclude(problem__pk__in = curr_problems.values('problem_id')).distinct()
#        P = prob_group.problems.exclude(id__in = curr_problems.values('problem_id')).distinct()
    context = {}
    context['my_class'] = my_class
    context['unit'] = unit
    context['problemset'] = problemset
    context['nbar'] = 'teacher'
    context['rows'] = P
    context['prob_group'] = prob_group
    return render(request,'teacher/editingtemplates/review-problem-group.html',context)

@login_required
def pset_as_pdf(request,**kwargs):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = kwargs['pk'])
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = kwargs['upk'])
    if my_class.unit_set.filter(pk = kwargs['upk']).exists == False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk = kwargs['ppk'])
    if unit.unit_objects.filter(problemset__isnull = False).filter(problemset__pk = problemset.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
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
#    prob_group = get_object_or_404(ProblemGroup, pk=kwargs['pk'])

    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('teacher/editingtemplates/my_latex_template.tex')########NEEDS TO BE CUSTOMIZED?
    rendered_tpl = template.render(context).encode('utf-8')
    with tempfile.TemporaryDirectory() as tempdir:
        fa = open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        context = {
            'problemset' : problemset,
            'include_problem_labels' : include_problem_labels,
            'include_answer_choices':include_answer_choices,
            'include_tags' : include_tags,
            'include_sols' : include_sols,
            'include_ans' : include_ans,
            'tempdirect' : tempdir,
            }
        template = get_template('teacher/editingtemplates/my_latex_template.tex')
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
                r['Content-Disposition'] = 'attachment;filename="'+problemset.name.replace(' ','')+'.pdf"'
                return r
        else:
            with open(os.path.join(tempdir, 'texput.log')) as f:
                error_text = f.read()
                return render(request,'randomtest/latex_errors.html',{'nbar':'teacher','name':problemset.name,'error_text':error_text})#####Perhaps the error page needs to be customized... 

@login_required
def pset_as_latex(request,**kwargs):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = kwargs['pk'])
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = kwargs['upk'])
    if my_class.unit_set.filter(pk = kwargs['upk']).exists == False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk = kwargs['ppk'])
    if unit.unit_objects.filter(problemset__isnull = False).filter(problemset__pk = problemset.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
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
    context = {
        'problemset' : problemset,
        'include_problem_labels' : include_problem_labels,
        'include_answer_choices':include_answer_choices,
        'include_sols' : include_sols,
        'include_ans' : include_ans,
        }

    filename = problemset.name+".tex"
    response = HttpResponse(render_to_string('teacher/editingtemplates/my_latex_template.tex',context), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response

@login_required
def pset_sols_as_pdf(request,**kwargs):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = kwargs['pk'])
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = kwargs['upk'])
    if my_class.unit_set.filter(pk = kwargs['upk']).exists == False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk = kwargs['ppk'])
    if unit.unit_objects.filter(problemset__isnull = False).filter(problemset__pk = problemset.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
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
    if 'include-problems' in form:
        include_problems = True
    else:
        include_problems = False
    if 'include-ans' in form:
        include_ans = True
    else:
        include_ans = False
#    prob_group = get_object_or_404(ProblemGroup, pk=kwargs['pk'])

    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('teacher/editingtemplates/my_latex_sol_template.tex')########NEEDS TO BE CUSTOMIZED?
    rendered_tpl = template.render(context).encode('utf-8')
    with tempfile.TemporaryDirectory() as tempdir:
        fa = open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        context = {
            'problemset' : problemset,
            'include_problem_labels' : include_problem_labels,
            'include_answer_choices':include_answer_choices,
            'include_problems' : include_problems,
            'include_ans' : include_ans,
            'tempdirect' : tempdir,
            }
        template = get_template('teacher/editingtemplates/my_latex_sol_template.tex')
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
                r['Content-Disposition'] = 'attachment;filename="'+problemset.name.replace(' ','')+'-sols.pdf"'
                return r
        else:
            with open(os.path.join(tempdir, 'texput.log')) as f:
                error_text = f.read()
                return render(request,'randomtest/latex_errors.html',{'nbar':'teacher','name':problemset.name,'error_text':error_text})#####Perhaps the error page needs to be customized... 



@login_required
def testeditview(request,pk,upk,tpk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    test = get_object_or_404(Test,pk = tpk)
    if unit.unit_objects.filter(test__isnull = False).filter(test__pk = test.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
    if request.method == "POST":
        form = request.POST                    
        if 'save' in form:
            prob_objs = list(test.problem_objects.all())
            prob_objs = sorted(prob_objs,key = lambda x:x.order)###
            prob_obj_inputs = form.getlist('problemobjectinput')#could be an issue if no units
            deleted = 0
            for p in prob_objs:
                if 'problemobject_'+str(p.pk) not in prob_obj_inputs:
                    p.delete()
                    deleted = 1
            for i in range(0,len(prob_obj_inputs)):
                p = test.problem_objects.get(pk = prob_obj_inputs[i].split('_')[1])
                p.order = i+1
                p.save()
                p.increment_version()
                deleted = 0
            if deleted == 1:
                test.increment_version()
            return JsonResponse({'problemobject-list':render_to_string('teacher/editingtemplates/problemobjectlist.html',{'test':test})})
    co_owned_pgs =  userprofile.owned_problem_groups.all()
    editor_pgs =  userprofile.editable_problem_groups.all()
    readonly_pgs =  userprofile.readonly_problem_groups.all()
    owned_pgs = userprofile.problem_groups.all()
    probgroups = list(chain(owned_pgs,co_owned_pgs,editor_pgs,readonly_pgs))
    problemset_list = []
    for uo in unit.unit_objects.exclude(pk = test.unit_object.pk):
        try:
            ps = uo.problemset
            problemset_list.append(('p','Problem Set: '+ps.name,ps.pk))
        except ProblemSet.DoesNotExist:
            try:
                ts = uo.test
                problemset_list.append(('t','Test: '+ts.name,ts.pk))
            except Test.DoesNotExist:
                pass
    context = {}
    context['my_class'] = my_class
    context['unit'] = unit
    context['test'] = test
    context['tags'] = NewTag.objects.exclude(tag='root')
    context['nbar'] = 'teacher'
    context['sharing_type'] = sharing_type
    context['problemset_list'] = problemset_list
    return render(request, 'teacher/editingtemplates/edittestview.html',context)

@login_required
def edittestname(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    test = get_object_or_404(Test,pk=pk)
    my_class = test.unit_object.unit.the_class
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    form = EditTestNameForm(instance = test)
    return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/modals/modal-edit-test-name.html',{'form':form})})

@login_required
def savetestname(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    test = get_object_or_404(Test,pk=pk)
    my_class = test.unit_object.unit.the_class
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    form = EditTestNameForm(request.POST,instance = test)
    form.save()
    test.increment_version()
    return JsonResponse({'test-name':form.instance.name})

@login_required
def testloadoriginalproblemform(request,**kwargs):
    qt = request.GET.get('qt','')
    po = ProblemObject()
    if qt == 'sa':
        form = NewProblemObjectSAForm(instance = po)
    if qt == 'mc':
        form = NewProblemObjectMCForm(instance = po)
    if qt == 'pf':
        form = NewProblemObjectPFForm(instance = po)
    return HttpResponse(render_to_string('teacher/editingtemplates/modals/originalproblemform.html',{'form':form}))


@login_required
def testloadcqtoriginalproblemform(request,**kwargs):
    qt = request.GET.get('qt','')
    pk = request.GET.get('pk','')
    po = get_object_or_404(ProblemObject,pk=pk)
    qt_dict = {'mc' : 'multiple choice', 'sa' : 'short answer', 'pf' : 'proof'}
    answers = ''
    if po.isProblem==0:
        if qt == 'sa':
            form = NewProblemObjectSAForm(instance=po)
        if qt == 'mc':
            form = NewProblemObjectMCForm(instance=po)
            answers = po.answers()
        if qt == 'pf':
            form = NewProblemObjectPFForm(instance=po)
        return JsonResponse({'answer_code' : render_to_string('teacher/editingtemplates/edit-slide/modals/exampleproblem-answers.html', {'ep' : po, 'ep_qt' : qt_dict[qt]}), 'latex_display' : render_to_string('teacher/editingtemplates/edit-slide/modals/exampleproblem-latex.html', {'problem_display' : newtexcode(po.problem_code,'originalproblem_'+str(po.pk),answers)})})


@login_required
def testaddoriginalproblem(request,pk,upk,ppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    test = get_object_or_404(Test,pk = ppk)
    if unit.unit_objects.filter(test__isnull = False).filter(test__pk = test.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
    if request.method == "POST":
        form = request.POST
        qt = form.get('question-type','')
        po = ProblemObject()
        problemset_list = []
        for uo in unit.unit_objects.exclude(pk = test.unit_object.pk):
            try:
                ps = uo.problemset
                problemset_list.append(('p','Problem Set: '+ps.name,ps.pk))
            except ProblemSet.DoesNotExist:
                try:
                    ts = uo.test
                    problemset_list.append(('t','Test: '+ts.name,ts.pk))
                except Test.DoesNotExist:
                    pass
        if qt == "multiple choice":
            pform = NewProblemObjectMCForm(request.POST, instance = po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_' + str(prob.pk),prob.answers())
                compileasy(prob.problem_code,'originalproblem_' + str(prob.pk))
                compiletikz(prob.problem_code,'originalproblem_' + str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type = qt)
                prob.author = request.user
                prob.point_value = test.default_point_value
                prob.blank_point_value = test.default_blank_value
                prob.order = test.problem_objects.count()+1
                prob.test = test
                prob.save()
                test.increment_version()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':test.problem_objects.count(),'problemset_list':problemset_list}),'pk':prob.pk})
        elif qt == "short answer":
            pform = NewProblemObjectSAForm(request.POST, instance = po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_' + str(prob.pk),'')
                compileasy(prob.problem_code,'originalproblem_' + str(prob.pk))
                compiletikz(prob.problem_code,'originalproblem_' + str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type = qt)
                prob.author = request.user
                prob.point_value = test.default_point_value
                prob.blank_point_value = test.default_blank_value
                prob.order = test.problem_objects.count() + 1
                prob.test = test
                prob.save()
                test.increment_version()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':test.problem_objects.count(),'problemset_list':problemset_list}),'pk':prob.pk})
        elif qt == "proof":
            pform = NewProblemObjectPFForm(request.POST, instance = po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_' + str(prob.pk),'')
                compileasy(prob.problem_code,'originalproblem_' + str(prob.pk))
                compiletikz(prob.problem_code,'originalproblem_' + str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type = qt)
                prob.author = request.user
                prob.point_value = test.default_point_value
                prob.blank_point_value = test.default_blank_value
                prob.order = test.problem_objects.count() + 1
                prob.test = test
                prob.save()
                test.increment_version()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':test.problem_objects.count(),'problemset_list':problemset_list}),'pk':prob.pk})
    return JsonResponse({'problem_text':'','pk':'0'})

@login_required
def testupdate_point_value(request,pk,upk,ppk,pppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    test = get_object_or_404(Test,pk = ppk)
    if unit.unit_objects.filter(test__isnull = False).filter(test__pk = test.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
    po = get_object_or_404(ProblemObject,pk = pppk)
    if request.method == 'POST':
        form = PointValueForm(request.POST,instance = po)
        if form.is_valid():
            form.save()
            data = {
                'pk': pppk,
                'point_value':form.instance.point_value,
            }
            po.increment_version()
            return JsonResponse(data)
    form = PointValueForm(instance = po)
    return render(request,'teacher/editingtemplates/editpointvalueform.html',{'form':form,'pk':pk,'upk':upk,'ppk':ppk,'pppk':pppk})

@login_required
def testupdate_blank_value(request,pk,upk,ppk,pppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    test = get_object_or_404(Test,pk = ppk)
    if unit.unit_objects.filter(test__isnull = False).filter(test__pk = test.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
    po = get_object_or_404(ProblemObject,pk = pppk)
    if request.method == 'POST':
        form = BlankPointValueForm(request.POST,instance = po)
        if form.is_valid():
            form.save()
            data = {
                'pk': pppk,
                'blank_point_value':form.instance.blank_point_value,
            }
            po.increment_version()
            return JsonResponse(data)
    form = BlankPointValueForm(instance = po)
    return render(request,'teacher/editingtemplates/editpointvalueform.html',{'form':form,'pk':pk,'upk':upk,'ppk':ppk,'pppk':pppk})

@login_required
def testnumprobsmatching(request,pk,upk,ppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    test = get_object_or_404(Test,pk = ppk)
    if unit.unit_objects.filter(test__isnull = False).filter(test__pk = test.pk).exists() == False:
        raise Http404("No such test in this unit.")
    form = request.GET
    typ = form.get('contest-type','')
    desired_tag = form.get('contest-tags','')
    curr_problems = test.problem_objects.filter(isProblem = 1)
    P = Problem.objects.filter(type_new__type = typ).filter(newtags__in = NewTag.objects.filter(tag__startswith = desired_tag)).exclude(id__in = curr_problems.values('problem_id')).distinct()####check this once contest problems are in a problem set.
    return JsonResponse({'num':str(P.count())})

@login_required
def testreviewmatchingproblems(request,pk,upk,ppk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    test = get_object_or_404(Test,pk = ppk)
    if unit.unit_objects.filter(test__isnull = False).filter(test__pk = test.pk).exists() == False:
        raise Http404("No such test in this unit.")
    P = []
    desired_tag = ''
    if request.method == 'POST':
        form = request.POST
        if 'add-selected-problems' in form:
            checked = form.getlist("chk")
            top = test.problem_objects.count()
            if len(checked) > 0:
                for i in range(0,len(checked)):
                    p = Problem.objects.get(label = checked[i])
                    po = ProblemObject(order = top + i + 1,point_value = test.default_point_value,blank_point_value = test.default_blank_value, test = test, isProblem = 1,problem = p,question_type = p.question_type_new)
                    po.save()
                test.increment_version()
                return redirect('../')
            return redirect('../')
        typ = form.get('contest-type','')
        desired_tag = form.get('contest-tags','')
        curr_problems = test.problem_objects.filter(isProblem=1)
        P = Problem.objects.filter(type_new__type = typ).filter(newtags__in = NewTag.objects.filter(tag__startswith = desired_tag)).exclude(id__in = curr_problems.values('problem_id')).distinct().order_by("problem_number")
    context = {}
    context['my_class'] = my_class
    context['unit'] = unit
    context['test'] = test
    context['nbar'] = 'teacher'
    context['rows'] = P
    context['tag'] = desired_tag
    return render(request,'teacher/editingtemplates/add-tagged-problems.html',context)

@login_required
def testreviewproblemgroup(request,pk,upk,ppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    test = get_object_or_404(Test,pk = ppk)
    if unit.unit_objects.filter(test__isnull = False).filter(test__pk = test.pk).exists()==False:
        raise Http404("No such test in this unit.")
    P = []
    desired_tag = ''
    if request.method == 'POST':
        form = request.POST
        if 'add-selected-problems' in form:
            checked = form.getlist("chk")
            top = test.problem_objects.count()
            if len(checked)>0:
                for i in range(0,len(checked)):
                    p = Problem.objects.get(label=checked[i])
                    po = ProblemObject(order = top + i + 1,point_value = test.default_point_value,blank_point_value = test.default_blank_value,isProblem = 1,problem = p,question_type = p.question_type_new,test = test)
                    po.save()
                test.increment_version()
                return redirect('../')
            return redirect('../')
        prob_group = get_object_or_404(ProblemGroup,pk = form.get('problem-group',''))
        curr_problems = test.problem_objects.filter(isProblem = 1)
        P = prob_group.problem_objects.exclude(problem__pk__in = curr_problems.values('problem_id')).distinct()
#        P = prob_group.problems.exclude(id__in = curr_problems.values('problem_id')).distinct()
    if request.method == 'GET':
        form = request.GET
        prob_group = get_object_or_404(ProblemGroup,pk = form.get('problem-group',''))
        curr_problems = test.problem_objects.filter(isProblem = 1)
#        P = prob_group.problems.exclude(id__in = curr_problems.values('problem_id')).distinct()
        P = prob_group.problem_objects.exclude(problem__pk__in = curr_problems.values('problem_id')).distinct()
    context = {}
    context['my_class'] = my_class
    context['unit'] = unit
    context['test'] = test
    context['nbar'] = 'teacher'
    context['rows'] = P
    context['prob_group'] = prob_group
    return render(request,'teacher/editingtemplates/review-problem-group.html',context)

###Slides###
@login_required
def slideseditview(request,pk,upk,spk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    slidegroup = get_object_or_404(SlideGroup,pk = spk)
    if unit.unit_objects.filter(slidegroup__isnull = False).filter(slidegroup__pk = slidegroup.pk).exists() == False:
        raise Http404("No such slides in this unit.")
    if request.method == "POST":
        form = request.POST
        if 'save' in form:#######
            slides = list(slidegroup.slides.all())
            slides = sorted(slides,key = lambda x:x.order)
            slide_inputs = form.getlist('slideinput')
            deleted = 0
            for s in slides:
                if 'slide_'+str(s.pk) not in slide_inputs:
                    s.delete()
                    deleted = 1
            for i in range(0,len(slide_inputs)):
                s = slidegroup.slides.get(pk = slide_inputs[i].split('_')[1])###better way to do this? (i.e., get the query set first)
                s.order = i+1
                s.save()
                s.increment_version()
                deleted = 0
            if deleted == 1:
                slidegroup.increment_version()
            return JsonResponse({'slidelist':render_to_string('teacher/editingtemplates/editslides/slidelist.html',{'slides' :slidegroup})})
    context = {}
    context['my_class'] = my_class
    context['unit'] = unit
    context['slides'] = slidegroup
    context['nbar'] = 'teacher'
    context['sharing_type'] = sharing_type
    return render(request,'teacher/editingtemplates/editslidesview.html',context)

@login_required
def editslidegroupname(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    slidegroup = get_object_or_404(SlideGroup,pk = pk)
    my_class = slidegroup.unit_object.unit.the_class
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    form = EditSlideGroupNameForm(instance = slidegroup)
    return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/modals/modal-edit-slidegroup-name.html',{'form':form})})

@login_required
def saveslidegroupname(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    slidegroup = get_object_or_404(SlideGroup,pk = pk)
    my_class = slidegroup.unit_object.unit.the_class
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    form = EditSlideGroupNameForm(request.POST,instance = slidegroup)
    form.save()
    slidegroup.increment_version()
    return JsonResponse({'slidegroup-name':form.instance.name})

@login_required
def newslideview(request,pk,upk,spk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists==False:
        raise Http404("No such unit in this class.")
    slidegroup = get_object_or_404(SlideGroup,pk = spk)
    if unit.unit_objects.filter(slidegroup__isnull = False).filter(slidegroup__pk = slidegroup.pk).exists() == False:
        raise Http404("No such slides in this unit.")
    if request.method == "POST":
        form = request.POST
        s = Slide(title = form.get("slide-title",""),order = slidegroup.slides.count() + 1,slidegroup = slidegroup)
        s.save()
        slidegroup.increment_version()
        return JsonResponse({'slide-body':render_to_string('teacher/editingtemplates/editslides/slidebody.html',{'slide':s,'forcount':s.order})})
#    return HttpResponse('')

def editslideview(request,pk,upk,spk,sspk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none':
        raise Http404("Unauthorized.")
    context = {}
    context['sharing_type'] = sharing_type
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.unit_set.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    slidegroup = get_object_or_404(SlideGroup,pk=spk)
    if unit.unit_objects.filter(slidegroup__isnull=False).filter(slidegroup__pk=slidegroup.pk).exists()==False:
        raise Http404("No such slides in this unit.")
    slide = get_object_or_404(Slide,pk=sspk)
    if slidegroup.slides.filter(pk=slide.pk).exists()==False:
        raise Http404("No such slide in the slide group.")

    if request.method == "POST":
        form = request.POST
        if "addtextblock" in form:
            s = SlideObject(slide = slide,order = slide.top_order_number + 1)
            s.save()
            textbl = form.get("codetextblock","")
            tb = TextBlock(up_slide_object = s, text_code = textbl, text_display = "")
            tb.save()
            tb.text_display = newtexcode(textbl, 'textblock_' + str(tb.pk), "")
            tb.save()
            compileasy(tb.text_code,'textblock_' + str(tb.pk))
            compiletikz(tb.text_code,'textblock_' + str(tb.pk))
            slide.top_order_number = slide.top_order_number + 1
            slide.save()
            slide.increment_version()
            return JsonResponse({'textblock':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})
        if "addtheorem" in form:
            s = SlideObject(slide = slide,order = slide.top_order_number + 1)
            s.save()
            thmbl = form.get("codetheoremblock","")
            prefix = form.get("theorem-prefix","")
            thmname = form.get("theorem-name","")
            th = Theorem(up_slide_object = s,theorem_code = thmbl, theorem_display = "",prefix = prefix,name = thmname)
            th.save()
            th.theorem_display = newtexcode(thmbl, 'theoremblock_'+str(th.pk), "")
            th.save()
            compileasy(th.text_code,'theoremblock_' + str(th.pk))
            compiletikz(th.text_code,'theoremblock_' + str(th.pk))
            slide.top_order_number = slide.top_order_number +1
            slide.save()
            slide.increment_version()
            return JsonResponse({'theorem':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})
        if "addproof" in form:
            s = SlideObject(slide = slide,order = slide.top_order_number + 1)
            s.save()
            proofbl = form.get("codeproofblock","")
            prefix = form.get("proof-prefix","")
            pf = Proof(up_slide_object = s, proof_code = proofbl, proof_display = "",prefix = prefix)
            pf.save()
            pf.proof_display = newtexcode(proofbl, 'proofblock_'+str(pf.pk), "")
            pf.save()
            compileasy(pf.proof_code,'proofblock_'+str(pf.pk))#######Check
            compiletikz(pf.proof_code,'proofblock_'+str(pf.pk))#######Check
            slide.top_order_number = slide.top_order_number +1
            slide.save()
            slide.increment_version()
            return JsonResponse({'proof':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})
        if "addimage" in form:
            form = ImageForm(request.POST, request.FILES)
            if form.is_valid():
                s = SlideObject(slide = slide,order = slide.top_order_number + 1)
                s.save()
                m = ImageModel(up_slide_object = s,image = form.cleaned_data['image'])
                m.save()
                slide.top_order_number = slide.top_order_number +1
                slide.save()
                slide.increment_version()
                return JsonResponse({'image':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})
        if "addproblem" in form:
            prefix = form.get("example-prefix","")
            source = form.get("problem-source","")
            if source == "bylabel":
                problem_label = form.get("problem-label","")
                if Problem.objects.filter(label = problem_label).exists():
                    p = Problem.objects.get(label = problem_label)
                    if p.type_new in userprofile.user_type_new.allowed_types.all():
                        s = SlideObject(slide = slide,order = slide.top_order_number + 1)
                        s.save()
                        ep = ExampleProblem(up_slide_object = s,isProblem = 1,problem = p,question_type = p.question_type_new,prefix=prefix)
                        ep.save()
                        slide.top_order_number = slide.top_order_number + 1
                        slide.save()
                        slide.increment_version()
                        return JsonResponse({'example':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})
                    else:
                        return JsonResponse({'error-msg': "No such problem with label"})
                else:
                    return JsonResponse({'error-msg': "No such problem with label"})
#            elif source == "bygroup":
#                pass
            elif source == "original":
                qt = form.get('question-type','')
                s = SlideObject(slide = slide,order = slide.top_order_number + 1)
                s.save()
                ep = ExampleProblem(up_slide_object = s)
                if qt == "multiple choice":
                    pform = NewExampleProblemMCForm(request.POST, instance = ep)
                    if pform.is_valid():
                        prob = pform.save()
                        prob.problem_display = newtexcode(prob.problem_code,'exampleproblem_'+str(prob.pk),prob.answers())
                        prob.prefix = prefix
                        compileasy(prob.problem_code,'exampleproblem_'+str(prob.pk))
                        compiletikz(prob.problem_code,'exampleproblem_'+str(prob.pk))
                        prob.question_type = QuestionType.objects.get(question_type = qt)
                        prob.author = request.user
                        prob.save()
                        slide.top_order_number = slide.top_order_number + 1
                        slide.save()
                        slide.increment_version()
                elif qt == "short answer":
                    pform = NewExampleProblemSAForm(request.POST, instance = ep)
                    if pform.is_valid():
                        prob = pform.save()
                        prob.problem_display = newtexcode(prob.problem_code,'exampleproblem_'+str(prob.pk),'')
                        prob.prefix = prefix
                        compileasy(prob.problem_code,'exampleproblem_'+str(prob.pk))
                        compiletikz(prob.problem_code,'exampleproblem_'+str(prob.pk))
                        prob.question_type = QuestionType.objects.get(question_type = qt)
                        prob.author = request.user
                        prob.save()
                        slide.top_order_number = slide.top_order_number + 1
                        slide.save()
                        slide.increment_version()
                elif qt == "proof":
                    pform = NewExampleProblemPFForm(request.POST, instance = ep)
                    if pform.is_valid():
                        prob = pform.save()
                        prob.problem_display = newtexcode(prob.problem_code,'exampleproblem_'+str(prob.pk),'')
                        prob.prefix = prefix
                        compileasy(prob.problem_code,'exampleproblem_'+str(prob.pk))
                        compiletikz(prob.problem_code,'exampleproblem_'+str(prob.pk))
                        prob.question_type = QuestionType.objects.get(question_type = qt)
                        prob.author = request.user
                        prob.save()
                        slide.top_order_number = slide.top_order_number + 1
                        slide.save()
                        slide.increment_version()
                return JsonResponse({'example':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})
        if 'save' in form:
            slide_objs = list(slide.slide_objects.all())
            slide_objs = sorted(slide_objs,key = lambda x:x.order)
            slide_obj_inputs = form.getlist('slideobjectinput')
            deleted = 0
            for s in slide_objs:
                if 'slideobject_'+str(s.pk) not in slide_obj_inputs:
                    s.delete()
                    deleted = 1
            for i in range(0,len(slide_obj_inputs)):
                s = slide.slide_objects.get(pk = slide_obj_inputs[i].split('_')[1])###better way to do this? (i.e., get the query set first)
                s.order = i + 1
                s.save()
                s.increment_version()
                deleted = 0
            slide.top_order_number = slide.slide_objects.count()
            slide.save()
            if deleted == 1:
                slide.increment_version()
            return JsonResponse({'slideobjectlist':render_to_string('teacher/editingtemplates/edit-slide/slideobjectlist.html',{'slide_objects' :slide.slide_objects.all()})})
    context['my_class'] = my_class
    context['unit'] = unit
    context['slides'] = slidegroup
    context['slide'] = slide
    context['nbar'] = 'teacher'
    return render(request,'teacher/editingtemplates/edit-slide.html',context)

@login_required
def editslidetitle(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    slide = get_object_or_404(Slide,pk = pk)
    my_class = slide.slidegroup.unit_object.unit.the_class
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    form = EditSlideTitleForm(instance = slide)
    return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/modals/modal-edit-slide-title.html',{'form':form})})

@login_required
def saveslidetitle(request):
    userprofile = request.user.userprofile
    pk = request.POST.get('pk','')
    slide = get_object_or_404(Slide,pk=pk)
    my_class = slide.slidegroup.unit_object.unit.the_class
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    form = EditSlideTitleForm(request.POST,instance = slide)
    form.save()
    slide.increment_version()
    return JsonResponse({'slide-title':form.instance.title})

@login_required
def exampleoriginalqt(request,**kwargs):
    return JsonResponse({'qt-form':render_to_string('teacher/editingtemplates/example-original-question-type.html')})

@login_required
def exampleproblemlabel(request,**kwargs):
    return JsonResponse({'pl-form':render_to_string('teacher/editingtemplates/example-problem-label.html')})

@login_required
def exampleproblemgroups(request,**kwargs):
    userprofile = request.user.userprofile
    co_owned_pgs =  userprofile.owned_problem_groups.all()
    editor_pgs =  userprofile.editable_problem_groups.all()
    readonly_pgs =  userprofile.readonly_problem_groups.all()
    owned_pgs = userprofile.problem_groups.all()
    probgroups = list(chain(owned_pgs,co_owned_pgs,editor_pgs,readonly_pgs))
    return JsonResponse({'pg-form':render_to_string('teacher/editingtemplates/example-problem-group.html',{'pg':probgroups})})#request.user.userprofile.problem_groups.all()})})

@login_required
def exampleaddproblem(request,**kwargs):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk = kwargs['pk'])
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = kwargs['upk'])
    if my_class.unit_set.filter(pk = kwargs['upk']).exists == False:
        raise Http404("No such unit in this class.")
    slidegroup = get_object_or_404(SlideGroup,pk = kwargs['spk'])
    if unit.unit_objects.filter(slidegroup__isnull = False).filter(slidegroup__pk = slidegroup.pk).exists() == False:
        raise Http404("No such slides in this unit.")
    slide = get_object_or_404(Slide,pk = kwargs['sspk'])
    if slidegroup.slides.filter(pk = slide.pk).exists() == False:
        raise Http404("No such slide in the slide group.")
    form = request.GET
    prefix = form.get("example-prefix","")
    p = Problem.objects.get(pk = form.get('pk',''))
    s = SlideObject(slide = slide,order = slide.top_order_number + 1)
    s.save()
    ep = ExampleProblem(up_slide_object = s, isProblem = 1,problem = p,question_type = p.question_type_new,prefix = prefix)
    ep.save()
    slide.top_order_number = slide.top_order_number + 1
    slide.save()
    slide.increment_version()
    return JsonResponse({'example':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})



@login_required
def exampleproblemgroupproblems(request,**kwargs):
    form = request.GET
    problem_group = get_object_or_404(ProblemGroup,pk = form.get('example-problem-group',''))
    return JsonResponse({'pgp-form':render_to_string('teacher/editingtemplates/example-problem-group-problems.html',{'problem_group':problem_group})})

@login_required
def examplebytag(request,**kwargs):
    contest_types = request.user.userprofile.user_type_new.allowed_types.all()
    tags = NewTag.objects.exclude(tag = 'root')
    return JsonResponse({'tag-form':render_to_string('teacher/editingtemplates/example-bytag.html',{'contest_types':contest_types,'tags':tags})})

@login_required
def examplebytagproblems(request,**kwargs):
    form = request.GET
    problems = Problem.objects.filter(type_new__type = form.get('example-contest-type','')).filter(newtags__in = NewTag.objects.filter(tag__startswith = NewTag.objects.get(pk = form.get('example-tag',''))))
    return JsonResponse({'problems':render_to_string('teacher/editingtemplates/example-bytag-problems.html',{'rows':problems})})

@login_required
def editexampleproblem(request,pk,upk,spk,sspk,sopk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none' or sharing_type == 'read':
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.unit_set.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    slidegroup = get_object_or_404(SlideGroup,pk = spk)
    if unit.unit_objects.filter(slidegroup__isnull = False).filter(slidegroup__pk = slidegroup.pk).exists() == False:
        raise Http404("No such slides in this unit.")
    slide = get_object_or_404(Slide,pk = sspk)
    if slidegroup.slides.filter(pk = slide.pk).exists() == False:
        raise Http404("No such slide in the slide group.")
    ep = get_object_or_404(ExampleProblem,pk = sopk)
    if slide.slide_objects.exclude(exampleproblem = None).filter(exampleproblem__id = ep.pk).exists() == False:
        raise Http404("No such object in slide.")
    so = slide.slide_objects.exclude(exampleproblem = None).get(exampleproblem__id = ep.pk)
    if request.method == "POST":
        form = request.POST
        qt = form.get('cqt-question-type','')
        qt_dict = {'mc' : 'multiple choice', 'sa' : 'short answer', 'pf' : 'proof'}
        if ep.isProblem == 0:
            if qt == "mc":
                pform = NewExampleProblemMCForm(request.POST, instance = ep)
                if pform.is_valid():
                    prob = pform.save()
                    prob.problem_display = newtexcode(prob.problem_code,'exampleproblem_' + str(prob.pk),prob.answers())
                    compileasy(prob.problem_code,'exampleproblem_' + str(prob.pk))
                    compiletikz(prob.problem_code,'exampleproblem_' + str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type = qt_dict[qt])
                    prob.author = request.user
                    prob.save()
                    ep.increment_version()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/edit-slide/slideobjectbody.html',{'s':so}),'qt':qt,'sopk':so.pk})
            elif qt == "sa":
                pform = NewExampleProblemSAForm(request.POST, instance = ep)
                if pform.is_valid():
                    prob = pform.save()
                    prob.problem_display = newtexcode(prob.problem_code,'exampleproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'exampleproblem_'+str(prob.pk))
                    compiletikz(prob.problem_code,'exampleproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type = qt_dict[qt])
                    prob.save()
                    ep.increment_version()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/edit-slide/slideobjectbody.html',{'s':so}),'qt':qt,'sopk':so.pk})
            elif qt == "pf":
                pform = NewExampleProblemPFForm(request.POST, instance = ep)
                if pform.is_valid():
                    prob = pform.save()
                    prob.problem_display = newtexcode(prob.problem_code,'exampleproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'exampleproblem_'+str(prob.pk))
                    compiletikz(prob.problem_code,'exampleproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type = qt_dict[qt])
                    prob.save()
                    ep.increment_version()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/edit-slide/slideobjectbody.html',{'s':so}),'qt':qt,'sopk':so.pk})
        else:
            ep.question_type = QuestionType.objects.get(question_type = qt_dict[qt])
            ep.save()
            ep.increment_version()
            return JsonResponse({'prob':render_to_string('teacher/editingtemplates/edit-slide/slideobjectbody.html',{'s':so}),'sopk': so.pk})
    if ep.isProblem == 0:
        return JsonResponse({'modal-html' : render_to_string('teacher/editingtemplates/edit-slide/modals/modal-edit-exampleproblem.html', {'ep' : ep})})
    else:
        pqt =  ep.problem.question_type_new.question_type
        qt =  ep.question_type.question_type
        if pqt == 'multiple choice':
            qts=[1,0,1]
            qts=['mc','pf']
        if pqt == 'short answer':
            qts=[0,1,1]
            qts=['sa','pf']
        if pqt == 'multiple choice short answer':
            qts=[1,1,1]
            qts=['mc','sa','pf']
        if pqt == 'proof':
            qts=[0,0,1]
            qts=['pf']
        if qt == 'multiple choice':
            answers = ep.problem.answers()#added.problem here....check on loadeditproblem...
            problem_display = newtexcode(ep.problem.mc_problem_text,str(ep.problem.label),answers)
        else:
            problem_display = ep.problem.display_problem_text
        return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/edit-slide/modals/modal-edit-exampleproblem.html',{'ep':ep,'qts':qts}), 'latex_display' : render_to_string('teacher/editingtemplates/edit-slide/modals/exampleproblem-latex.html', {'problem_display' : problem_display})})

class TextBlockUpdateView(UpdateView):
    model = TextBlock
    form_class = TextBlockForm
    template_name = 'teacher/editingtemplates/editslides/modals/textblock_edit_form.html'

    def dispatch(self, *args, **kwargs):
        self.textblock_id = kwargs['tpk']
        self.url_pk = kwargs['pk']
        self.url_upk = kwargs['upk']
        self.url_spk = kwargs['spk']
        self.url_sspk = kwargs['sspk']
        return super(TextBlockUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        textblock = TextBlock.objects.get(id=self.textblock_id)
        textblock.text_display = newtexcode(textblock.text_code, 'textblock_'+str(textblock.pk), "")
        compileasy(textblock.text_code,'textblock_'+str(textblock.pk))
        compiletikz(textblock.text_code,'textblock_'+str(textblock.pk))
        textblock.increment_version()
        return JsonResponse({'slide-code':render_to_string('teacher/editingtemplates/edit-slide/slideobjectbody.html',{'s':textblock.up_slide_object}),'sopk':textblock.up_slide_object.pk})

    def get_object(self, queryset=None):
        return get_object_or_404(TextBlock, pk=self.textblock_id)
    def get_context_data(self, *args, **kwargs):
        context = super(TextBlockUpdateView, self).get_context_data(*args, **kwargs)
        context['pk'] = self.url_pk
        context['upk'] = self.url_upk
        context['spk'] = self.url_spk
        context['sspk'] = self.url_sspk
        return context

class TheoremUpdateView(UpdateView):
    model = Theorem
    form_class = TheoremForm
    template_name = 'teacher/editingtemplates/editslides/modals/theorem_edit_form.html'

    def dispatch(self, *args, **kwargs):
        self.theorem_id = kwargs['tpk']
        self.url_pk = kwargs['pk']
        self.url_upk = kwargs['upk']
        self.url_spk = kwargs['spk']
        self.url_sspk = kwargs['sspk']
        return super(TheoremUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        theorem = Theorem.objects.get(id=self.theorem_id)
        theorem.theorem_display = newtexcode(theorem.theorem_code, 'theoremblock_'+str(theorem.pk), "")
        compileasy(theorem.theorem_code,'theoremblock_'+str(theorem.pk))
        compiletikz(theorem.theorem_code,'theoremblock_'+str(theorem.pk))
        theorem.increment_version()
        return JsonResponse({'slide-code':render_to_string('teacher/editingtemplates/edit-slide/slideobjectbody.html',{'s':theorem.up_slide_object}),'sopk':theorem.up_slide_object.pk})

    def get_object(self, queryset=None):
        return get_object_or_404(Theorem, pk=self.theorem_id)
    def get_context_data(self, *args, **kwargs):
        context = super(TheoremUpdateView, self).get_context_data(*args, **kwargs)
        context['pk'] = self.url_pk
        context['upk'] = self.url_upk
        context['spk'] = self.url_spk
        context['sspk'] = self.url_sspk
        return context

class ProofUpdateView(UpdateView):
    model = Proof
    form_class = ProofForm
    template_name = 'teacher/editingtemplates/editslides/modals/proof_edit_form.html'

    def dispatch(self, *args, **kwargs):
        self.proof_id = kwargs['tpk']
        self.url_pk = kwargs['pk']
        self.url_upk = kwargs['upk']
        self.url_spk = kwargs['spk']
        self.url_sspk = kwargs['sspk']
        return super(ProofUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        proof = Proof.objects.get(id=self.proof_id)
        proof.proof_display = newtexcode(proof.proof_code, 'proofblock_'+str(proof.pk), "")
        compileasy(proof.proof_code,'proofblock_'+str(proof.pk))
        compiletikz(proof.proof_code,'proofblock_'+str(proof.pk))
        proof.increment_version()
        return JsonResponse({'slide-code':render_to_string('teacher/editingtemplates/edit-slide/slideobjectbody.html',{'s':proof.up_slide_object}),'sopk':proof.up_slide_object.pk})


    def get_object(self, queryset=None):
        return get_object_or_404(Proof, pk=self.proof_id)
    def get_context_data(self, *args, **kwargs):
        context = super(ProofUpdateView, self).get_context_data(*args, **kwargs)
        context['pk'] = self.url_pk
        context['upk'] = self.url_upk
        context['spk'] = self.url_spk
        context['sspk'] = self.url_sspk
        return context

@login_required
def currentclassview(request,pk):#only for published classes...grading; viewing; etc.
    userprofile=request.user.userprofile
    my_class = get_object_or_404(PublishedClass,pk=pk)
    return render(request,'teacher/publishedclasses/classview.html',{'class':my_class,'nbar':'teacher'})

@login_required
def studentmanager(request):#request student accounts; add to classes
    userprofile = request.user.userprofile
    return render(request,'teacher/students/studentmanager.html',{'userprofile':userprofile,'nbar':'teacher'})

@login_required
def blindgrade(request,**kwargs):
    my_class = get_object_or_404(PublishedClass,pk=kwargs['pk'])
    problemset = get_object_or_404(PublishedProblemSet,pk=kwargs['pspk'])##
    problem_object = get_object_or_404(PublishedProblemObject,pk=kwargs['popk'])
    if problem_object.question_type.question_type != 'proof':
        raise Http404('Not a proof question')
    responses = list(problem_object.response_set.all())
    shuffle(responses)
    return render(request,'teacher/publishedclasses/blindgrading.html',{'problem_object':problem_object,'responses':responses,'class':my_class,'problemset':problemset,'nbar':'teacher'})

@login_required
def alphagrade(request,**kwargs):
    my_class = get_object_or_404(PublishedClass,pk=kwargs['pk'])
    problemset = get_object_or_404(PublishedProblemSet,pk=kwargs['pspk'])
    problem_object = get_object_or_404(PublishedProblemObject,pk=kwargs['popk'])
    if problem_object.question_type.question_type != 'proof':
        raise Http404('Not a proof question')
    responses = problem_object.response_set.order_by('user_problemset__userunitobject__user_unit__user_class__userprofile__user__username')
    return render(request,'teacher/publishedclasses/alphagrading.html',{'problem_object':problem_object,'responses':responses,'class':my_class,'problemset':problemset,'nbar':'teacher'})




#######PROBLEM GROUPS#######
@login_required
def grouptableview(request):
    userprofile = request.user.userprofile

    owned_pgs =  userprofile.problem_groups.all()
    co_owned_pgs =  userprofile.owned_problem_groups.all()
    editor_pgs =  userprofile.editable_problem_groups.all()
    readonly_pgs =  userprofile.readonly_problem_groups.all()

    template = loader.get_template('teacher/problemgroups/grouptableview.html')

    group_inst = ProblemGroup(name='')
    form = GroupModelForm(instance=group_inst)
    context = {}
    context['form'] = form
    context['nbar'] = 'teacher'
    context['owned_pgs'] = owned_pgs
    context['co_owned_pgs'] = co_owned_pgs
    context['editor_pgs'] = editor_pgs
    context['readonly_pgs'] = readonly_pgs
    return HttpResponse(template.render(context,request))


@login_required
def migrate_response(request,username,npk):
    user=get_object_or_404(User,username=username)
    userprofile=user.userprofile
    if user not in request.user.userprofile.students.all():
        raise Http404('no')
    newuserclass = get_object_or_404(UserClass,pk=npk)
    if newuserclass not in userprofile.userclasses.all():
        raise Http404('nouc')
    usertests = userprofile.usertests.all()
    user_psets = UserProblemSet.objects.filter(userunitobject__user_unit__user_class=newuserclass)
    UTR = []
    for ut in usertests:
        R=[]
        for r in ut.newresponses.all():
            J=[]
            for ups in user_psets:
                if ups.published_problemset.problem_objects.filter(problem=r.problem).exists():
                    J.append(ups)
            R.append((r,J))
        UTR.append((ut,R))
    return render(request,'teacher/response_migration.html', {'usertests':usertests,'user_psets':user_psets,'UTR':UTR})

@login_required
def move_response(request,**kwargs):
    user=get_object_or_404(User,username=kwargs['username'])
    userprofile=user.userprofile
    if user not in request.user.userprofile.students.all():
        raise Http404('no')
    userclass = get_object_or_404(UserClass,pk=kwargs['npk'])
    if userclass not in userprofile.userclasses.all():
        raise Http404('nouc')
    resp_pk = request.GET.get('resp_pk','')
    resp = get_object_or_404(NewResponse,pk=resp_pk)
    ups_pk = request.GET.get('ups_pk','')
    user_problemset = get_object_or_404(UserProblemSet,pk=ups_pk)
    po = user_problemset.published_problemset.problem_objects.get(problem = resp.problem)
    if user_problemset.response_set.filter(problem_object = po).exists()==False:
        r = Response(problem_object = po, user_problemset=user_problemset, response = resp.response,attempted = resp.attempted, stickied = resp.stickied, order = po.order, point_value = po.point_value, modified_date = resp.modified_date)
        r.save()
        if po.question_type.question_type == "short answer":
            if resp.response == po.sa_answer:
                r.points = r.point_value
                r.save()
        resp.is_migrated = 1
        resp.save()
        return JsonResponse({'success':1,'name':user_problemset.published_problemset.name,'resp_pk':resp_pk})
    return JsonResponse({'success':0,'name':''})




@login_required
def load_edit_duedate(request):
    data_type = request.POST.get('uo')
    if data_type == 'ps':
        problemset = get_object_or_404(ProblemSet,pk=request.POST.get('pk'))
        if problemset.due_date == None:
            default_date = timezone.now()
        else:
            default_date = problemset.due_date
        return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/modals/modal-edit-duedate.html',{'problemset' : problemset}),'date' : default_date})
    elif data_type == "tst":
        test = get_object_or_404(Test,pk=request.POST.get('pk'))
        if test.due_date == None:
            default_date = timezone.now()
        else:
            default_date = test.due_date
        return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/modals/modal-edit-duedate.html',{'test' : test}),'date' : default_date})

@login_required
def save_duedate(request):
    data_type = request.POST.get('uo')
    if data_type == 'ps':
        problemset = get_object_or_404(ProblemSet,pk=request.POST.get('edps-pk'))
        due_date = request.POST.get('due_date')
        tz = pytz.timezone(request.user.userprofile.time_zone)
        tz_due_date = tz.localize(datetime.strptime(due_date,'%m/%d/%Y %I:%M %p'))
        if problemset.start_date != None:
            if problemset.start_date >= tz_due_date:
                return JsonResponse({'error': 'Due date is before start date'})
        problemset.due_date = tz_due_date
        problemset.save()
        problemset.increment_version()
        return JsonResponse({'date_snippet':render_to_string('teacher/editingtemplates/due_date_snippet.html',{'problemset':problemset,'request':request})})
    elif data_type == 'tst':
        test = get_object_or_404(Test,pk=request.POST.get('edps-pk'))
        due_date = request.POST.get('due_date')
        tz = pytz.timezone(request.user.userprofile.time_zone)
        tz_due_date = tz.localize(datetime.strptime(due_date,'%m/%d/%Y %I:%M %p'))
        if test.start_date != None:
            if test.start_date >= tz_due_date:
                return JsonResponse({'error': 'Due date is before start date'})
        test.due_date = tz_due_date
        test.save()
        test.increment_version()
        return JsonResponse({'date_snippet':render_to_string('teacher/editingtemplates/due_date_snippet.html',{'test':test,'request':request})})
    
@login_required
def delete_duedate(request):
    data_type = request.POST.get('uo')
    if data_type == 'ps':
        problemset = get_object_or_404(ProblemSet,pk=request.POST.get('pk'))
        problemset.due_date = None
        problemset.save()
        problemset.increment_version()
        return JsonResponse({'date_snippet':render_to_string('teacher/editingtemplates/due_date_snippet.html',{'problemset':problemset,'request':request})})
    elif data_type == 'tst':
        test = get_object_or_404(Test,pk=request.POST.get('pk'))
        test.due_date = None
        test.save()
        test.increment_version()
        return JsonResponse({'date_snippet':render_to_string('teacher/editingtemplates/due_date_snippet.html',{'test' : test,'request':request})})


@login_required
def load_edit_startdate(request):
    data_type = request.POST.get('uo')
    if data_type == 'ps':
        problemset = get_object_or_404(ProblemSet,pk=request.POST.get('pk'))
        if problemset.start_date == None:
            default_date = timezone.now()
        else:
            default_date = problemset.start_date
        return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/modals/modal-edit-startdate.html',{'problemset' : problemset}),'date' : default_date})
    elif data_type == "tst":
        test = get_object_or_404(Test,pk=request.POST.get('pk'))
        if test.start_date == None:
            default_date = timezone.now()
        else:
            default_date = test.start_date
        return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/modals/modal-edit-startdate.html',{'test' : test}),'date' : default_date})

@login_required
def save_startdate(request):
    data_type = request.POST.get('uo')
    if data_type == 'ps':
        problemset = get_object_or_404(ProblemSet,pk=request.POST.get('edps-pk'))
        start_date = request.POST.get('start_date')
        tz = pytz.timezone(request.user.userprofile.time_zone)
        tz_start_date = tz.localize(datetime.strptime(start_date,'%m/%d/%Y %I:%M %p'))
        if problemset.due_date != None:
            if problemset.due_date <= tz_start_date:
                return JsonResponse({'error': 'Start date is after end date'})
        problemset.start_date = tz_start_date
        problemset.save()
        problemset.increment_version()
        return JsonResponse({'date_snippet':render_to_string('teacher/editingtemplates/due_date_snippet.html',{'problemset':problemset,'request':request})})
    elif data_type == 'tst':
        test = get_object_or_404(Test,pk=request.POST.get('edps-pk'))
        start_date = request.POST.get('start_date')
        tz = pytz.timezone(request.user.userprofile.time_zone)
        tz_start_date = tz.localize(datetime.strptime(start_date,'%m/%d/%Y %I:%M %p'))
        if test.due_date != None:
            if test.due_date <= tz_start_date:
                return JsonResponse({'error': 'Start date is after end date'})
        test.start_date = tz_start_date
        test.save()
        test.increment_version()
        return JsonResponse({'date_snippet':render_to_string('teacher/editingtemplates/due_date_snippet.html',{'test':test,'request':request})})
    
@login_required
def delete_startdate(request):
    data_type = request.POST.get('uo')
    if data_type == 'ps':
        problemset = get_object_or_404(ProblemSet,pk=request.POST.get('pk'))
        problemset.start_date = None
        problemset.save()
        problemset.increment_version()
        return JsonResponse({'date_snippet':render_to_string('teacher/editingtemplates/due_date_snippet.html',{'problemset':problemset,'request':request})})
    elif data_type == 'tst':
        test = get_object_or_404(Test,pk=request.POST.get('pk'))
        test.start_date = None
        test.save()
        test.increment_version()
        return JsonResponse({'date_snippet':render_to_string('teacher/editingtemplates/due_date_snippet.html',{'test' : test,'request':request})})



@login_required
def load_edit_timelimit(request):
    data_type = request.POST.get('uo')
    if data_type == 'ps':
        problemset = get_object_or_404(ProblemSet,pk=request.POST.get('pk'))
        if problemset.time_limit == None:
            default_hours = 1
            default_minutes = 0
        else:
            default_hours = problemset.time_limit.hour
            default_minutes = problemset.time_limit.minute
        return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/modals/modal-edit-timelimit.html',{'problemset' : problemset,'default_hours':default_hours,'default_minutes':default_minutes,'minuterange':[5*i for i in range(0,12)]})})
    elif data_type == 'tst':
        test = get_object_or_404(Test,pk=request.POST.get('pk'))
        if test.time_limit == None:
            default_hours = 1
            default_minutes = 0
        else:
            default_hours = test.time_limit.hour
            default_minutes = test.time_limit.minute
        return JsonResponse({'modal-html':render_to_string('teacher/editingtemplates/modals/modal-edit-timelimit.html',{'test' : test,'default_hours':default_hours,'default_minutes':default_minutes,'minuterange':[5*i for i in range(0,12)]})})

@login_required
def save_timelimit(request):
    data_type = request.POST.get('uo')
    if data_type == 'ps':
        problemset = get_object_or_404(ProblemSet,pk=request.POST.get('edps-pk'))
        minutes = request.POST.get('minutes')
        hours = request.POST.get('hours')
        problemset.time_limit = time(hour=int(hours),minute=int(minutes))
        problemset.save()
        problemset.increment_version()
        return JsonResponse({'time_snippet':render_to_string('teacher/editingtemplates/time_limit_snippet.html',{'problemset':problemset,'request':request})})
    elif data_type == 'tst':
        test = get_object_or_404(Test,pk=request.POST.get('edps-pk'))
        minutes = request.POST.get('minutes')
        hours = request.POST.get('hours')
        test.time_limit = time(hour=int(hours),minute=int(minutes))
        test.save()
        test.increment_version()
        return JsonResponse({'time_snippet':render_to_string('teacher/editingtemplates/time_limit_snippet.html',{'test':test,'request':request})})

@login_required
def delete_timelimit(request):
    data_type = request.POST.get('uo')
    if data_type == 'ps':
        problemset = get_object_or_404(ProblemSet,pk=request.POST.get('pk'))
        problemset.time_limit = None
        problemset.save()
        problemset.increment_version()
        return JsonResponse({'time_snippet':render_to_string('teacher/editingtemplates/time_limit_snippet.html',{'problemset':problemset,'request':request})})
    elif data_type == 'tst':
        test = get_object_or_404(Test,pk=request.POST.get('pk'))
        test.time_limit = None
        test.save()
        test.increment_version()
        return JsonResponse({'time_snippet':render_to_string('teacher/editingtemplates/time_limit_snippet.html',{'test':test,'request':request})})


####################
#####SHARING CLASSES
####################
@login_required
def load_sharing_modal(request,**kwargs):
    userprofile = request.user.userprofile
    context={}
    pk = request.POST.get('pk','')
    my_class = get_object_or_404(Class,pk=pk)
    context['cl'] = my_class
    owners = my_class.userprofiles.all()
    coowners = my_class.owneruserprofiles.all()
    editors = my_class.editoruserprofiles.all()
    readers = my_class.readeruserprofiles.all()
    context['owners'] = owners
    context['coowners'] = coowners
    context['editors'] = editors
    context['read_only_users'] = readers
    context['collaborators'] = userprofile.collaborators.exclude(userprofile__pk__in=owners.values_list('pk')).exclude(userprofile__pk__in=editors.values_list('pk')).exclude(userprofile__pk__in=readers.values_list('pk')).exclude(userprofile__pk__in=coowners.values_list('pk'))
    if userprofile in owners or userprofile in coowners:
        context['is_owner'] = 1
    context['userprofile'] = userprofile
    return JsonResponse({'modal-html' : render_to_string('teacher/sharing/modals/edit-sharing.html',context)})

@login_required
def share_with_user(request, **kwargs):
    userprofile = request.user.userprofile
    form = request.POST
    pk = form.get('classpk','')
    my_class = get_object_or_404(Class,pk = pk)
    share_target = get_object_or_404(User,pk = form.get('collaborator',''))
    share_target_up = share_target.userprofile
    sharing_type = form.get('sharing-type','')
    if my_class in userprofile.my_classes.all() or my_class in userprofile.owned_my_classes.all():
        if sharing_type == 'read':
            if my_class not in share_target_up.editable_my_classes.all() and my_class not in share_target_up.owned_my_classes.all() and my_class not in share_target_up.my_classes.all():
                share_target_up.readonly_my_classes.add(my_class)
                share_target_up.save()
            return JsonResponse({'user-row' : render_to_string('teacher/sharing/modals/user-row.html',{'sharing_type': 'reader','shared_user' : share_target_up, 'is_owner' : 1}),'col': share_target.pk,'sharing_type': 'read'})
        elif sharing_type == 'edit':
            if my_class not in share_target_up.my_classes.all() and my_class not in share_target_up.owned_my_classes.all():
                share_target_up.editable_my_classes.add(my_class)
                share_target_up.save()
            if my_class in share_target_up.readonly_my_classes.all():
                share_target_up.readonly_my_classes.remove(my_class)
                share_target_up.save()
            return JsonResponse({'user-row' : render_to_string('teacher/sharing/modals/user-row.html',{'sharing_type': 'editor','shared_user' : share_target_up, 'is_owner' : 1}),'col': share_target.pk,'sharing_type': 'edit'})
        elif sharing_type == 'own':
            share_target_up.owned_my_classes.add(my_class)
            share_target_up.save()
            if my_class in share_target_up.readonly_my_classes.all():
                share_target_up.readonly_my_classes.remove(my_class)
                share_target_up.save()
            if my_class in share_target_up.editable_my_classes.all():
                share_target_up.editable_my_classes.remove(my_class)
                share_target_up.save()
            return JsonResponse({'user-row' : render_to_string('teacher/sharing/modals/user-row.html',{'sharing_type': 'coowner','shared_user' : share_target_up, 'is_owner' : 1}),'col': share_target.pk,'sharing_type': 'own'})

@login_required
def change_permission(request):
    userprofile = request.user.userprofile
    form = request.POST
    sharing_type = form.get('sharing_type','')
    pk = form.get('classpk','')
    my_class = get_object_or_404(Class,pk = pk)
    share_target_up = get_object_or_404(UserProfile,pk = form.get('pk',''))
    if share_target_up.my_classes.filter(pk = my_class.pk).exists()==False:#if target not an original owner...                                                                                   
        if my_class in userprofile.my_classes.all() or my_class in userprofile.owned_my_classes.all():#if owner....                                                                      
            if sharing_type == 'read':
                share_target_up.owned_my_classes.remove(my_class)
                share_target_up.editable_my_classes.remove(my_class)
                share_target_up.readonly_my_classes.add(my_class)
                share_target_up.save()
                return JsonResponse({'user-row' : render_to_string('teacher/sharing/modals/user-row.html',{'sharing_type': 'reader','shared_user' : share_target_up, 'is_owner' : 1}),'sharing_type': 'read'})
            elif sharing_type == 'edit':
                share_target_up.owned_my_classes.remove(my_class)
                share_target_up.editable_my_classes.add(my_class)
                share_target_up.readonly_my_classes.remove(my_class)
                share_target_up.save()
                return JsonResponse({'user-row' : render_to_string('teacher/sharing/modals/user-row.html',{'sharing_type': 'editor','shared_user' : share_target_up, 'is_owner' : 1}),'sharing_type': 'edit'})
            elif sharing_type == 'own':
                share_target_up.owned_my_classes.add(my_class)
                share_target_up.editable_my_classes.remove(my_class)
                share_target_up.readonly_my_classes.remove(my_class)
                share_target_up.save()
                return JsonResponse({'user-row' : render_to_string('teacher/sharing/modals/user-row.html',{'sharing_type': 'coowner','shared_user' : share_target_up, 'is_owner' : 1}),'sharing_type': 'own'})
            elif sharing_type == 'del':
                share_target_up.owned_my_classes.remove(my_class)
                share_target_up.editable_my_classes.remove(my_class)
                share_target_up.readonly_my_classes.remove(my_class)
                share_target_up.save()
                return JsonResponse({'sharing_type':'del'})

@login_required
def export_pset_to_group(request):
    userprofile = request.user.userprofile
    form = request.POST
    ppk = form.get('pset_pk','')
    pg_name = form.get('pg_name','')
    pset = get_object_or_404(ProblemSet,pk=ppk)
    my_class = pset.unit_object.unit.the_class
    sharing_type = get_permission_level(request,my_class)
    if sharing_type == 'none':
        raise Http404("Unauthorized.")
    problem_objects = pset.problem_objects.filter(isProblem=1).order_by('order')
    if problem_objects.count() > 0:
        pg = ProblemGroup(name = pg_name)
        pg.save()
        userprofile.problem_groups.add(pg)
        userprofile.save()
        for po in problem_objects:
            pg.add_to_end(po.problem)
        pg.save()
    return JsonResponse({})
