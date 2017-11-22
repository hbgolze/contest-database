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
from teacher.forms import NewProblemObjectMCForm, NewProblemObjectSAForm, NewProblemObjectPFForm,PointValueForm,SearchForm,AddProblemsForm,EditProblemProblemObjectForm,TheoremForm,ProofForm,TextBlockForm,ImageForm,LabelForm,NewExampleProblemMCForm,NewExampleProblemSAForm,NewExampleProblemPFForm,BlankPointValueForm
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
            return JsonResponse({"newrow":render_to_string("teacher/editingtemplates/editclassrow.html",{'cls':c})})
#reorder sections in post...
    context={}
    context['my_classes'] = userprofile.my_classes
    context['my_published_classes'] = userprofile.my_published_classes
    context['my_TA_classes'] = userprofile.my_TA_classes
    context['my_students'] = userprofile.students
    context['nbar'] = 'teacher'
    return render(request, 'teacher/teacherview.html',context)

@login_required
def publishview(request,pk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    p=my_class.publish(userprofile)
    return JsonResponse({'newrow':render_to_string('teacher/publishedclasses/publishedclassrow.html',{'cls':p})})

@login_required
def publishview2(request,pk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    p=PublishedClass(name=my_class.name,parent_class = my_class)
    p.save()
    class_points = 0
    class_prob_num = 0
    for u in my_class.units.all():
        new_unit = Unit(name=u.name,order=u.order)
        new_unit.save()
        p.units.add(new_unit)
        unit_points = 0
        unit_prob_num = 0
        num_problemsets = 0
        for uo in u.unit_objects.all():
            try:
                sg = uo.slidegroup
#            if uo.slidegroup:#####fix this
                new_unit_object = UnitObject(unit = new_unit,order = uo.order)
                new_unit_object.save()
                new_slide_group = SlideGroup(name = uo.slidegroup.name,num_slides = uo.slidegroup.slides.count(),unit_object = new_unit_object)
                new_slide_group.save()
                for s in uo.slidegroup.slides.all():
                    new_slide = Slide(title=s.title,order=s.order, slidegroup=new_slide_group,top_order_number=s.top_order_number)
                    new_slide.save()
                    for so in s.slide_objects.all():
                        if so.content_type == ContentType.objects.get(app_label = 'teacher', model = 'textblock'):
                            new_textblock = TextBlock(text_code = so.content_object.text_code,text_display="")
                            new_textblock.save()
                            new_textblock.text_display = newtexcode(so.content_object.text_code, 'textblock_'+str(new_textblock.pk), "")
                            new_textblock.save()
                            compileasy(new_textblock.text_code,'textblock_'+str(new_textblock.pk))
                            new_so=SlideObject(content_object=new_textblock,slide=new_slide,order=so.order)
                            new_so.save()
                        if so.content_type == ContentType.objects.get(app_label = 'teacher', model = 'proof'):
                            new_proof = Proof(prefix=so.content_object.prefix,proof_code = so.content_object.proof_code,proof_display="")
                            new_proof.save()
                            new_proof.proof_display = newtexcode(so.content_object.proof_code, 'proofblock_'+str(new_proof.pk), "")
                            new_proof.save()
                            compileasy(new_proof.proof_code,'proofblock_'+str(new_proof.pk))
                            new_so=SlideObject(content_object=new_proof,slide=new_slide,order=so.order)
                            new_so.save()
                        if so.content_type == ContentType.objects.get(app_label = 'teacher', model = 'theorem'):
                            new_theorem = Theorem(name=so.content_object.name,prefix=so.content_object.prefix,theorem_code = so.content_object.theorem_code,theorem_display="")
                            new_theorem.save()
                            new_theorem.theorem_display = newtexcode(so.content_object.theorem_code, 'theoremblock_'+str(new_theorem.pk), "")
                            new_theorem.save()
                            compileasy(new_theorem.theorem_code,'theoremblock_'+str(new_theorem.pk))
                            new_so=SlideObject(content_object=new_theorem,slide=new_slide,order=so.order)
                            new_so.save()
                        if so.content_type == ContentType.objects.get(app_label = 'teacher', model = 'exampleproblem'):
                            new_example = ExampleProblem(name=so.content_object.name,prefix=so.content_object.prefix,problem_code = so.content_object.problem_code,problem_display="",isProblem=so.content_object.isProblem, problem=so.content_object.problem,question_type=so.content_object.question_type,mc_answer = so.content_object.mc_answer,sa_answer = so.content_object.sa_answer,answer_A = so.content_object.answer_A,answer_B = so.content_object.answer_B,answer_C = so.content_object.answer_C,answer_D = so.content_object.answer_D,answer_E = so.content_object.answer_E,author=so.content_object.author)
                            new_example.save()
                            new_example.problem_display = newtexcode(so.content_object.problem_code, 'exampleproblem_'+str(new_example.pk), "")
                            new_example.save()
                            compileasy(new_example.problem_code,'exampleproblem_'+str(new_example.pk))
                            new_so=SlideObject(content_object=new_example,slide=new_slide,order=so.order)
                            new_so.save()
                        if so.content_type == ContentType.objects.get(app_label = 'teacher', model = 'imagemodel'):
                            new_image = ImageModel(image = so.content_object.image)
                            new_image.save()
                            new_so=SlideObject(content_object=new_image,slide=new_slide,order=so.order)
                            new_so.save()
            except SlideGroup.DoesNotExist:
                pset = uo.problemset
#            if uo.problemset:################
                num_problemsets += 1
                new_unit_object = UnitObject(unit = new_unit,order = uo.order)
                new_unit_object.save()
                new_problemset = ProblemSet(name = uo.problemset.name,default_point_value = uo.problemset.default_point_value,unit_object = new_unit_object)
                new_problemset.save()
                total_points=0
                for po in uo.problemset.problem_objects.all():
                    new_po = ProblemObject(order = po.order,point_value=po.point_value,problem_code = po.problem_code,problem_display="",isProblem=po.isProblem, problem=po.problem,question_type=po.question_type,mc_answer = po.mc_answer,sa_answer = po.sa_answer,answer_A = po.answer_A,answer_B = po.answer_B,answer_C = po.answer_C,answer_D = po.answer_D,answer_E = po.answer_E,author=po.author)
                    new_po.save()
                    if new_po.isProblem == 0:
                        if new_po.question_type.question_type =='multiple choice':
                            new_po.problem_display = newtexcode(po.problem_code, 'originalproblem_'+str(new_po.pk), new_po.answers())
                        else:
                            new_po.problem_display = newtexcode(po.problem_code, 'originalproblem_'+str(new_po.pk), "")
                        new_po.save()
                        compileasy(new_po.problem_code,'originalproblem_'+str(new_po.pk))
                    new_problemset.problem_objects.add(new_po)
                    total_points += po.point_value
                new_problemset.total_points = total_points
                new_problemset.num_problems = new_problemset.problem_objects.count()
                new_problemset.save()
                unit_points += total_points
                unit_prob_num += new_problemset.num_problems
        new_unit.total_points = unit_points
        new_unit.num_problems = unit_prob_num
        new_unit.num_problemsets = num_problemsets
        new_unit.save()
        class_points += unit_points
        class_prob_num += new_unit.num_problems
    p.total_points = class_points
    p.num_problems = class_prob_num
    p.save()
    userprofile.my_published_classes.add(p)
    userprofile.save()
    return JsonResponse({'newrow':render_to_string('teacher/publishedclasses/publishedclassrow.html',{'cls':p})})

@login_required
def rosterview(request,pk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(PublishedClass,pk=pk)
    if userprofile.my_published_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    student_classes = my_class.userclass_set.all()
    return render(request,'teacher/publishedclasses/rosterview.html',{'student_classes':student_classes,'my_class':my_class,'nbar':'teacher'})

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
    template_name = 'teacher/publishedclass/load_sol.html'

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
    po = resp.problem_object
    if po.isProblem:
        if po.question_type == "multiple choice":
            problem_display = po.problem.display_mc_problem_text
        else:
            problem_display = po.problem.display_problem_text
        context['readable_label'] = po.problem.readable_label
    else:
        problem_display = po.problem.problem_display
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
    return render(request,'teacher/publishedclasses/slidesview.html',{'slides':slidegroup,'rows':rows,'class':pub_class})

def teacherproblemsetview(request,**kwargs):
    context={}
    my_class = get_object_or_404(PublishedClass, pk = kwargs['pk'])
    userprofile=request.user.userprofile
    problemset = get_object_or_404(PublishedProblemSet, pk = kwargs['pspk'])##
    if my_class not in userprofile.my_published_classes.all():
        raise Http404("Unauthorized.")
    if problemset.unit_object.unit not in my_class.pub_units.all():##
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
    if test.unit_object.unit not in my_class.pub_units.all():##
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
#        for unit in my_class.pub_units.all():
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
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    if request.method == "POST":
        form=request.POST
        if 'save' in form:
            U=list(my_class.units.all())
            U=sorted(U,key=lambda x:x.order)
            unit_inputs = form.getlist('unitinput')
            for u in U:
                if 'unit_'+str(u.pk) not in unit_inputs:
                    u.delete()
            for i in range(0,len(unit_inputs)):
                u = my_class.units.get(pk=unit_inputs[i].split('_')[1])
                u.order = i+1
                u.save()
    context={}
    context['my_class'] = my_class
    context['nbar'] = 'teacher'
    return render(request, 'teacher/editingtemplates/editclassview.html',context)


@login_required
def newunitview(request,pk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    if request.method == "POST":
        form=request.POST
        u=Unit(name=form.get("unit-name",""),order=my_class.units.count()+1)
        u.save()
        my_class.units.add(u)
        my_class.save()
        return HttpResponse(render_to_string('teacher/editingtemplates/unitsnippet.html',{'unit':u,'forcount':my_class.units.count()}))
    return HttpResponse('')

@login_required
def uniteditview(request,pk,upk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    if userprofile.my_classes.filter(pk = pk).exists() == False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.units.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")

    if request.method == "POST":
        form = request.POST
        if "addslides" in form:
            u = UnitObject(unit = unit,order = unit.unit_objects.count()+1)
            u.save()
            s = SlideGroup(name = form.get("slides-name",""),unit_object = u)
            s.save()
        if "addproblemset" in form:
            u = UnitObject(unit = unit,order = unit.unit_objects.count()+1)
            u.save()
            p = ProblemSet(name = form.get("problemset-name",""),default_point_value = form.get("problemset-default_point_value",""),unit_object = u)
            p.save()
        if 'save' in form:
            unit_objs = list(unit.unit_objects.all())
            unit_objs = sorted(unit_objs,key = lambda x:x.order)###
            unit_obj_inputs = form.getlist('unitobjectinput')
            for u in unit_objs:
                if 'unitobject_'+str(u.pk) not in unit_obj_inputs:
                    u.delete()
            for i in range(0,len(unit_obj_inputs)):
                u = unit.unit_objects.get(pk = unit_obj_inputs[i].split('_')[1])
                u.order = i+1
                u.save()
    context = {}
    context['my_class'] = my_class
    context['unit'] = unit
    context['nbar'] = 'teacher'
    context['minuterange'] = [5*i for i in range(0,12)]
    context['default_hours'] = 1
    return render(request, 'teacher/editingtemplates/editunitview.html',context)

@login_required
def newproblemsetview(request,pk,upk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.units.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    if request.method == "POST":
        form=request.POST
        u=UnitObject(unit=unit,order=unit.unit_objects.count()+1)
        u.save()
        p=ProblemSet(name=form.get("problemset-name",""),default_point_value=form.get("problemset-default_point_value",""),unit_object = u)
        p.save()
        return HttpResponse(render_to_string('teacher/editingtemplates/unitobjectsnippet.html',{'unitobj':u,'forcount':unit.unit_objects.count()},request=request))
    return HttpResponse('')

@login_required
def newtestview(request,pk,upk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.units.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    if request.method == "POST":
        form=request.POST
        u=UnitObject(unit=unit,order=unit.unit_objects.count()+1)
        u.save()
        minutes = request.POST.get('minutes')
        hours = request.POST.get('hours')
        time_limit = time(hour=int(hours),minute=int(minutes))
        t=Test(name=form.get("test-name",""),default_point_value=form.get("test-default_point_value",""),default_blank_value = form.get("test-default_blank_value",""),unit_object = u,time_limit = time_limit)
        t.save()
        return HttpResponse(render_to_string('teacher/editingtemplates/unitobjectsnippet.html',{'unitobj':u,'forcount':unit.unit_objects.count()},request=request))
    return HttpResponse('')

@login_required
def newslidesview(request,pk,upk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.units.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    if request.method == "POST":
        form=request.POST
        u=UnitObject(unit=unit,order=unit.unit_objects.count()+1)
        u.save()
        s=SlideGroup(name=form.get("slides-name",""),unit_object = u)
        s.save()
        return HttpResponse(render_to_string('teacher/editingtemplates/unitobjectsnippet.html',{'unitobj':u,'forcount':unit.unit_objects.count()}))
    return HttpResponse('')


@login_required
def problemseteditview(request,pk,upk,ppk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.units.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk=ppk)
    if unit.unit_objects.filter(problemset__isnull=False).filter(problemset__pk=problemset.pk).exists()==False:
        raise Http404("No such problem set in this unit.")
    if request.method == "POST":
        form=request.POST
        if "addoriginalproblem" in form:###############
            qt = form.get('question-type','')
            po=ProblemObject()
            if qt == "multiple choice":
                pform=NewProblemObjectMCForm(request.POST, instance=po)
                if pform.is_valid():
                    prob=pform.save()
                    prob.problem_display=newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),prob.answers())
                    compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type=qt)
                    prob.author = request.user
                    prob.point_value = problemset.default_point_value
                    prob.order = problemset.problem_objects.count()+1
                    prob.save()
                    problemset.problem_objects.add(prob)
                    problemset.save()
            elif qt == "short answer":
                pform=NewProblemObjectSAForm(request.POST, instance=po)
                if pform.is_valid():
                    prob=pform.save()
                    prob.problem_display=newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type=qt)
                    prob.author = request.user
                    prob.point_value = problemset.default_point_value
                    prob.order = problemset.problem_objects.count()+1
                    prob.save()
                    problemset.problem_objects.add(prob)
                    problemset.save()
            elif qt == "proof":
                pform=NewProblemObjectPFForm(request.POST, instance=po)
                if pform.is_valid():
                    prob=pform.save()
                    prob.problem_display=newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type=qt)
                    prob.author = request.user
                    prob.point_value = problemset.default_point_value
                    prob.order = problemset.problem_objects.count()+1
                    prob.save()
                    problemset.problem_objects.add(prob)
                    problemset.save()
                    
        if 'save' in form:
            prob_objs=list(problemset.problem_objects.all())
            prob_objs=sorted(prob_objs,key=lambda x:x.order)###
            prob_obj_inputs = form.getlist('problemobjectinput')#could be an issue if no units
            for p in prob_objs:
                if 'problemobject_'+str(p.pk) not in prob_obj_inputs:
                    p.delete()
            for i in range(0,len(prob_obj_inputs)):
                p = problemset.problem_objects.get(pk=prob_obj_inputs[i].split('_')[1])
                p.order = i+1
                p.save()
    context={}
    context['my_class'] = my_class
    context['unit'] = unit
    context['problemset'] = problemset
    context['tags'] = NewTag.objects.exclude(tag='root')
    context['nbar'] = 'teacher'
    return render(request, 'teacher/editingtemplates/editproblemsetview.html',context)

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
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.units.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk=ppk)
    if unit.unit_objects.filter(problemset__isnull=False).filter(problemset__pk=problemset.pk).exists()==False:
        raise Http404("No such problem set in this unit.")
    if request.method == "POST":
        form=request.POST
        qt = form.get('question-type','')
        po=ProblemObject()
        if qt == "multiple choice":
            pform=NewProblemObjectMCForm(request.POST, instance=po)
            if pform.is_valid():
                prob=pform.save()
                prob.problem_display=newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),prob.answers())
                compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type=qt)
                prob.author = request.user
                prob.point_value = problemset.default_point_value
                prob.order = problemset.problem_objects.count()+1
                prob.save()
                problemset.problem_objects.add(prob)
                problemset.save()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':problemset.problem_objects.count()}),'pk':prob.pk})
        elif qt == "short answer":
            pform=NewProblemObjectSAForm(request.POST, instance=po)
            if pform.is_valid():
                prob=pform.save()
                prob.problem_display=newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type=qt)
                prob.author = request.user
                prob.point_value = problemset.default_point_value
                prob.order = problemset.problem_objects.count()+1
                prob.save()
                problemset.problem_objects.add(prob)
                problemset.save()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':problemset.problem_objects.count()}),'pk':prob.pk})
        elif qt == "proof":
            pform=NewProblemObjectPFForm(request.POST, instance=po)
            if pform.is_valid():
                prob=pform.save()
                prob.problem_display=newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type=qt)
                prob.author = request.user
                prob.point_value = problemset.default_point_value
                prob.order = problemset.problem_objects.count()+1
                prob.save()
                problemset.problem_objects.add(prob)
                problemset.save()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':problemset.problem_objects.count()}),'pk':prob.pk})
    return JsonResponse({'problem_text':'','pk':'0'})

