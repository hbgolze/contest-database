from django.conf.urls import include,url

from . import views
#from views import TestDelete

urlpatterns = [
    url(r'^$', views.tableview, name='tableview'),
    url(r'^createtest/$', views.startform, name='startform'),
    url(r'^createtest/readme$', views.readme, name='readme'),
    url(r'^test/(?P<pk>\d+)/$', views.testview, name='testview'),
    url(r'^test/(?P<testpk>\d+)/(?P<pk>\d+)/$', views.solutionview, name='solutionview'),
    url(r'^delete/(?P<pk>\d+)/$', views.deletetestresponses,name='test_delete'),
    url(r'^edittest/(?P<pk>\d+)/$', views.testeditview,name='test_edit'),
    url(r'^viewlatex/(?P<pk>\d+)/$', views.latexview, name='view_latex'),
    url(r'^viewlatexsol/(?P<pk>\d+)/$', views.latexsolview, name='view_latex_sol'),
    url(r'^tagcounts/$', views.tagcounts, name='tag_counts'),
    url(r'^pdftest/(?P<pk>\d+)/$', views.test_as_pdf,name='test_pdf'),
    url(r'^pdfsoltest/(?P<pk>\d+)/$', views.test_sol_as_pdf,name='test_sol_pdf'),
    url(r'^student/(?P<username>\w+)/$', views.tableview, name='studenttableview'),
    url(r'^student/(?P<username>\w+)/addtest/(?P<pk>\w+)/$', views.addtestview, name='addstudenttestview'),
    url(r'^student/(?P<username>\w+)/(?P<pk>\w+)/$', views.testview, name='studenttestview'),
    url(r'^student/(?P<username>\w+)/archive/(?P<tpk>\d+)/$', views.archivestudentview, name='archivestudentview'),
    url(r'^student/(?P<username>\w+)/unarchive/(?P<tpk>\d+)/$', views.unarchivestudentview, name='unarchivestudentview'),
    url(r'^student/(?P<username>\w+)/delete/(?P<pk>\d+)/$', views.deletestudenttestresponses,name='test_delete'),
    url(r'^student/(?P<username>\w+)/(?P<testpk>\w+)/(?P<pk>\w+)/$', views.solutionview, name='studentsolutionview'),
    url(r'^archive/(?P<tpk>\d+)/$', views.archiveview, name='archiveview'),
    url(r'^unarchive/(?P<tpk>\d+)/$', views.unarchiveview, name='unarchiveview'),
    url(r'^highscores/$', views.highscore, name='highscoreview'),
    url(r'^highscores/(?P<username>\w+)/$', views.highscore, name='highscoreview'),
    url(r'^addfolder/(?P<pk>\w+)/$',views.addfolderview,name='addfolderview'),
    url(r'^addtest/(?P<pk>\w+)/$',views.addtestview,name='addtestview'),
    url(r'^urltest/$',views.urltemptest,name='urltemptest'),
    url(r'^urltest/test$',views.urltest,name='urltestview'),
    url(r'^urltest/latex$', views.urllatexview, name='urlview_latex'),
    url(r'^urltest/latexsol$', views.urllatexsolview, name='urlview_latex'),
    url(r'^profiles/(?P<username>\w+)/',views.profileview,name='profileview'),
    url(r'^newcreatetest/$', views.newstartform, name='startform2'),
    url(r'^newtest/(?P<pk>\d+)/$', views.editnewtestview, name='editnewtestview'),
]
