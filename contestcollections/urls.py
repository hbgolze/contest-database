from django.conf.urls import include,url


from django.contrib.auth.decorators import login_required

from . import views
#from views import TestDelete

urlpatterns = [
    url(r'^$', views.tableview, name='cctableview'),
    url(r'^test/(?P<pk>\d+)/$', views.testview, name='cctestview'),
    url(r'^test/pdf/(?P<pk>\d+)/$', views.test_as_pdf, name='ccpdfview'),
    url(r'^test/(?P<testpk>\d+)/(?P<pk>\d+)/$', views.solutionview, name='ccsolutionview'),
#    url(r'^test/(?P<testpk>\d+)/load_sol/(?P<pk>\d+)/$', views.load_solution, name='load_solution'),
    url(r'^test/(?P<testpk>\d+)/load_sol/(?P<pk>\d+)/?$', login_required(views.SolutionView.as_view()), name='cc_load_solution'),
    url(r'^test/(?P<pk>\d+)/pdfoptions/$', views.testpdfoptions, name='cctestpdfoptions'),
    url(r'^test/(?P<pk>\d+)/pdfoptions/problems/$', views.problempdf, name='ccproblempdf'),
    url(r'^test/(?P<pk>\d+)/pdfoptions/solutions/$', views.solutionpdf, name='ccsolutionpdf'),
    url(r'^test/(?P<pk>\d+)/pdfoptions/answerkey/$', views.answerkeypdf, name='ccanswerkeypdf'),
    url(r'^test/(?P<pk>\d+)/pdfoptions/viewlatex/$', views.latexview, name='ccviewlatex'),

]
