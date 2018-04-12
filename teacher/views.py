from django.shortcuts import render,render_to_response, get_object_or_404,redirect
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
import pytz

from randomtest.utils import newtexcode,compileasy,pointsum
from randomtest.models import QuestionType,ProblemGroup,Problem,NewTag,NewResponse

from teacher.models import Class,PublishedClass,Unit,ProblemSet,SlideGroup,UnitObject,ProblemObject,Slide,SlideObject,TextBlock,Proof,Theorem,ImageModel,ExampleProblem,Test
from teacher.models import PublishedUnit,PublishedProblemSet,PublishedSlideGroup,PublishedUnitObject,PublishedProblemObject,PublishedSlide,PublishedSlideObject,PublishedTest
from teacher.forms import NewProblemObjectMCForm, NewProblemObjectSAForm, NewProblemObjectPFForm,PointValueForm,SearchForm,AddProblemsForm,EditProblemProblemObjectForm,TheoremForm,ProofForm,TextBlockForm,ImageForm,LabelForm,NewExampleProblemMCForm,NewExampleProblemSAForm,NewExampleProblemPFForm,BlankPointValueForm,EditClassNameForm,EditUnitNameForm,EditProblemSetNameForm,EditTestNameForm,EditSlideGroupNameForm,EditSlideTitleForm
from groups.forms import GroupModelForm
from student.models import UserClass,UserUnit,UserProblemSet,UserUnitObject,UserSlides,Response


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
        pk=kwargs['pk']
        spk = kwargs['spk']
        slidegroup = get_object_or_404(PublishedSlideGroup, pk = spk)
        pub_class = get_object_or_404(PublishedClass, pk = pk)
        if userprofile not in pub_class.userprofiles.all():
            return HttpResponse('Unauthorized', status=401)
    if 'uspk' in kwargs:
        user_slides = get_object_or_404(UserSlides,pk=kwargs['uspk'])
        student_user = get_object_or_404(User,username=kwargs['username'])
        student_userprofile = student_user.userprofile
        slidegroup = user_slides.published_slides
        if student_user not in userprofile.students.all():
            return HttpResponse('Unauthorized', status=401)
        if user_slides.userunitobject.user_unit.user_class.userprofile != student_userprofile:
            return HttpResponse('Unauthorized', status=401)
        pub_class = user_slides.userunitobject.user_unit.user_class.published_class
    slides = slidegroup.slides.all()
    paginator = Paginator(slides,1)
    page = request.GET.get('page')
    try:
        rows=paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        rows = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        rows = paginator.page(paginator.num_pages)
    return render(request,'teacher/publishedclasses/slidesview.html',{'slides':slidegroup,'rows':rows,'class':pub_class,'nbar':'teacher'})

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
    if sharing_type == 'none':
        raise Http404("Unauthorized.")
    context = {}
    context['my_class'] = my_class
    filename = my_class.name+".tex"
    response = HttpResponse(render_to_string('teacher/editingtemplates/latexclassview.tex',context), content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response

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
    context = {}
    context['my_class'] = my_class
    context['unit'] = unit
    context['problemset'] = problemset
    context['tags'] = NewTag.objects.exclude(tag='root')
    context['nbar'] = 'teacher'
    context['sharing_type'] = sharing_type
    return render(request, 'teacher/editingtemplates/editproblemsetview.html',context)

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
    qt=request.GET.get('qt','')
    po=ProblemObject()
    if qt == 'sa':
        form = NewProblemObjectSAForm(instance=po)
    if qt == 'mc':
        form = NewProblemObjectMCForm(instance=po)
    if qt == 'pf':
        form = NewProblemObjectPFForm(instance=po)
    return HttpResponse(render_to_string('teacher/editingtemplates/modals/originalproblemform.html',{'form':form}))

@login_required
def loadcqtoriginalproblemform(request,**kwargs):
    qt=request.GET.get('qt','')
    pk=request.GET.get('pk','')
    po=get_object_or_404(ProblemObject,pk=pk)
    if po.isProblem==0:
        if qt == 'sa':
            form = NewProblemObjectSAForm(instance=po)
        if qt == 'mc':
            form = NewProblemObjectMCForm(instance=po)
        if qt == 'pf':
            form = NewProblemObjectPFForm(instance=po)
        return HttpResponse(render_to_string('teacher/editingtemplates/modals/originalproblemform.html',{'form':form}))
    form = EditProblemProblemObjectForm(instance=po)
    return HttpResponse(render_to_string('teacher/editingtemplates/modals/originalproblemform.html',{'form':form}))

@login_required
def loadoriginalexampleproblemform(request,**kwargs):
    qt=request.GET.get('qt','')
    ep=ExampleProblem()
    if qt == 'sa':
        form = NewExampleProblemSAForm(instance=ep)
    if qt == 'mc':
        form = NewExampleProblemMCForm(instance=ep)
    if qt == 'pf':
        form = NewExampleProblemPFForm(instance=ep)
    return HttpResponse(render_to_string('teacher/editingtemplates/modals/originalproblemform.html',{'form':form}))

@login_required
def loadcqtexampleproblemform(request,**kwargs):
    qt=request.GET.get('qt','')
    pk=request.GET.get('pk','')
    ep=get_object_or_404(ExampleProblem,pk=pk)
    if ep.isProblem==0:
        if qt == 'sa':
            form = NewExampleProblemSAForm(instance=ep)
        if qt == 'mc':
            form = NewExampleProblemMCForm(instance=ep)
        if qt == 'pf':
            form = NewExampleProblemPFForm(instance=ep)
        return HttpResponse(render_to_string('teacher/editingtemplates/modals/originalproblemform.html',{'form':form}))
    return HttpResponse('')

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
        if qt == "multiple choice":
            pform = NewProblemObjectMCForm(request.POST, instance=po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),prob.answers())
                compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type=qt)
                prob.author = request.user
                prob.point_value = problemset.default_point_value
                prob.order = problemset.problem_objects.count()+1
                prob.problemset = problemset
                prob.save()
                problemset.increment_version()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':problemset.problem_objects.count()}),'pk':prob.pk})
        elif qt == "short answer":
            pform = NewProblemObjectSAForm(request.POST, instance=po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type=qt)
                prob.author = request.user
                prob.point_value = problemset.default_point_value
                prob.order = problemset.problem_objects.count()+1
                prob.problemset = problemset
                prob.save()
                problemset.increment_version()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':problemset.problem_objects.count()}),'pk':prob.pk})
        elif qt == "proof":
            pform = NewProblemObjectPFForm(request.POST, instance=po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type=qt)
                prob.author = request.user
                prob.point_value = problemset.default_point_value
                prob.order = problemset.problem_objects.count()+1
                prob.problemset = problemset
                prob.save()
                problemset.increment_version()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':problemset.problem_objects.count()}),'pk':prob.pk})
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
    userprofile=request.user.userprofile
    po = get_object_or_404(ProblemObject,pk=request.POST.get('popk'))
    if po.test != None:
        if po.test.unit_object.unit.the_class not in userprofile.my_classes.all():
            raise Http404("Unauthorized.")
    elif po.problemset!=None:
        if po.problemset.unit_object.unit.the_class not in userprofile.my_classes.all():
            raise Http404("Unauthorized.")
    else:
        raise Http404("Problem does not belong to a valid class.")
    qt=po.question_type.question_type
    if po.isProblem == 0:
        if qt == 'short answer':
            form = NewProblemObjectSAForm(instance=po)
        if qt == 'multiple choice':
            form = NewProblemObjectMCForm(instance=po)
        if qt == 'proof':
            form = NewProblemObjectPFForm(instance=po)
        return JsonResponse({'form':render_to_string('teacher/editingtemplates/modals/originalproblemform.html',{'form':form}),'qt':qt,'qts':[1,1,1]})#qts: mc,sa,pf

    form = EditProblemProblemObjectForm(instance=po)
    if po.problem.question_type_new.question_type == 'multiple choice':
        qts=[1,0,1]
    if po.problem.question_type_new.question_type == 'short answer':
        qts=[0,1,1]
    if po.problem.question_type_new.question_type == 'multiple choice short answer':
        qts=[1,1,1]
    if po.problem.question_type_new.question_type == 'proof':
        qts=[0,0,1]
    return JsonResponse({'form':render_to_string('teacher/editingtemplates/modals/originalproblemform.html',{'form':form}),'qts':qts,'qt':qt})

