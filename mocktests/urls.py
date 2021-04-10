from django.conf.urls import include,url
from django.urls import path


from . import views

from django.contrib.auth.decorators import login_required,user_passes_test


urlpatterns = [
    path('',views.index,name='mocktest_index'),
    path('student/',views.teacherindex,name='mocktest_teacher_index'),
    path('student/review_test/',views.teacher_review_mocktest,name='teacher_review_mocktest'),
    path('student/review_test/allow_solutions/',views.review_allow_solutions,name='review_allow_solutions'),
    path('test/',views.mocktestview,name='mocktestview'),
    path('review_test/',views.review_mocktest,name='review_mocktest'),
    path('ajax/add-mocktest/',views.add_mocktest,name='add_mocktest'),
    path('ajax/start-mocktest/',views.start_mocktest,name='start_mocktest'),
    path('ajax/submit-mocktest-segment/',views.submit_mocktest_segment,name='submit_mocktest_segment'),
    path('load_sol/<int:pk>/', login_required(views.SolutionView.as_view()), name='mocktest_load_solution'),
    ]
