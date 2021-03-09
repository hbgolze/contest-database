from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse,HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required

# Create your views here.
from randomtest.models import UserProfile,Problem
from .models import MockTestFolder,MockTest,UserMockTest,UserMockTestSegment,UserMockProblem

@login_required
def index(request):
    userprofile,boolcreated = UserProfile.objects.get_or_create(user=request.user)
    folders = MockTestFolder.objects.all()
    return render(request,'mocktests/indexview.html',{'folders': folders,'userprofile': userprofile, 'nbar': 'mocktests'})
@login_required
def add_mocktest(request):
    pk = request.POST.get('pk','')
    mocktest = get_object_or_404(MockTest,pk=pk)
    userprofile = UserProfile.objects.get(user = request.user)
    umt = mocktest.add_to_user(userprofile)
    return JsonResponse({'table-row-html': render_to_string('mocktests/usermocktestrow.html',{'umt': umt, 'request': request})})
@login_required
def mocktestview(request):
    pk = request.GET.get('id','')
    usermocktest = get_object_or_404(UserMockTest,pk=pk)
    userprofile = UserProfile.objects.get(user = request.user)
    if usermocktest.userprofile != userprofile:
        return HttpResponse("Unauthorized")
    if usermocktest.status > 0:
        return HttpResponse("Test already started")
    return render(request,'mocktests/mocktest_view.html',{'umt': usermocktest})
@login_required
def start_mocktest(request):
    pk = request.POST.get('pk','')
    t = timezone.now()
    usermocktest = get_object_or_404(UserMockTest,pk=pk)
    usermocktest.status = 1
    usermocktest.current_segment = 1
    usermocktest.start_time = t
    usermocktest.save()
    user_segment = usermocktest.segments.all()[0]
    user_segment.status = 1
    user_segment.start_time = t
    user_segment.save()
    return JsonResponse({'problems-html':render_to_string('mocktests/mocktest_problems.html',{'user_segment':user_segment,'request':request}),'time_limit': user_segment.mock_test_segment.time_limit.seconds*1000})
@login_required
def submit_mocktest_segment(request):
    pk = request.POST.get('seg-pk','')
    t = timezone.now()
    user_segment = get_object_or_404(UserMockTestSegment,pk=pk)
    user_mocktest = user_segment.user_mock_test
    for key,value in request.POST.items():
        if 'answer_' in key:
            a = key.split('__')
            prob = UserMockProblem.objects.get(pk=a[1])
            if a[0] == 'answer_a':
                prob.answer_a = value
            elif a[0] == 'answer_b':
                prob.answer_b = value
            elif a[0] == 'answer_c':
                prob.answer_c = value
            prob.save()
    user_segment.status = 2
    user_segment.end_time = t
    user_segment.save()
    next_segments = user_mocktest.segments.filter(order__gt = user_segment.order)
    if next_segments.count() == 0:
        user_mocktest.end_time = t
        user_mocktest.grade()
        user_mocktest.status = 2
        user_mocktest.save()
        return JsonResponse({'end':1})
    next_segment = next_segments[0]
    user_mocktest.current_segement = next_segment.order
    user_mocktest.save()
    next_segment.start_time = timezone.now()
    next_segment.status = 1
    next_segment.save()
    if next_segment.mock_test_segment.segment_type == 'PR':
        return JsonResponse({'problems-html':render_to_string('mocktests/mocktest_problems.html',{'user_segment':next_segment,'request':request}),'time_limit': next_segment.mock_test_segment.time_limit.seconds*1000,'end':0})
    else:
        return JsonResponse({'problems-html':render_to_string('mocktests/mocktest_break.html',{'user_segment':next_segment,'request':request}),'time_limit': next_segment.mock_test_segment.time_limit.seconds*1000,'end':0})
@login_required
def review_mocktest(request):
    pk = request.GET.get('id','')
    usermocktest = get_object_or_404(UserMockTest,pk=pk)
    userprofile = UserProfile.objects.get(user = request.user)
    if usermocktest.userprofile != userprofile:
        return HttpResponse("Unauthorized")
    if usermocktest.status < 2:
        return HttpResponse("Test not completed")
    return render(request,'mocktests/review_mocktest.html',{'umt': usermocktest})

class SolutionView(DetailView):
    model = Problem
    template_name = 'mocktests/load_sol.html'
    def dispatch(self, *args, **kwargs):
        self.item_id = kwargs['pk']
        return super(SolutionView, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Problem, pk=self.item_id)