@login_required
def savequestiontype(request,**kwargs):
    userprofile = request.user.userprofile
    form = request.POST
    qt = form.get('cqt-question-type','')
    po = get_object_or_404(ProblemObject,pk=form.get('problem_id',''))
    if po.test != None:
        if po.test.unit_object.unit.the_class not in userprofile.my_classes.all():
            raise Http404("Unauthorized.")
    elif po.problemset!=None:
        if po.problemset.unit_object.unit.the_class not in userprofile.my_classes.all():
            raise Http404("Unauthorized.")
    else:
        raise Http404("Problem does not belong to a valid class.")

    if po.isProblem == 0:
        if qt == "multiple choice":
            pform = NewProblemObjectMCForm(request.POST, instance = po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_' + str(prob.pk),prob.answers())
                compileasy(prob.problem_code,'originalproblem_' + str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type = qt)
                prob.author = request.user
                prob.save()
                prob.increment_version()
                return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':prob}),'qt':qt})
        elif qt == "short answer":
            pform = NewProblemObjectSAForm(request.POST, instance = po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_' + str(prob.pk),'')
                compileasy(prob.problem_code,'originalproblem_' + str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type = qt)
                prob.save()
                prob.increment_version()
                return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':prob}),'qt':qt})
        elif qt == "proof":
            pform = NewProblemObjectPFForm(request.POST, instance = po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_' + str(prob.pk),'')
                compileasy(prob.problem_code,'originalproblem_' + str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type = qt)
                prob.save()
                prob.increment_version()
                return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':prob}),'qt':qt})
    else:
        po.question_type = QuestionType.objects.get(question_type = qt)
        po.save()
        po.increment_version()
        return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':po}),'qt':qt})



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
        P = prob_group.problems.exclude(id__in = curr_problems.values('problem_id')).distinct()
    context = {}
    context['my_class'] = my_class
    context['unit'] = unit
    context['problemset'] = problemset
    context['nbar'] = 'teacher'
    context['rows'] = P
    context['prob_group'] = prob_group
    return render(request,'teacher/editingtemplates/review-problem-group.html',context)

###Test###
#    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/$', views.testeditview, name='testeditview'),
#    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/load-original-problem/$', views.testloadoriginalproblemform, name='test-load-original-problem'),
#    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/add-original-problem/$', views.testaddoriginalproblem, name='testadd-original-problem'),
#    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/find-num-probs-matching-tag/$', views.testnumprobsmatching, name='testnumprobsmatching'),
#    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/add-tagged-problems/$', views.testreviewmatchingproblems, name='testreviewmatchingproblems'),
#    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/review-problem-group/$', views.testreviewproblemgroup, name='testreviewproblemgroup'),
#    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/edit-point-value/(?P<pppk>\d+)/$', views.testupdate_point_value, name='testedit-point-value'),
#    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/edit-blank-value/(?P<pppk>\d+)/$', views.testupdate_blank_value, name='testedit-blank-value'),
#    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/edit-question-type/(?P<pppk>\d+)/$', views.testeditquestiontype, name='testedit-question-type'),
#    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/change-qt-original-problem/$', views.testloadcqtoriginalproblemform, name='testloadcqtoriginalproblemform'),

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
    context={}
    context['my_class'] = my_class
    context['unit'] = unit
    context['test'] = test
    context['tags'] = NewTag.objects.exclude(tag='root')
    context['nbar'] = 'teacher'
    context['sharing_type'] = sharing_type
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
    po = get_object_or_404(ProblemObject,pk = pk)
    if po.isProblem == 0:
        if qt == 'sa':
            form = NewProblemObjectSAForm(instance = po)
        if qt == 'mc':
            form = NewProblemObjectMCForm(instance = po)
        if qt == 'pf':
            form = NewProblemObjectPFForm(instance = po)
        return HttpResponse(render_to_string('teacher/editingtemplates/modals/originalproblemform.html',{'form':form}))
    form = EditProblemProblemObjectForm(instance = po)
    return HttpResponse(render_to_string('teacher/editingtemplates/modals/originalproblemform.html',{'form':form}))

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
        if qt == "multiple choice":
            pform = NewProblemObjectMCForm(request.POST, instance = po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_' + str(prob.pk),prob.answers())
                compileasy(prob.problem_code,'originalproblem_' + str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type = qt)
                prob.author = request.user
                prob.point_value = test.default_point_value
                prob.blank_point_value = test.default_blank_value
                prob.order = test.problem_objects.count()+1
                prob.test = test
                prob.save()
                test.increment_version()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':test.problem_objects.count()}),'pk':prob.pk})
        elif qt == "short answer":
            pform = NewProblemObjectSAForm(request.POST, instance = po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_' + str(prob.pk),'')
                compileasy(prob.problem_code,'originalproblem_' + str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type = qt)
                prob.author = request.user
                prob.point_value = test.default_point_value
                prob.blank_point_value = test.default_blank_value
                prob.order = test.problem_objects.count() + 1
                prob.test = test
                prob.save()
                test.increment_version()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':test.problem_objects.count()}),'pk':prob.pk})
        elif qt == "proof":
            pform = NewProblemObjectPFForm(request.POST, instance = po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_' + str(prob.pk),'')
                compileasy(prob.problem_code,'originalproblem_' + str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type = qt)
                prob.author = request.user
                prob.point_value = test.default_point_value
                prob.blank_point_value = test.default_blank_value
                prob.order = test.problem_objects.count() + 1
                prob.test = test
                prob.save()
                test.increment_version()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':test.problem_objects.count()}),'pk':prob.pk})
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
        P = prob_group.problems.exclude(id__in = curr_problems.values('problem_id')).distinct()
    if request.method == 'GET':
        form = request.GET
        prob_group = get_object_or_404(ProblemGroup,pk = form.get('problem-group',''))
        curr_problems = test.problem_objects.filter(isProblem = 1)
        P = prob_group.problems.exclude(id__in = curr_problems.values('problem_id')).distinct()
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
            tb = TextBlock(slide_object = s, text_code = textbl, text_display = "")
            tb.save()
            tb.text_display = newtexcode(textbl, 'textblock_' + str(tb.pk), "")
            tb.save()
            compileasy(tb.text_code,'textblock_' + str(tb.pk))
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
            th = Theorem(slide_object = s,theorem_code = thmbl, theorem_display = "",prefix = prefix,name = thmname)
            th.save()
            th.theorem_display = newtexcode(thmbl, 'theoremblock_'+str(th.pk), "")
            th.save()
            slide.top_order_number = slide.top_order_number +1
            slide.save()
            slide.increment_version()
            return JsonResponse({'theorem':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})
        if "addproof" in form:
            s = SlideObject(slide = slide,order = slide.top_order_number + 1)
            s.save()
            proofbl = form.get("codeproofblock","")
            prefix = form.get("proof-prefix","")
            pf = Proof(slide_object = s, proof_code = proofbl, proof_display = "",prefix = prefix)
            pf.save()
            pf.proof_display = newtexcode(proofbl, 'proofblock_'+str(pf.pk), "")
            pf.save()
            compileasy(pf.proof_code,'proofblock_'+str(pf.pk))#######Check
            slide.top_order_number = slide.top_order_number +1
            slide.save()
            slide.increment_version()
            return JsonResponse({'proof':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})
        if "addimage" in form:
            form = ImageForm(request.POST, request.FILES)
            if form.is_valid():
                s = SlideObject(slide = slide,order = slide.top_order_number + 1)
                s.save()
                m = ImageModel(slide_object = s,image = form.cleaned_data['image'])
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
                        ep = ExampleProblem(slide_object = s,isProblem = 1,problem = p,question_type = p.question_type_new,prefix=prefix)
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
                ep = ExampleProblem(slide_object = s)
                if qt == "multiple choice":
                    pform = NewExampleProblemMCForm(request.POST, instance = ep)
                    if pform.is_valid():
                        prob = pform.save()
                        prob.problem_display = newtexcode(prob.problem_code,'exampleproblem_'+str(prob.pk),prob.answers())
                        prob.prefix = prefix
                        compileasy(prob.problem_code,'exampleproblem_'+str(prob.pk))
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
    return JsonResponse({'pg-form':render_to_string('teacher/editingtemplates/example-problem-group.html',{'pg':request.user.userprofile.problem_groups.all()})})

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
    ep = ExampleProblem(slide_object = s, isProblem = 1,problem = p,question_type = p.question_type_new,prefix = prefix)
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
    userprofile=request.user.userprofile
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
        if ep.isProblem == 0:
            if qt == "multiple choice":
                pform = NewExampleProblemMCForm(request.POST, instance = ep)
                if pform.is_valid():
                    prob = pform.save()
                    prob.problem_display = newtexcode(prob.problem_code,'exampleproblem_' + str(prob.pk),prob.answers())
                    compileasy(prob.problem_code,'exampleproblem_' + str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type = qt)
                    prob.author = request.user
                    prob.save()
                    ep.increment_version()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/edit-slide/slideobjectbody.html',{'s':so}),'qt':qt,'sopk':so.pk})
            elif qt == "short answer":
                pform = NewExampleProblemSAForm(request.POST, instance = ep)
                if pform.is_valid():
                    prob = pform.save()
                    prob.problem_display = newtexcode(prob.problem_code,'exampleproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'exampleproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type = qt)
                    prob.save()
                    ep.increment_version()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/edit-slide/slideobjectbody.html',{'s':so}),'qt':qt,'sopk':so.pk})
            elif qt == "proof":
                pform = NewExampleProblemPFForm(request.POST, instance = ep)
                if pform.is_valid():
                    prob = pform.save()
                    prob.problem_display = newtexcode(prob.problem_code,'exampleproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'exampleproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type = qt)
                    prob.save()
                    ep.increment_version()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/edit-slide/slideobjectbody.html',{'s':so}),'qt':qt,'sopk':so.pk})
    qt=ep.question_type.question_type
    if qt == 'short answer':
        form = NewExampleProblemSAForm(instance=ep)
    if qt == 'multiple choice':
        form = NewExampleProblemMCForm(instance=ep)
    if qt == 'proof':
        form = NewExampleProblemPFForm(instance=ep)
    return JsonResponse({'form':render_to_string('teacher/editingtemplates/modals/originalproblemform.html',{'form':form}),'qt':qt})

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
        textblock.increment_version()
        return JsonResponse({'slide-code':render_to_string('teacher/editingtemplates/edit-slide/slideobjectbody.html',{'s':textblock.slide_object}),'sopk':textblock.slide_object.pk})

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
        theorem.increment_version()
        return JsonResponse({'slide-code':render_to_string('teacher/editingtemplates/edit-slide/slideobjectbody.html',{'s':theorem.slide_object}),'sopk':theorem.slide_object.pk})

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
        proof.increment_version()
        return JsonResponse({'slide-code':render_to_string('teacher/editingtemplates/edit-slide/slideobjectbody.html',{'s':proof.slide_object}),'sopk':proof.slide_object.pk})


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
def viewproblemgroup(request,pk):
    userprofile = request.user.userprofile
    prob_group = get_object_or_404(ProblemGroup,pk=pk)
    if prob_group not in userprofile.problem_groups.all():
        return HttpResponse('Unauthorized', status=401)
    if request.method=='POST':
        if request.POST.get("save"):
            form=request.POST
            P=prob_group.problems.all()
            remaining_problems = form.getlist("chk")
            for i in P:
                if i.label not in remaining_problems:
                    prob_group.problems.remove(i)
#        if request.POST.get("add-problems"):
#            form=request.POST
#            print(form)
    P = prob_group.problems.all()
    name = prob_group.name
    context = {}
    context['rows'] = P
    context['name'] = name
    context['nbar'] = 'teacher'
    context['pk'] = pk
    context['form'] = AddProblemsForm(userprofile=userprofile)
    template=loader.get_template('teacher/problemgroups/probgroupview.html')
    return HttpResponse(template.render(context,request))

@login_required
def fetchproblems(request,pk):
    userprofile = request.user.userprofile
    prob_group = get_object_or_404(ProblemGroup,pk=pk)
    if prob_group not in userprofile.problem_groups.all():
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
    desired_tag = form.get('desired_tag','')
    if desired_tag == 'Unspecified':
        problems = Problem.objects.filter(type_new__type=form.get('contest_type','')).filter(year__gte=year_low).filter(year__lte=year_high).filter(problem_number__gte=prob_num_low).filter(problem_number__lte=prob_num_high)
    else:
        problems = Problem.objects.filter(type_new__type=form.get('contest_type','')).filter(year__gte=year_low).filter(year__lte=year_high).filter(problem_number__gte=prob_num_low).filter(problem_number__lte=prob_num_high).filter(newtags__in=NewTag.objects.filter(tag__startswith=desired_tag)).distinct()
    problems = problems.exclude(pk__in=prob_group.problems.all())
    prob_list = list(problems)
    shuffle(prob_list)
    prob_list = prob_list[0:num_problems]
    prob_code = []
    base_num = prob_group.problems.count()
    for i in range(0,len(prob_list)):
        prob_group.problems.add(prob_list[i])
        prob_code.append(render_to_string('teacher/problemgroups/problemsnippet2.html',{'prob':prob_list[i],'forcount':base_num+i+1}))
    prob_group.save()
    data = {
                'prob_list': prob_code,
            }
    return JsonResponse(data)

#@login_required
#def deletegroup(request,pk):
#    pg = get_object_or_404(ProblemGroup, pk=pk)
#    userprofile = request.user.userprofile
#    if pg in userprofile.problem_groups.all():
#        if pg.is_shared==0:
#            pg.delete()
#        else:
#            userprofile.problem_groups.remove(pg)
#    return redirect('/teacher/problemgroups/')

@login_required
def deletegroup(request,pk):
    pg = get_object_or_404(ProblemGroup, pk=pk)
    userprofile = request.user.userprofile
    if pg in userprofile.problem_groups.all():
        pg.delete()
    return redirect('/teacher/problemgroups/')

@login_required
def removegroup(request,pk):
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
    return redirect('/teacher/problemgroups/')

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