@login_required
def update_point_value(request,pk,upk,ppk,pppk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.units.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk=ppk)
    if unit.unit_objects.filter(problemset__isnull=False).filter(problemset__pk=problemset.pk).exists()==False:
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
            return JsonResponse(data)
    form = PointValueForm(instance=po)
    return render(request,'teacher/editingtemplates/editpointvalueform.html',{'form':form,'pk':pk,'upk':upk,'ppk':ppk,'pppk':pppk})

@login_required
def editquestiontype(request,pk,upk,ppk,pppk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.units.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk=ppk)
    if unit.unit_objects.filter(problemset__isnull=False).filter(problemset__pk=problemset.pk).exists()==False:
        raise Http404("No such problem set in this unit.")
    po = get_object_or_404(ProblemObject,pk=pppk)
    if request.method == "POST":
        form=request.POST
        qt = form.get('cqt-question-type','')
        if po.isProblem == 0:
            if qt == "multiple choice":
                pform=NewProblemObjectMCForm(request.POST, instance=po)
                if pform.is_valid():
                    prob=pform.save()
                    prob.problem_display=newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),prob.answers())
                    compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type=qt)
                    prob.author = request.user
                    prob.save()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':prob}),'qt':qt})
            elif qt == "short answer":
                pform=NewProblemObjectSAForm(request.POST, instance=po)
                if pform.is_valid():
                    prob=pform.save()
                    prob.problem_display=newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type=qt)
                    prob.save()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':prob}),'qt':qt})
            elif qt == "proof":
                pform=NewProblemObjectPFForm(request.POST, instance=po)
                if pform.is_valid():
                    prob=pform.save()
                    prob.problem_display=newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type=qt)
                    prob.save()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':prob}),'qt':qt})
        else:
            po.question_type=QuestionType.objects.get(question_type=qt)
            po.save()
            return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':po}),'qt':qt})
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
def numprobsmatching(request,pk,upk,ppk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.units.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk=ppk)
    if unit.unit_objects.filter(problemset__isnull=False).filter(problemset__pk=problemset.pk).exists()==False:
        raise Http404("No such problem set in this unit.")
    form = request.GET
    typ = form.get('contest-type','')
    desired_tag = form.get('contest-tags','')
    curr_problems = problemset.problem_objects.filter(isProblem=1)
    P=Problem.objects.filter(type_new__type=typ).filter(newtags__in=NewTag.objects.filter(tag__startswith=desired_tag)).exclude(id__in=curr_problems.values('problem_id')).distinct()####check this once contest problems are in a problem set.
    return JsonResponse({'num':str(P.count())})

