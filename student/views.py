from django.shortcuts import render,render_to_response, get_object_or_404,redirect
from django.template.loader import get_template,render_to_string
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,Http404,HttpResponse

from django.contrib.auth.models import User
from django.views.generic import DetailView
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from datetime import datetime,timedelta


from student.models import UserProblemSet,Response,Sticky,UserResponse,UserSlides,UserTest
from teacher.models import ProblemObject,PublishedProblemObject

from randomtest.utils import pointsum,compileasy,newtexcode

@login_required
def classview(request):
    userprofile = request.user.userprofile
#    classes = request.user.publishedclass_set.all()
    classes = userprofile.userclasses.all()


#pointsum
    weekofresponses = userprofile.student_responselog.filter(modified_date__date__gte = datetime.today().date() - timedelta(days = 7)).filter(correct = 1)
    daycorrect=[((datetime.today().date() - timedelta(days = i)).strftime('%A, %B %d'),str(weekofresponses.filter(modified_date__date = datetime.today().date() - timedelta(days = i)).count()),pointsum(weekofresponses.filter(modified_date__date = datetime.today().date() - timedelta(days = i)))) for i in range(1,7)]

    todaycorrect = str(userprofile.student_responselog.filter(modified_date__date = datetime.today().date()).filter(correct = 1).count())
    pointtoday = str(pointsum(userprofile.student_responselog.filter(modified_date__date = datetime.today().date()).filter(correct = 1)))
    context = {}
    context['nbar'] = 'student'

    context['todaycorrect'] = todaycorrect
    context['weekcorrect'] = daycorrect
    context['pointtoday'] = pointtoday

    context['stickies'] = userprofile.student_stickies.all().order_by('-sticky_date')
    context['responselog'] = userprofile.student_responselog.all().order_by('-modified_date')[0:50]
    


    context['classes'] = classes
    return render(request,'student/studentview.html',context)


@login_required
def problemsetview(request,**kwargs): 
    context={}
    pk=kwargs['pk']
    userprofile = request.user.userprofile
    user_problemset = get_object_or_404(UserProblemSet, pk=pk)
    if user_problemset.userunitobject.user_unit.user_class.userprofile != userprofile:
        return HttpResponse('Unauthorized', status=401)
    if user_problemset.published_problemset.start_date != None:
        if user_problemset.published_problemset.start_date > timezone.now():
            context['problemset'] = user_problemset
            context['pk'] = pk
            context['nbar'] = 'student'
            context['too_early'] = 1
            return render(request,'student/problemsetview.html',context)
    if user_problemset.is_initialized == 0:
        print('not_init')
        user_problemset.response_initialize()
    if user_problemset.published_problemset.due_date != None:
        if user_problemset.published_problemset.due_date < timezone.now():
            context['past_due'] = 1
    spammed_pks = []
    if request.method == "POST":
        form=request.POST
        P=user_problemset.response_set.all()

        num_correct = 0
        num_points = 0
        for r in P:
            prev_attempted = r.attempted
            tempanswer = form.get('answer'+str(r.publishedproblem_object.pk))
            if tempanswer != None and tempanswer !='':
                t=timezone.now()
                r.attempted = 1
                if r.response != tempanswer:# new response
                    if r.publishedproblem_object.question_type.question_type == "short answer" or r.publishedproblem_object.question_type.question_type == "multiple choice":
                        if prev_attempted and t < r.modified_date+timedelta(hours=0,minutes=1):
                            spammed_pks.append(r.pk)
                        else:
                            if r.publishedproblem_object.isProblem:
                                readable_label = r.publishedproblem_object.problem.readable_label
                            else:
                                readable_label = 'Problem #'+str(r.publishedproblem_object.order)
                            ur = UserResponse(userprofile=userprofile, user_problemset = user_problemset,response=r,static_response=tempanswer,readable_label=readable_label,modified_date=t,point_value=r.point_value)
                            ur.save()
                            r.modified_date = t
                            r.response = tempanswer
                            if r.publishedproblem_object.question_type.question_type == "multiple choice" or r.publishedproblem_object.question_type.question_type == "short answer":
                                r.num_attempts = r.num_attempts + 1
