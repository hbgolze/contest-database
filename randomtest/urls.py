from django.conf.urls import include,url

from django.contrib.auth.decorators import login_required

from . import views
#from views import TestDelete

urlpatterns = [
    url(r'^$', views.splashview, name='splashview'),
    url(r'^randomtest/$', views.tableview, name='tableview'),
    url(r'^randomtest/createtest/$', views.startform, name='startform'),
    url(r'^randomtest/createtest/readme$', views.readme, name='readme'),
    url(r'^randomtest/test/(?P<pk>\d+)/$', views.testview, name='testview'),
    url(r'^randomtest/test/(?P<pk>\d+)/toggle_star/$', views.toggle_star, name='toggle_star'),
    url(r'^randomtest/test/(?P<pk>\d+)/checkanswer/$', views.checkanswer, name='checkanswer'),
    url(r'^randomtest/test/(?P<pk>\d+)/load_sol/(?P<ppk>\d+)/$', login_required(views.SolutionView.as_view()), name='load_solution'),
    url(r'^randomtest/newtest/(?P<pk>\d+)/$', views.newtestview, name='newtestview'),
    url(r'^randomtest/newtest/(?P<pk>\d+)/toggle_star/$', views.new_toggle_star, name='new_toggle_star'),
#    url(r'^newtest/(?P<pk>\d+)/checkanswer/$', views.checkanswer, name='checkanswer'),
    url(r'^randomtest/newtest/(?P<pk>\d+)/load_sol/(?P<ppk>\d+)/$', login_required(views.SolutionView.as_view()), name='load_solution'),
    url(r'^randomtest/delete/(?P<pk>\d+)/$', views.deletetestresponses,name='test_delete'),
#    url(r'^edittest/(?P<pk>\d+)/$', views.testeditview,name='test_edit'),
    url(r'^randomtest/viewlatex/(?P<pk>\d+)/$', views.latexview, name='view_latex'),
    url(r'^randomtest/viewlatexsol/(?P<pk>\d+)/$', views.latexsolview, name='view_latex_sol'),
    url(r'^randomtest/tagcounts/$', views.tagcounts, name='tag_counts'),
    url(r'^randomtest/pdftest/(?P<pk>\d+)/$', views.test_as_pdf,name='test_pdf'),
    url(r'^randomtest/pdfsoltest/(?P<pk>\d+)/$', views.test_sol_as_pdf,name='test_sol_pdf'),
    url(r'^randomtest/student/(?P<username>\w+)/$', views.tableview, name='studenttableview'),
    url(r'^randomtest/student/(?P<username>\w+)/addtest/(?P<pk>\w+)/$', views.addtestview, name='addstudenttestview'),
    url(r'^randomtest/student/(?P<username>\w+)/(?P<pk>\w+)/$', views.testview, name='studenttestview'),
    url(r'^randomtest/student/(?P<username>\w+)/viewlatex/(?P<pk>\d+)/$', views.latexview, name='view_latex'),
    url(r'^randomtest/student/(?P<username>\w+)/viewlatexsol/(?P<pk>\d+)/$', views.latexsolview, name='view_latex_sol'),
    url(r'^randomtest/student/(?P<username>\w+)/(?P<pk>\d+)/load_sol/(?P<ppk>\d+)/$', login_required(views.SolutionView.as_view()), name='load_solution'),
    url(r'^randomtest/student/(?P<username>\w+)/archive/(?P<tpk>\d+)/$', views.archivestudentview, name='archivestudentview'),
    url(r'^randomtest/student/(?P<username>\w+)/unarchive/(?P<tpk>\d+)/$', views.unarchivestudentview, name='unarchivestudentview'),
    url(r'^randomtest/student/(?P<username>\w+)/delete/(?P<pk>\d+)/$', views.deletestudenttestresponses,name='test_delete'),
    url(r'^randomtest/archive/(?P<tpk>\d+)/$', views.archiveview, name='archiveview'),
    url(r'^randomtest/unarchive/(?P<tpk>\d+)/$', views.unarchiveview, name='unarchiveview'),
    url(r'^randomtest/highscores/$', views.highscore, name='highscoreview'),
    url(r'^randomtest/highscores/(?P<username>\w+)/$', views.highscore, name='highscoreview'),
    url(r'^randomtest/addfolder/(?P<pk>\w+)/$',views.addfolderview,name='addfolderview'),
    url(r'^randomtest/addtest/(?P<pk>\w+)/$',views.addtestview,name='addtestview'),
    url(r'^randomtest/urltest/$',views.urltemptest,name='urltemptest'),
    url(r'^randomtest/urltest/test$',views.urltest,name='urltestview'),
    url(r'^randomtest/urltest/latex$', views.urllatexview, name='urlview_latex'),
    url(r'^randomtest/urltest/latexsol$', views.urllatexsolview, name='urlview_latex'),
    url(r'^randomtest/profiles/(?P<username>\w+)/',views.profileview,name='profileview'),
    url(r'^randomtest/newcreatetest/$', views.newstartform, name='startform2'),
    url(r'^randomtest/editnewtest/(?P<pk>\d+)/$', views.editnewtestview, name='editnewtestview'),
    url(r'^randomtest/edittimezone/$',views.changetimezoneview,name='changetimezoneview'),
    
]