@login_required
def reviewmatchingproblems(request,pk,upk,ppk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.units.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk=ppk)
    if unit.unit_objects.filter(problemset__isnull=False).filter(problemset__pk=problemset.pk).exists()==False:
        raise Http404("No such problem set in this unit.")
    P=[]
    desired_tag = ''
    if request.method == 'POST':
        form=request.POST
        if 'add-selected-problems' in form:
            checked=form.getlist("chk")
            top = problemset.problem_objects.count()
            if len(checked)>0:
                for i in range(0,len(checked)):
                    p=Problem.objects.get(label=checked[i])
                    po = ProblemObject(order=top+i+1,point_value = problemset.default_point_value,isProblem=1,problem=p,question_type = p.question_type_new)
                    po.save()
                    problemset.problem_objects.add(po)
                    problemset.save()
                return redirect('../')
            return redirect('../')
        typ = form.get('contest-type','')
        desired_tag = form.get('contest-tags','')
        curr_problems = problemset.problem_objects.filter(isProblem=1)
        P=Problem.objects.filter(type_new__type=typ).filter(newtags__in=NewTag.objects.filter(tag__startswith=desired_tag)).exclude(id__in=curr_problems.values('problem_id')).distinct().order_by("problem_number")
    context={}
    context['my_class'] = my_class
    context['unit'] = unit
    context['problemset'] = problemset
    context['nbar'] = 'teacher'
    context['rows'] = P
    context['tag'] = desired_tag
    return render(request,'teacher/editingtemplates/add-tagged-problems.html',context)

