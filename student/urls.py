from django.conf.urls import include,url

from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^$', views.classview, name='studentview'),
    url(r'^problemset/(?P<pk>\d+)/$', views.problemsetview, name='problemsetview'),
    url(r'^problemset/(?P<pk>\d+)/load_sol/(?P<ppk>\d+)/$', login_required(views.SolutionView.as_view()), name='student_load_solution'),
    url(r'^problemset/(?P<pk>\d+)/toggle_star/$', views.toggle_star, name='student_toggle_star'),
    url(r'^problemset/(?P<pk>\d+)/checkanswer/$', views.checkanswer, name='student_checkanswer'),
#    url(r'^problemset/(?P<pk>\d+)/load-proof-response/$', views.load_proof_response, name='load_proof_response'),
#    url(r'^problemset/(?P<pk>\d+)/save-proof-response/$', views.save_proof_response, name='save_proof_response'),
    url(r'^slides/(?P<pk>\d+)/$', views.slidesview, name='slidesview'),
    url(r'^test/(?P<pk>\d+)/$', views.testview, name='testview'),
    url(r'^test/(?P<pk>\d+)/grade_test/$', views.grade_test, name='gradetestview'),
    url(r'^test/(?P<pk>\w+)/saveresponse/$', views.saveresponse, name='student_save_response'),
    url(r'^test/(?P<pk>\d+)/load_sol/(?P<ppk>\d+)/$', login_required(views.SolutionView.as_view()), name='student_load_solution'),
    url(r'^ajax/load-proof-response/$', views.load_proof_response, name='load_proof_response'),
    url(r'^ajax/save-proof-response/$', views.save_proof_response, name='save_proof_response'),
]