# should something similar happen for proof?
                            r.save()

                            if r.publishedproblem_object.question_type.question_type == "multiple choice":
                                if r.publishedproblem_object.isProblem == True:
                                    answer = r.publishedproblem_object.problem.mc_answer
                                else:
                                    answer = r.publishedproblem_object.mc_answer
                                if r.response == answer:
                                    ur.correct = 1
                                    ur.save()
                                    r.points = r.point_value
                                    r.save()
                                    num_correct += 1
                                    num_points += r.point_value
                            elif r.publishedproblem_object.question_type.question_type == "short answer":
                                if r.publishedproblem_object.isProblem == True:
                                    answer = r.publishedproblem_object.problem.sa_answer
                                else:
                                    answer = r.publishedproblem_object.sa_answer
                                if r.response == answer:
                                    ur.correct = 1
                                    ur.save()
                                    r.points = r.point_value
                                    r.save()
                                    num_correct += 1
                                    num_points += r.point_value
        user_problemset.num_correct = user_problemset.num_correct+num_correct
        user_problemset.userunitobject.user_unit.num_correct = user_problemset.userunitobject.user_unit.num_correct+num_correct
        user_problemset.userunitobject.user_unit.user_class.num_correct = user_problemset.userunitobject.user_unit.user_class.num_correct+num_correct
        user_problemset.points_earned = user_problemset.points_earned+num_points
        user_problemset.userunitobject.user_unit.points_earned = user_problemset.userunitobject.user_unit.points_earned+num_points
        user_problemset.userunitobject.user_unit.user_class.points_earned = user_problemset.userunitobject.user_unit.user_class.points_earned+num_points
        user_problemset.save()
        user_problemset.userunitobject.user_unit.save()
        user_problemset.userunitobject.user_unit.user_class.save()
#        return HttpResponse('')
    rows = user_problemset.response_set.all()
    context['rows'] = rows
    response_rows = []
    for i in range(0,int((rows.count()+14)/15)):
        response_rows.append((rows[15*i:15*(i+1)],15*i))
    context['response_rows'] = response_rows
    context['problemset'] = user_problemset
    context['pk'] = pk
    context['nbar'] = 'student'
    context['spammed_pks'] = spammed_pks
    return render(request, 'student/problemsetview.html',context)