@login_required
def reviewproblemgroup(request,pk,upk,ppk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.units.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    problemset = get_object_or_404(ProblemSet,pk=ppk)
    if unit.unit_objects.filter(problemset__isnull=False).filter(problemset__pk=problemset.pk).exists()==False:
        raise Http404("No such problem set in this unit.")
    P=[]
    desired_tag = ''
    if request.method == 'POST':
        form=request.POST
        if 'add-selected-problems' in form:
            checked=form.getlist("chk")
            top = problemset.problem_objects.count()
            if len(checked)>0:
                for i in range(0,len(checked)):
                    p=Problem.objects.get(label=checked[i])
                    po = ProblemObject(order=top+i+1,point_value = problemset.default_point_value,isProblem=1,problem=p,question_type = p.question_type_new)
                    po.save()
                    problemset.problem_objects.add(po)
                    problemset.save()
                return redirect('../')
            return redirect('../')
        prob_group = get_object_or_404(ProblemGroup,pk=form.get('problem-group',''))
        curr_problems = problemset.problem_objects.filter(isProblem=1)
        P=prob_group.problems.exclude(id__in=curr_problems.values('problem_id')).distinct()
    context={}
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
    if userprofile.my_classes.filter(pk = pk).exists() == False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.units.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    test = get_object_or_404(Test,pk = tpk)
    if unit.unit_objects.filter(test__isnull = False).filter(test__pk = test.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
    if request.method == "POST":
        form = request.POST
        if "addoriginalproblem" in form:###############
            qt = form.get('question-type','')
            po = ProblemObject()
            if qt == "multiple choice":
                pform = NewProblemObjectMCForm(request.POST, instance = po)
                if pform.is_valid():
                    prob = pform.save()
                    prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),prob.answers())
                    compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type = qt)
                    prob.author = request.user
                    prob.point_value = test.default_point_value
                    prob.blank_point_value = test.default_blank_value
                    prob.order = test.problem_objects.count() + 1
                    prob.test = test
                    prob.save()
            elif qt == "short answer":
                pform = NewProblemObjectSAForm(request.POST, instance = po)
                if pform.is_valid():
                    prob = pform.save()
                    prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type = qt)
                    prob.author = request.user
                    prob.blank_point_value = test.default_blank_value
                    prob.order = test.problem_objects.count() + 1
                    prob.test = test
                    prob.save()
            elif qt == "proof":
                pform = NewProblemObjectPFForm(request.POST, instance = po)
                if pform.is_valid():
                    prob = pform.save()
                    prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type = qt)
                    prob.author = request.user
                    prob.blank_point_value = test.default_blank_value
                    prob.order = test.problem_objects.count() + 1
                    prob.test = test
                    prob.save()
                    
        if 'save' in form:
            prob_objs = list(test.problem_objects.all())
            prob_objs = sorted(prob_objs,key = lambda x:x.order)###
            prob_obj_inputs = form.getlist('problemobjectinput')#could be an issue if no units
            for p in prob_objs:
                if 'problemobject_'+str(p.pk) not in prob_obj_inputs:
                    p.delete()
            for i in range(0,len(prob_obj_inputs)):
                p = test.problem_objects.get(pk = prob_obj_inputs[i].split('_')[1])
                p.order = i+1
                p.save()
    context={}
    context['my_class'] = my_class
    context['unit'] = unit
    context['test'] = test
    context['tags'] = NewTag.objects.exclude(tag='root')
    context['nbar'] = 'teacher'
    return render(request, 'teacher/editingtemplates/edittestview.html',context)

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
    if userprofile.my_classes.filter(pk = pk).exists() == False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.units.filter(pk = upk).exists == False:
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
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),prob.answers())
                compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type = qt)
                prob.author = request.user
                prob.point_value = test.default_point_value
                prob.blank_point_value = test.default_blank_value
                prob.order = test.problem_objects.count()+1
                prob.test = test
                prob.save()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':test.problem_objects.count()}),'pk':prob.pk})
        elif qt == "short answer":
            pform = NewProblemObjectSAForm(request.POST, instance = po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type = qt)
                prob.author = request.user
                prob.point_value = test.default_point_value
                prob.blank_point_value = test.default_blank_value
                prob.order = test.problem_objects.count() + 1
                prob.test = test
                prob.save()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':test.problem_objects.count()}),'pk':prob.pk})
        elif qt == "proof":
            pform = NewProblemObjectPFForm(request.POST, instance = po)
            if pform.is_valid():
                prob = pform.save()
                prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                prob.question_type = QuestionType.objects.get(question_type = qt)
                prob.author = request.user
                prob.point_value = test.default_point_value
                prob.blank_point_value = test.default_blank_value
                prob.order = test.problem_objects.count() + 1
                prob.test = test
                prob.save()
                return JsonResponse({'problem_text':render_to_string('teacher/editingtemplates/problemobjectsnippet.html',{'probobj':prob,'forcount':test.problem_objects.count()}),'pk':prob.pk})
    return JsonResponse({'problem_text':'','pk':'0'})

@login_required
def testupdate_point_value(request,pk,upk,ppk,pppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    if userprofile.my_classes.filter(pk = pk).exists() == False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.units.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    test = get_object_or_404(Test,pk = ppk)
    if unit.unit_objects.filter(test__isnull = False).filter(test__pk = test.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
    po = get_object_or_404(ProblemObject,pk = pppk)
    if request.method == 'POST':
        form = PointValueForm(request.POST,instance=po)
        if form.is_valid():
            form.save()
            data = {
                'pk': pppk,
                'point_value':form.instance.point_value,
            }
            return JsonResponse(data)
    form = PointValueForm(instance = po)
    return render(request,'teacher/editingtemplates/editpointvalueform.html',{'form':form,'pk':pk,'upk':upk,'ppk':ppk,'pppk':pppk})

@login_required
def testupdate_blank_value(request,pk,upk,ppk,pppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    if userprofile.my_classes.filter(pk = pk).exists() == False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.units.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    test = get_object_or_404(Test,pk = ppk)
    if unit.unit_objects.filter(test__isnull = False).filter(test__pk = test.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
    po = get_object_or_404(ProblemObject,pk = pppk)
    if request.method == 'POST':
        form = BlankPointValueForm(request.POST,instance=po)
        if form.is_valid():
            form.save()
            data = {
                'pk': pppk,
                'blank_point_value':form.instance.blank_point_value,
            }
            return JsonResponse(data)
    form = BlankPointValueForm(instance = po)
    return render(request,'teacher/editingtemplates/editpointvalueform.html',{'form':form,'pk':pk,'upk':upk,'ppk':ppk,'pppk':pppk})

@login_required
def testeditquestiontype(request,pk,upk,ppk,pppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    if userprofile.my_classes.filter(pk = pk).exists() == False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.units.filter(pk = upk).exists == False:
        raise Http404("No such unit in this class.")
    test = get_object_or_404(Test,pk = ppk)
    if unit.unit_objects.filter(test__isnull = False).filter(test__pk = test.pk).exists() == False:
        raise Http404("No such problem set in this unit.")
    po = get_object_or_404(ProblemObject,pk = pppk)
    if request.method == "POST":
        form = request.POST
        qt = form.get('cqt-question-type','')
        if po.isProblem == 0:
            if qt == "multiple choice":
                pform = NewProblemObjectMCForm(request.POST, instance=po)
                if pform.is_valid():
                    prob=pform.save()
                    prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),prob.answers())
                    compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type = qt)
                    prob.author = request.user
                    prob.save()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':prob}),'qt':qt})
            elif qt == "short answer":
                pform = NewProblemObjectSAForm(request.POST, instance=po)
                if pform.is_valid():
                    prob = pform.save()
                    prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type = qt)
                    prob.author = request.user
                    prob.save()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':prob}),'qt':qt})
            elif qt == "proof":
                pform = NewProblemObjectPFForm(request.POST, instance=po)
                if pform.is_valid():
                    prob = pform.save()
                    prob.problem_display = newtexcode(prob.problem_code,'originalproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'originalproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type=qt)
                    prob.author = request.user
                    prob.save()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':prob}),'qt':qt})
        else:
            po.question_type = QuestionType.objects.get(question_type = qt)
            po.save()
            return JsonResponse({'prob':render_to_string('teacher/editingtemplates/problemsnippet.html',{'probobj':po}),'qt':qt})
    qt=po.question_type.question_type
    if po.isProblem == 0:
        if qt == 'short answer':
            form = NewProblemObjectSAForm(instance = po)
        if qt == 'multiple choice':
            form = NewProblemObjectMCForm(instance = po)
        if qt == 'proof':
            form = NewProblemObjectPFForm(instance = po)
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
def testnumprobsmatching(request,pk,upk,ppk):
    userprofile = request.user.userprofile
    my_class = get_object_or_404(Class,pk = pk)
    if userprofile.my_classes.filter(pk = pk).exists() == False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.units.filter(pk = upk).exists == False:
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
    if userprofile.my_classes.filter(pk = pk).exists() == False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.units.filter(pk = upk).exists == False:
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
            if len(checked)>0:
                for i in range(0,len(checked)):
                    p = Problem.objects.get(label=checked[i])
                    po = ProblemObject(order=top+i+1,point_value = test.default_point_value,blank_point_value = test.default_blank_value, test = test, isProblem=1,problem=p,question_type = p.question_type_new)
                    po.save()
                return redirect('../')
            return redirect('../')
        typ = form.get('contest-type','')
        desired_tag = form.get('contest-tags','')
        curr_problems = test.problem_objects.filter(isProblem=1)
        P = Problem.objects.filter(type_new__type=typ).filter(newtags__in=NewTag.objects.filter(tag__startswith=desired_tag)).exclude(id__in=curr_problems.values('problem_id')).distinct().order_by("problem_number")
    context={}
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
    if userprofile.my_classes.filter(pk = pk).exists() == False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk = upk)
    if my_class.units.filter(pk = upk).exists == False:
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
                    po = ProblemObject(order=top+i+1,point_value = test.default_point_value,blank_point_value = test.default_blank_value,isProblem=1,problem=p,question_type = p.question_type_new,test=test)
                    po.save()
                return redirect('../')
            return redirect('../')
        prob_group = get_object_or_404(ProblemGroup,pk=form.get('problem-group',''))
        curr_problems = test.problem_objects.filter(isProblem=1)
        P = prob_group.problems.exclude(id__in=curr_problems.values('problem_id')).distinct()
    context={}
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
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.units.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    slidegroup = get_object_or_404(SlideGroup,pk=spk)
    if unit.unit_objects.filter(slidegroup__isnull=False).filter(slidegroup__pk=slidegroup.pk).exists()==False:
        raise Http404("No such slides in this unit.")
    if request.method == "POST":
        form=request.POST
        if 'save' in form:#######
            slides=list(slidegroup.slides.all())
            slides=sorted(slides,key=lambda x:x.order)
            slide_inputs = form.getlist('slideinput')
            for s in slides:
                if 'slide_'+str(s.pk) not in slide_inputs:
                    for so in s.slide_objects.all():
                        so.content_object.delete()
                    s.delete()
            for i in range(0,len(slide_inputs)):
                s = slidegroup.slides.get(pk=slide_inputs[i].split('_')[1])###better way to do this? (i.e., get the query set first)
                s.order = i+1
                s.save()
            return JsonResponse({'slidelist':render_to_string('teacher/editingtemplates/editslides/slidelist.html',{'slides' :slidegroup})})
    context={}
    context['my_class'] = my_class
    context['unit'] = unit
    context['slides'] = slidegroup
    context['nbar'] = 'teacher'
    return render(request,'teacher/editingtemplates/editslidesview.html',context)

    