class SolutionView(DetailView):
    model = PublishedProblemObject
    template_name = 'student/load_sol.html'

    def dispatch(self, *args, **kwargs):
        self.item_id = kwargs['ppk']
        return super(SolutionView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(PublishedProblemObject, pk=self.item_id)

@login_required
def toggle_star(request,**kwargs):
    userprofile = request.user.userprofile
    data_type = request.POST.get('data_type','')
    pk = request.POST.get('pk','')
    if data_type == 'ups':
        user_problemset = get_object_or_404(UserProblemSet, pk=pk)
        if user_problemset.userunitobject.user_unit.user_class.userprofile != userprofile:
            return HttpResponse('Unauthorized', status=401)
    elif data_type == 'ut':
        user_test = get_object_or_404(UserTest, pk=pk)
        if user_test.userunitobject.user_unit.user_class.userprofile != userprofile:
            return HttpResponse('Unauthorized', status=401)
    star_tag = request.POST.get('star_id','')
    star_list = star_tag.split('_')
    response_pk = star_list[1]
    response = get_object_or_404(Response,pk=response_pk)
    if response.stickied == True:
        response.stickied = False
        response.save()
        try:
            s = Sticky.objects.get(response = response)
            s.delete()
        except Sticky.DoesNotExist:
            s = None
        return JsonResponse({
                'response_pk' : response_pk,
                'is_stickied' : 'false',
                'response_code' : "<span class='fa fa-star-o'></span>",
                'problem_label':response.publishedproblem_object.pk
                })
    else:
        if response.publishedproblem_object.isProblem:
            readable_label = response.publishedproblem_object.problem.readable_label
        else:
            readable_label = 'Problem #'+str(response.publishedproblem_object.order)
        if data_type == 'ups':
            s = Sticky(response = response, problemset = user_problemset, userprofile = userprofile, readable_label = readable_label)
            s.save()
        elif data_type == 'ut':
            s = Sticky(response = response, test = user_test, userprofile = userprofile, readable_label = readable_label)
            s.save()
        response.stickied = True
        response.save()
        return JsonResponse({
                'response_pk' : response_pk,
                'is_stickied' : 'true',
                'response_code' : "<span class='fa fa-star'></span>",
                'problem_label' : response.publishedproblem_object.pk
                })


@login_required
def checkanswer(request,pk):
    userprofile = request.user.userprofile
    user_problemset = get_object_or_404(UserProblemSet, pk=pk)
    if user_problemset.userunitobject.user_unit.user_class.userprofile != userprofile:
        return HttpResponse('Unauthorized', status=401)
    response_label=request.POST.get('response_id','')
    problem_label = response_label.split('-')[2]
    problem_object = get_object_or_404(PublishedProblemObject,pk=problem_label)

    tempanswer = request.POST.get('answer','')
    
    r = user_problemset.response_set.get(publishedproblem_object = problem_object)
    t=timezone.now()
    if problem_object.question_type.question_type == "short answer" or problem_object.question_type.question_type == "multiple choice":
        if r.attempted and t < r.modified_date+timedelta(hours=0,minutes=1):
            return JsonResponse({'spam':'true'})
    r.attempted = 1
    if r.response != tempanswer:#....if new response
        if r.publishedproblem_object.question_type.question_type == "multiple choice" or r.publishedproblem_object.question_type.question_type == "short answer":
            r.num_attempts = r.num_attempts + 1
        # should something similar happen for proof?
        if problem_object.isProblem:
            readable_label = problem_object.problem.readable_label
        else:
            readable_label = 'Problem #'+str(problem_object.order)
        ur=UserResponse(userprofile=userprofile, user_problemset = user_problemset,response=r,static_response=tempanswer,readable_label=readable_label,modified_date=t,point_value=r.point_value)
        ur.save()
        r.modified_date = t
        r.response = tempanswer
        r.save()
        if problem_object.question_type.question_type == "multiple choice":
            if problem_object.isProblem == True:
                answer = problem_object.problem.mc_answer
            else:
                answer = problem_object.mc_answer
            if r.response == answer:
                ur.correct = 1
                ur.save()
                r.points = r.point_value
                r.save()
        elif problem_object.question_type.question_type == "short answer":
            if problem_object.isProblem == True:
                answer = problem_object.problem.sa_answer
            else:
                answer = problem_object.sa_answer
            if r.response == answer:
                ur.correct=1
                ur.save()
                r.points = r.point_value
                r.save()
        if ur.correct == 1:
            user_problemset.num_correct = user_problemset.num_correct+1
            user_problemset.userunitobject.user_unit.num_correct = user_problemset.userunitobject.user_unit.num_correct+1
            user_problemset.userunitobject.user_unit.user_class.num_correct = user_problemset.userunitobject.user_unit.user_class.num_correct+1
            user_problemset.points_earned = user_problemset.points_earned+r.point_value
            user_problemset.userunitobject.user_unit.points_earned = user_problemset.userunitobject.user_unit.points_earned+r.point_value
            user_problemset.userunitobject.user_unit.user_class.points_earned = user_problemset.userunitobject.user_unit.user_class.points_earned+r.point_value
            user_problemset.save()
            user_problemset.userunitobject.user_unit.save()
            user_problemset.userunitobject.user_unit.user_class.save()
    else:#response is not new
        return JsonResponse({'blank': 'true'})
    if tempanswer != None and tempanswer !='' and tempanswer != 'undefined':
        mod_date = render_to_string("student/problemset/date-snippet.html",{'resp':r})
        if tempanswer == answer:
            if problem_object.isProblem == True and problem_object.problem.solutions.count() > 0:
                return JsonResponse({'blank':'false','correct' : 'true', 'has_solution' : 'true','prob_pk' : problem_object.pk,'mod-date':mod_date})
            else:
                return JsonResponse({'blank':'false','correct' : 'true', 'has_solution' : 'false','prob_pk' : problem_object.pk,'mod-date':mod_date})
        else:
            return JsonResponse({'blank':'false','correct' : 'false','mod-date':mod_date})
    return JsonResponse({'blank':'true'})

@login_required
def load_proof_response(request,**kwargs):
    resp_pk = request.GET.get('resp_pk','')
    resp = get_object_or_404(Response,pk=resp_pk)
    context = {}
    if resp.publishedproblem_object.isProblem == 1:
        if resp.publishedproblem_object.question_type.question_type == "multiple choice":
            context['problem_display'] = resp.publishedproblem_object.problem.display_mc_problem_text
        else:
            context['problem_display'] = resp.publishedproblem_object.problem.display_problem_text
        context['readable_label'] = resp.publishedproblem_object.problem.readable_label
    else:
        context['problem_display'] = resp.publishedproblem_object.problem_display
    context['resp'] = resp
    return JsonResponse({'modal-html':render_to_string('student/problemset/modal-edit-proof.html',context)})

@login_required
def save_proof_response(request,**kwargs):
    resp_pk = request.POST.get('er-pk','')
    response_code = request.POST.get('response_text','')
    resp = get_object_or_404(Response,pk = resp_pk)
    resp.response_code = response_code
    resp.attempted = 1
    resp.display_response = newtexcode(resp.response_code, 'response_'+str(resp.pk), "")
    resp.modified_date = timezone.now()
    resp.save()
    compileasy(resp.response_code,'response_'+str(resp.pk))
    mod_date = render_to_string("student/problemset/date-snippet.html",{'resp':resp})
    return JsonResponse({'display_response':render_to_string("student/problemset/proof-response-snippet.html",{'resp':resp,'problem_label':resp.publishedproblem_object.pk}),'po_pk':resp.publishedproblem_object.pk,'mod-date':mod_date})

@login_required
def slidesview(request,**kwargs):
    context={}
    pk=kwargs['pk']
    userprofile = request.user.userprofile
    user_slides = get_object_or_404(UserSlides, pk=pk)
    if user_slides.userunitobject.user_unit.user_class.userprofile != userprofile:
        return HttpResponse('Unauthorized', status=401)
    slides = user_slides.published_slides.slides.all()
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
    return render(request,'student/slidesview.html',{'slides':user_slides,'rows':rows})


@login_required
def testview(request,**kwargs): 
    context={}
    pk=kwargs['pk']
    userprofile = request.user.userprofile
    user_test = get_object_or_404(UserTest, pk=pk)
    if user_test.userunitobject.user_unit.user_class.userprofile != userprofile:
        return HttpResponse('Unauthorized', status=401)
    if user_test.published_test.start_date != None:
        if user_test.published_test.start_date > timezone.now():
            context['test'] = user_test
            context['pk'] = pk
            context['nbar'] = 'student'
            context['too_early'] = 1
            return render(request,'student/testview.html',context)
    if user_test.is_initialized == 0:
        user_test.response_initialize()
    if user_test.published_test.due_date != None:
        if user_test.published_test.due_date < timezone.now():
            context['past_due'] = 1
    if user_test.start_time !=None:
        if user_test.start_time+timedelta(hours=user_test.published_test.time_limit.hour,minutes = user_test.published_test.time_limit.minute) < timezone.now():#if current time is past due_date or past time_limit
            context['past_due'] = 1
    if user_test.is_graded == 0:
        context['not_graded'] = 1
    if user_test.in_progress == False:
        user_test.start_time = timezone.now()
        user_test.in_progress = True
        user_test.save()
    if request.method == "POST":
        form=request.POST
        P=user_test.response_set.all()
        for r in P:
            tempanswer = form.get('answer'+str(r.publishedproblem_object.pk))
            if tempanswer != None and tempanswer !='':
                t=timezone.now()
                r.attempted = 1
                if r.response != tempanswer:# if new answer
                    r.modified_date = t
                    r.response = tempanswer
                    r.save()
            else:
                r.attempted = 0
                r.response = ''
                r.save()
        return HttpResponse('')#The jquery does location.reload
    rows = user_test.response_set.all()
    context['rows'] = rows
    response_rows = []
    for i in range(0,int((rows.count()+14)/15)):
        response_rows.append((rows[15*i:15*(i+1)],15*i))
    context['response_rows'] = response_rows
    context['test'] = user_test
    context['pk'] = pk
    context['nbar'] = 'student'
    return render(request, 'student/testview.html',context)


@login_required
def saveresponse(request,pk):
    userprofile = request.user.userprofile
    user_test = get_object_or_404(UserTest, pk=pk)
    if user_test.userunitobject.user_unit.user_class.userprofile != userprofile:
        return HttpResponse('Unauthorized', status=401)

    response_label=request.POST.get('response_id','')
    problem_label = response_label.split('-')[2]
    problem_object = get_object_or_404(PublishedProblemObject,pk=problem_label)

    tempanswer = request.POST.get('answer','')
    
    r = user_test.response_set.get(publishedproblem_object = problem_object)
    t = timezone.now()
    if t > user_test.start_time+timedelta(hours=user_test.published_test.time_limit.hour,minutes=user_test.published_test.time_limit.minute):
        return JsonResponse({'error':'Time is up!'})
    if user_test.published_test.due_date != None:
        if t > user_test.published_test.due_date:
            return JsonResponse({'error':'Test is due!!'})
    r.attempted = 1
    if r.response != tempanswer:#....if new response
        if tempanswer == "" or tempanswer == None or tempanswer == "undefined":
            r.attempted = 0
            r.response = ""
            r.save()
            return JsonResponse({'prob_pk':problem_object.pk,'mod-date':"",'newly_blank':1})
        r.modified_date = t
        r.response = tempanswer
        r.save()
#DO NOT ADJUST ANY STATS UNTIL GRADING!!!!
        mod_date = render_to_string("student/test/date-snippet.html",{'resp':r,'request':request})
        return JsonResponse({'prob_pk':problem_object.pk,'mod-date':mod_date})
    return JsonResponse({'prob_pk':problem_object.pk,'no_change':1})

@login_required
def grade_test(request,**kwargs):
    pk=kwargs['pk']
    userprofile = request.user.userprofile
    user_test = get_object_or_404(UserTest, pk=pk)
    if user_test.userunitobject.user_unit.user_class.userprofile != userprofile:
        return HttpResponse('Unauthorized', status=401)
    t=timezone.now()

    if t <= user_test.start_time+timedelta(hours=user_test.published_test.time_limit.hour,minutes=user_test.published_test.time_limit.minute):
        return JsonResponse({'error':'Please wait for the time limit to expire!'})
    if user_test.is_graded == False:
        P = user_test.response_set.all()
        points_earned = 0
        correct_problems = 0
        for r in P:
            if r.publishedproblem_object.question_type.question_type == 'short answer' or r.publishedproblem_object.question_type.question_type == 'multiple choice':
                if r.attempted:
                    print('attempted')
                    if r.publishedproblem_object.question_type.question_type =='short answer':
                        if r.publishedproblem_object.isProblem ==1:
                            answer = r.publishedproblem_object.problem.sa_answer
                        else:
                            answer = r.publishedproblem_object.sa_answer
                    else:
                        if r.problem_object.isProblem ==1:
                            answer = r.publishedproblem_object.problem.mc_answer
                        else:
                            answer = r.publishedproblem_object.mc_answer
                    if r.response == answer:
                        correct_problems += 1
                        points_earned += r.publishedproblem_object.point_value
                        r.points = r.publishedproblem_object.point_value
                        r.is_graded = 1
                        r.save()
                else:
                    print('blank')
                    r.points = r.publishedproblem_object.blank_point_value
                    points_earned += r.publishedproblem_object.blank_point_value
                    r.is_graded = 1
                    r.save()
            else:
                print('sad')
        user_test.points_earned = points_earned
        user_test.num_correct = correct_problems
        user_test.is_graded = 1
        user_test.save()
    return JsonResponse({})