@login_required
def newslideview(request,pk,upk,spk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.units.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    slidegroup = get_object_or_404(SlideGroup,pk=spk)
    if unit.unit_objects.filter(slidegroup__isnull=False).filter(slidegroup__pk=slidegroup.pk).exists()==False:
        raise Http404("No such slides in this unit.")
    if request.method == "POST":
        form=request.POST
        s=Slide(title=form.get("slide-title",""),order=slidegroup.slides.count()+1,slidegroup=slidegroup)
        s.save()
        return JsonResponse({'slide-body':render_to_string('teacher/editingtemplates/editslides/slidebody.html',{'slide':s,'forcount':s.order})})
#    return HttpResponse('')

def editslideview(request,pk,upk,spk,sspk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.units.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    slidegroup = get_object_or_404(SlideGroup,pk=spk)
    if unit.unit_objects.filter(slidegroup__isnull=False).filter(slidegroup__pk=slidegroup.pk).exists()==False:
        raise Http404("No such slides in this unit.")
    slide = get_object_or_404(Slide,pk=sspk)
    if slidegroup.slides.filter(pk=slide.pk).exists()==False:
        raise Http404("No such slide in the slide group.")

    if request.method == "POST":
        form=request.POST
        if "addtextblock" in form:
            textbl = form.get("codetextblock","")
            tb = TextBlock(text_code = textbl, text_display="")
            tb.save()
            tb.text_display = newtexcode(textbl, 'textblock_'+str(tb.pk), "")
            tb.save()
            compileasy(tb.text_code,'textblock_'+str(tb.pk))
            s=SlideObject(content_object=tb,slide=slide,order=slide.top_order_number+1)
            s.save()
            slide.top_order_number = slide.top_order_number +1
            slide.save()
            return JsonResponse({'textblock':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})
        if "addtheorem" in form:
            thmbl = form.get("codetheoremblock","")
            prefix = form.get("theorem-prefix","")
            thmname = form.get("theorem-name","")
            th = Theorem(theorem_code = thmbl, theorem_display="",prefix=prefix,name=thmname)
            th.save()
            th.theorem_display = newtexcode(thmbl, 'theoremblock_'+str(th.pk), "")
            th.save()
            s=SlideObject(content_object=th,slide=slide,order=slide.top_order_number+1)
            s.save()
            slide.top_order_number = slide.top_order_number +1
            slide.save()
            return JsonResponse({'theorem':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})
        if "addproof" in form:
            proofbl = form.get("codeproofblock","")
            prefix = form.get("proof-prefix","")
            pf = Proof(proof_code = proofbl, proof_display="",prefix=prefix)
            pf.save()
            pf.proof_display = newtexcode(proofbl, 'proofblock_'+str(pf.pk), "")
            pf.save()
            compileasy(pf.proof_code,'proofblock_'+str(pf.pk))#######Check
            s=SlideObject(content_object=pf,slide=slide,order=slide.top_order_number+1)
            s.save()
            slide.top_order_number = slide.top_order_number +1
            slide.save()
            return JsonResponse({'proof':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})
        if "addimage" in form:
            form = ImageForm(request.POST, request.FILES)
            if form.is_valid():
                m = ImageModel(image=form.cleaned_data['image'])
                m.save()
                s = SlideObject(content_object=m,slide=slide,order=slide.top_order_number+1)
                s.save()
                slide.top_order_number = slide.top_order_number +1
                slide.save()
                return JsonResponse({'image':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})
        if "addproblem" in form:
            prefix = form.get("example-prefix","")
            source = form.get("problem-source","")
            if source == "bylabel":
                problem_label = form.get("problem-label","")
                if Problem.objects.filter(label = problem_label).exists():
                    p = Problem.objects.get(label = problem_label)
                    if p.type_new in userprofile.user_type_new.allowed_types.all():
                        ep = ExampleProblem(isProblem=1,problem=p,question_type=p.question_type_new,prefix=prefix)
                        ep.save()
                        s = SlideObject(content_object=ep,slide=slide,order=slide.top_order_number+1)
                        s.save()
                        slide.top_order_number = slide.top_order_number + 1
                        slide.save()
                        return JsonResponse({'example':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})
                    else:
                        return JsonResponse({'error-msg': "No such problem with label"})
                else:
                    return JsonResponse({'error-msg': "No such problem with label"})
#            elif source == "bygroup":
#                pass
            elif source == "original":
                qt = form.get('question-type','')
                s = SlideObject()
                ep = ExampleProblem()
                if qt == "multiple choice":
                    pform = NewExampleProblemMCForm(request.POST, instance=ep)
                    if pform.is_valid():
                        prob=pform.save()
                        prob.problem_display=newtexcode(prob.problem_code,'exampleproblem_'+str(prob.pk),prob.answers())
                        prob.prefix = prefix
                        compileasy(prob.problem_code,'exampleproblem_'+str(prob.pk))
                        prob.question_type = QuestionType.objects.get(question_type=qt)
                        prob.author = request.user
                        prob.save()
                        s = SlideObject(content_object=ep,slide=slide,order=slide.top_order_number+1)
                        s.save()
                        slide.top_order_number = slide.top_order_number + 1
                        slide.save()
                elif qt == "short answer":
                    pform=NewExampleProblemSAForm(request.POST, instance=ep)
                    if pform.is_valid():
                        prob=pform.save()
                        prob.problem_display=newtexcode(prob.problem_code,'exampleproblem_'+str(prob.pk),'')
                        prob.prefix = prefix
                        compileasy(prob.problem_code,'exampleproblem_'+str(prob.pk))
                        prob.question_type = QuestionType.objects.get(question_type=qt)
                        prob.author = request.user
                        prob.save()
                        s = SlideObject(content_object=ep,slide=slide,order=slide.top_order_number+1)
                        s.save()
                        slide.top_order_number = slide.top_order_number + 1
                        slide.save()
                elif qt == "proof":
                    pform=NewExampleProblemPFForm(request.POST, instance=ep)
                    if pform.is_valid():
                        prob=pform.save()
                        prob.problem_display=newtexcode(prob.problem_code,'exampleproblem_'+str(prob.pk),'')
                        prob.prefix = prefix
                        compileasy(prob.problem_code,'exampleproblem_'+str(prob.pk))
                        prob.question_type = QuestionType.objects.get(question_type=qt)
                        prob.author = request.user
                        prob.save()
                        s = SlideObject(content_object=ep,slide=slide,order=slide.top_order_number+1)
                        s.save()
                        slide.top_order_number = slide.top_order_number + 1
                        slide.save()
                return JsonResponse({'example':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})
        if 'save' in form:
            slide_objs=list(slide.slide_objects.all())
            slide_objs=sorted(slide_objs,key=lambda x:x.order)
            slide_obj_inputs = form.getlist('slideobjectinput')
            for s in slide_objs:
                if 'slideobject_'+str(s.pk) not in slide_obj_inputs:
                    s.content_object.delete()# wouldn't this delete s???(copied comment from u)
                    s.delete()
            for i in range(0,len(slide_obj_inputs)):
                s = slide.slide_objects.get(pk=slide_obj_inputs[i].split('_')[1])###better way to do this? (i.e., get the query set first)
                s.order = i+1
                s.save()
            slide.top_order_number = slide.slide_objects.count()
            slide.save()
            return JsonResponse({'slideobjectlist':render_to_string('teacher/editingtemplates/edit-slide/slideobjectlist.html',{'slide_objects' :slide.slide_objects.all()})})
    context={}
    context['my_class'] = my_class
    context['unit'] = unit
    context['slides'] = slidegroup
    context['slide'] = slide
    context['nbar'] = 'teacher'
    return render(request,'teacher/editingtemplates/edit-slide.html',context)

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
    my_class = get_object_or_404(Class,pk=kwargs['pk'])
    if userprofile.my_classes.filter(pk=kwargs['pk']).exists()==False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=kwargs['upk'])
    if my_class.units.filter(pk=kwargs['upk']).exists==False:
        raise Http404("No such unit in this class.")
    slidegroup = get_object_or_404(SlideGroup,pk=kwargs['spk'])
    if unit.unit_objects.filter(slidegroup__isnull=False).filter(slidegroup__pk=slidegroup.pk).exists()==False:
        raise Http404("No such slides in this unit.")
    slide = get_object_or_404(Slide,pk=kwargs['sspk'])
    if slidegroup.slides.filter(pk=slide.pk).exists()==False:
        raise Http404("No such slide in the slide group.")
    form = request.GET
    prefix = form.get("example-prefix","")
    p = Problem.objects.get(pk=form.get('pk',''))
    ep = ExampleProblem(isProblem=1,problem=p,question_type=p.question_type_new,prefix=prefix)
    ep.save()
    s = SlideObject(content_object=ep,slide=slide,order=slide.top_order_number+1)
    s.save()
    slide.top_order_number = slide.top_order_number + 1
    slide.save()
    return JsonResponse({'example':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':s}),'sopk':s.pk})



@login_required
def exampleproblemgroupproblems(request,**kwargs):
    form = request.GET
    problem_group = get_object_or_404(ProblemGroup,pk=form.get('example-problem-group',''))
    return JsonResponse({'pgp-form':render_to_string('teacher/editingtemplates/example-problem-group-problems.html',{'problem_group':problem_group})})

@login_required
def examplebytag(request,**kwargs):
    contest_types = request.user.userprofile.user_type_new.allowed_types.all()
    tags = NewTag.objects.exclude(tag='root')
    return JsonResponse({'tag-form':render_to_string('teacher/editingtemplates/example-bytag.html',{'contest_types':contest_types,'tags':tags})})

@login_required
def examplebytagproblems(request,**kwargs):
    form = request.GET
    problems = Problem.objects.filter(type_new__type=form.get('example-contest-type','')).filter(newtags__in=NewTag.objects.filter(tag__startswith=NewTag.objects.get(pk=form.get('example-tag',''))))
    return JsonResponse({'problems':render_to_string('teacher/editingtemplates/example-bytag-problems.html',{'rows':problems})})

@login_required
def editexampleproblem(request,pk,upk,spk,sspk,sopk):
    userprofile=request.user.userprofile
    my_class = get_object_or_404(Class,pk=pk)
    if userprofile.my_classes.filter(pk=pk).exists()==False:
        raise Http404("Unauthorized.")
    unit = get_object_or_404(Unit,pk=upk)
    if my_class.units.filter(pk=upk).exists==False:
        raise Http404("No such unit in this class.")
    slidegroup = get_object_or_404(SlideGroup,pk=spk)
    if unit.unit_objects.filter(slidegroup__isnull=False).filter(slidegroup__pk=slidegroup.pk).exists()==False:
        raise Http404("No such slides in this unit.")
    slide = get_object_or_404(Slide,pk=sspk)
    if slidegroup.slides.filter(pk=slide.pk).exists()==False:
        raise Http404("No such slide in the slide group.")
    ep = get_object_or_404(ExampleProblem,pk=sopk)
    if slide.slide_objects.filter(content_type=ContentType.objects.get(app_label = 'teacher', model = 'exampleproblem')).filter(object_id=ep.pk).exists()==False:
        raise Http404("No such object in slide.")
    so = slide.slide_objects.filter(content_type=ContentType.objects.get(app_label = 'teacher', model = 'exampleproblem')).get(object_id=ep.pk)
    if request.method == "POST":
        form=request.POST
        qt = form.get('cqt-question-type','')
        if ep.isProblem == 0:
            if qt == "multiple choice":
                pform=NewExampleProblemMCForm(request.POST, instance=ep)
                if pform.is_valid():
                    prob=pform.save()
                    prob.problem_display=newtexcode(prob.problem_code,'exampleproblem_'+str(prob.pk),prob.answers())
                    compileasy(prob.problem_code,'exampleproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type=qt)
                    prob.author = request.user
                    prob.save()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':so}),'qt':qt,'sopk':so.pk})
            elif qt == "short answer":
                pform=NewExampleProblemSAForm(request.POST, instance=ep)
                if pform.is_valid():
                    prob=pform.save()
                    prob.problem_display=newtexcode(prob.problem_code,'exampleproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'exampleproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type=qt)
                    prob.save()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':so}),'qt':qt,'sopk':so.pk})
            elif qt == "proof":
                pform=NewExampleProblemPFForm(request.POST, instance=ep)
                if pform.is_valid():
                    prob=pform.save()
                    prob.problem_display=newtexcode(prob.problem_code,'exampleproblem_'+str(prob.pk),'')
                    compileasy(prob.problem_code,'exampleproblem_'+str(prob.pk))
                    prob.question_type = QuestionType.objects.get(question_type=qt)
                    prob.save()
                    return JsonResponse({'prob':render_to_string('teacher/editingtemplates/edit-slide/slideobject.html',{'s':so}),'qt':qt,'sopk':so.pk})
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
        return redirect('../../')

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
        return redirect('../../')

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
        return redirect('../../')

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
    return render(request,'teacher/publishedclasses/classview.html',{'class':my_class})

@login_required
def studentmanager(request):#request student accounts; add to classes
    userprofile = request.user.userprofile
    return render(request,'teacher/students/studentmanager.html',{'userprofile':userprofile})

@login_required
def blindgrade(request,**kwargs):
    my_class = get_object_or_404(PublishedClass,pk=kwargs['pk'])
    problemset = get_object_or_404(PublishedProblemSet,pk=kwargs['pspk'])##
    problem_object = get_object_or_404(PublishedProblemObject,pk=kwargs['popk'])
    if problem_object.question_type.question_type != 'proof':
        raise Http404('Not a proof question')
    responses = list(problem_object.response_set.all())
    shuffle(responses)
    return render(request,'teacher/publishedclasses/blindgrading.html',{'problem_object':problem_object,'responses':responses,'class':my_class,'problemset':problemset})

@login_required
def alphagrade(request,**kwargs):
    my_class = get_object_or_404(PublishedClass,pk=kwargs['pk'])
    problemset = get_object_or_404(PublishedProblemSet,pk=kwargs['pspk'])
    problem_object = get_object_or_404(PublishedProblemObject,pk=kwargs['popk'])
    if problem_object.question_type.question_type != 'proof':
        raise Http404('Not a proof question')
    responses = problem_object.response_set.order_by('user_problemset__userunitobject__user_unit__user_class__userprofile__user__username')
    return render(request,'teacher/publishedclasses/alphagrading.html',{'problem_object':problem_object,'responses':responses,'class':my_class,'problemset':problemset})




class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response

'''
class UnitUpdateView(AjaxableResponseMixin,UpdateView):
    model = Unit
    form_class = UnitForm
    template_name = 'teacher/classview/unit_edit_form.html'

    def dispatch(self, *args, **kwargs):
        self.unit_id = kwargs['upk']
        self.class_id = kwargs['pk']
        return super(UnitUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.save()
        unit = Unit.objects.get(id=self.unit_id)
        return redirect('/teacher/classes/'+str(self.class_id)+'/')

    def get_object(self, queryset=None):
        return get_object_or_404(Unit, pk=self.unit_id)
    def get_context_data(self, *args, **kwargs):
        context = super(UnitUpdateView, self).get_context_data(*args, **kwargs)
        context['class'] = self.class_id
        return context
'''


#######PROBLEM GROUPS#######
@login_required
def grouptableview(request):
    userprofile = request.user.userprofile
    if request.method == 'POST':
        group_form = GroupModelForm(request.POST)
        if group_form.is_valid():
            group = group_form.save()
            userprofile.problem_groups.add(group)
            userprofile.save()
    prob_groups = userprofile.problem_groups.all()
    template = loader.get_template('teacher/problemgroups/grouptableview.html')
    group_inst = ProblemGroup(name='')
    form = GroupModelForm(instance=group_inst)
    context = {}
    context['form'] = form
    context['nbar'] = 'teacher'
    context['probgroups'] =  prob_groups
    return HttpResponse(template.render(context,request))

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

@login_required
def deletegroup(request,pk):
    pg = get_object_or_404(ProblemGroup, pk=pk)
    userprofile = request.user.userprofile
    if pg in userprofile.problem_groups.all():
        if pg.is_shared==0:
            pg.delete()
        else:
            userprofile.problem_groups.remove(pg)
    return redirect('/teacher/problemgroups/')

#@login_required
#def sync_class(request,pk):
#    p = get_object_or_404(PublishedClass,pk=pk)
#    userprofile=request.user.userprofile
#    my_class = pub_class.parent_class
#    if userprofile.my_published_classes.filter(pk=pk).exists()==False:
#        raise Http404("Unauthorized.")
#    class_points = 0
#    class_prob_num = 0
#    for u in my_class.units.all():
#        new_unit = Unit(name=u.name,order=u.order)
#        new_unit.save()
#        p.units.add(new_unit)
#        unit_points = 0
#        unit_prob_num = 0
#        num_problemsets = 0
#        for uo in u.unit_objects.all():
#            try:
#                sg = uo.slidegroup
#                new_unit_object = UnitObject(unit = new_unit,order = uo.order)
#                new_unit_object.save()
#                new_slide_group = SlideGroup(name = uo.slidegroup.name,num_slides = uo.slidegroup.slides.count(),unit_object = new_unit_object)
#                new_slide_group.save()
#                for s in uo.slidegroup.slides.all():
#                    new_slide = Slide(title=s.title,order=s.order, slidegroup=new_slide_group,top_order_number=s.top_order_number)
#                    new_slide.save()
#                    for so in s.slide_objects.all():
#                        if so.content_type == ContentType.objects.get(app_label = 'teacher', model = 'textblock'):
#                            new_textblock = TextBlock(text_code = so.content_object.text_code,text_display="")
#                            new_textblock.save()
#                            new_textblock.text_display = newtexcode(so.content_object.text_code, 'textblock_'+str(new_textblock.pk), "")
#                            new_textblock.save()
#                            compileasy(new_textblock.text_code,'textblock_'+str(new_textblock.pk))
#                            new_so=SlideObject(content_object=new_textblock,slide=new_slide,order=so.order)
#                            new_so.save()
#                        if so.content_type == ContentType.objects.get(app_label = 'teacher', model = 'proof'):
#                            new_proof = Proof(prefix=so.content_object.prefix,proof_code = so.content_object.proof_code,proof_display="")
#                            new_proof.save()
#                            new_proof.proof_display = newtexcode(so.content_object.proof_code, 'proofblock_'+str(new_proof.pk), "")
#                            new_proof.save()
#                            compileasy(new_proof.proof_code,'proofblock_'+str(new_proof.pk))
#                            new_so=SlideObject(content_object=new_proof,slide=new_slide,order=so.order)
#                            new_so.save()
#                        if so.content_type == ContentType.objects.get(app_label = 'teacher', model = 'theorem'):
#                            new_theorem = Theorem(name=so.content_object.name,prefix=so.content_object.prefix,theorem_code = so.content_object.theorem_code,theorem_display="")
#                            new_theorem.save()
#                            new_theorem.theorem_display = newtexcode(so.content_object.theorem_code, 'theoremblock_'+str(new_theorem.pk), "")
#                            new_theorem.save()
#                            compileasy(new_theorem.theorem_code,'theoremblock_'+str(new_theorem.pk))
#                            new_so=SlideObject(content_object=new_theorem,slide=new_slide,order=so.order)
#                            new_so.save()
#                        if so.content_type == ContentType.objects.get(app_label = 'teacher', model = 'exampleproblem'):
#                            new_example = ExampleProblem(name=so.content_object.name,prefix=so.content_object.prefix,problem_code = so.content_object.problem_code,problem_display="",isProblem=so.content_object.isProblem, problem=so.content_object.problem,question_type=so.content_object.question_type,mc_answer = so.content_object.mc_answer,sa_answer = so.content_object.sa_answer,answer_A = so.content_object.answer_A,answer_B = so.content_object.answer_B,answer_C = so.content_object.answer_C,answer_D = so.content_object.answer_D,answer_E = so.content_object.answer_E,author=so.content_object.author)
#                            new_example.save()
#                            new_example.problem_display = newtexcode(so.content_object.problem_code, 'exampleproblem_'+str(new_example.pk), "")
#                            new_example.save()
#                            compileasy(new_example.problem_code,'exampleproblem_'+str(new_example.pk))
#                            new_so=SlideObject(content_object=new_example,slide=new_slide,order=so.order)
#                            new_so.save()
#                        if so.content_type == ContentType.objects.get(app_label = 'teacher', model = 'imagemodel'):
#                            new_image = ImageModel(image = so.content_object.image)
#                            new_image.save()
#                            new_so=SlideObject(content_object=new_image,slide=new_slide,order=so.order)
#                            new_so.save()
#            except:
#                pset = uo.problemset
#                num_problemsets += 1
#                new_unit_object = UnitObject(unit = new_unit,order = uo.order)
#                new_unit_object.save()
#                new_problemset = ProblemSet(name = uo.problemset.name,default_point_value = uo.problemset.default_point_value,unit_object = new_unit_object)
#                new_problemset.save()
#                total_points=0
#                for po in uo.problemset.problem_objects.all():
#                    new_po = ProblemObject(order = po.order,point_value=po.point_value,problem_code = po.problem_code,problem_display="",isProblem=po.isProblem, problem=po.problem,question_type=po.question_type,mc_answer = po.mc_answer,sa_answer = po.sa_answer,answer_A = po.answer_A,answer_B = po.answer_B,answer_C = po.answer_C,answer_D = po.answer_D,answer_E = po.answer_E,author=po.author)
#                    new_po.save()
#                    if new_po.isProblem == 0:
#                        if new_po.question_type.question_type =='multiple choice':
#                            new_po.problem_display = newtexcode(po.problem_code, 'originalproblem_'+str(new_po.pk), new_po.answers())
#                        else:
#                            new_po.problem_display = newtexcode(po.problem_code, 'originalproblem_'+str(new_po.pk), "")
#                        new_po.save()
#                        compileasy(new_po.problem_code,'originalproblem_'+str(new_po.pk))
#                    new_problemset.problem_objects.add(new_po)
#                    total_points += po.point_value
#                new_problemset.total_points = total_points
#                new_problemset.num_problems = new_problemset.problem_objects.count()
#                new_problemset.save()
#                unit_points += total_points
#                unit_prob_num += new_problemset.num_problems
#        new_unit.total_points = unit_points
#        new_unit.num_problems = unit_prob_num
#        new_unit.num_problemsets = num_problemsets
#        new_unit.save()
#        class_points += unit_points
#        class_prob_num += new_unit.num_problems
#    p.total_points = class_points
#    p.num_problems = class_prob_num
#    p.save()
#    userprofile.my_published_classes.add(p)
#    userprofile.save()

    
    


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
                if ups.problemset.problem_objects.filter(problem=r.problem).exists():
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
    po = user_problemset.problemset.problem_objects.get(problem = resp.problem)
    print('josadf')
    print(user_problemset.response_set.filter(problem_object = po))
    if user_problemset.response_set.filter(problem_object = po).exists()==False:
        print('josadf2')
        r = Response(problem_object = po, user_problemset=user_problemset, response = resp.response,attempted = resp.attempted, stickied = resp.stickied, order = po.order, point_value = po.point_value, modified_date = resp.modified_date)
        r.save()
        if po.question_type.question_type == "short answer":
            if resp.response == po.sa_answer:
                r.points = r.point_value
                r.save()
        resp.is_migrated = 1
        resp.save()
        return JsonResponse({'success':1,'name':user_problemset.problemset.name,'resp_pk':resp_pk})
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
        return JsonResponse({'date_snippet':render_to_string('teacher/editingtemplates/due_date_snippet.html',{'test':test,'request':request})})
    
@login_required
def delete_duedate(request):
    data_type = request.POST.get('uo')
    if data_type == 'ps':
        problemset = get_object_or_404(ProblemSet,pk=request.POST.get('pk'))
        problemset.due_date = None
        problemset.save()
        return JsonResponse({'date_snippet':render_to_string('teacher/editingtemplates/due_date_snippet.html',{'problemset':problemset,'request':request})})
    elif data_type == 'tst':
        test = get_object_or_404(Test,pk=request.POST.get('pk'))
        test.due_date = None
        test.save()
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
        return JsonResponse({'date_snippet':render_to_string('teacher/editingtemplates/due_date_snippet.html',{'test':test,'request':request})})
    
@login_required
def delete_startdate(request):
    data_type = request.POST.get('uo')
    if data_type == 'ps':
        problemset = get_object_or_404(ProblemSet,pk=request.POST.get('pk'))
        problemset.start_date = None
        problemset.save()
        return JsonResponse({'date_snippet':render_to_string('teacher/editingtemplates/due_date_snippet.html',{'problemset':problemset,'request':request})})
    elif data_type == 'tst':
        test = get_object_or_404(Test,pk=request.POST.get('pk'))
        test.start_date = None
        test.save()
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
        return JsonResponse({'time_snippet':render_to_string('teacher/editingtemplates/time_limit_snippet.html',{'problemset':problemset,'request':request})})
    elif data_type == 'tst':
        test = get_object_or_404(Test,pk=request.POST.get('edps-pk'))
        minutes = request.POST.get('minutes')
        hours = request.POST.get('hours')
        test.time_limit = time(hour=int(hours),minute=int(minutes))
        test.save()
        return JsonResponse({'time_snippet':render_to_string('teacher/editingtemplates/time_limit_snippet.html',{'test':test,'request':request})})

@login_required
def delete_timelimit(request):
    data_type = request.POST.get('uo')
    if data_type == 'ps':
        problemset = get_object_or_404(ProblemSet,pk=request.POST.get('pk'))
        problemset.time_limit = None
        problemset.save()
        return JsonResponse({'time_snippet':render_to_string('teacher/editingtemplates/time_limit_snippet.html',{'problemset':problemset,'request':request})})
    elif data_type == 'tst':
        test = get_object_or_404(Test,pk=request.POST.get('pk'))
        test.time_limit = None
        test.save()
        return JsonResponse({'time_snippet':render_to_string('teacher/editingtemplates/time_limit_snippet.html',{'test':test,'request':request})})
