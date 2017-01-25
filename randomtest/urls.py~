from django.conf.urls import include,url

from . import views
#from views import TestDelete

urlpatterns = [
    url(r'^$', views.tableview, name='tableview'),
    url(r'^createtest/$', views.startform, name='startform'),
    url(r'^createtest/readme$', views.readme, name='readme'),
    url(r'^test/(?P<pk>\d+)/$', views.testview, name='testview'),
    url(r'^delete/(?P<pk>\d+)/$', views.deletetestresponses,name='test_delete'),
    url(r'^edittest/(?P<pk>\d+)/$', views.testeditview,name='test_edit'),
    url(r'^viewlatex/(?P<pk>\d+)/$', views.latexview, name='view_latex'),
    url(r'^tagcounts/$', views.tagcounts, name='tag_counts'),
    url(r'^pdftest/(?P<pk>\d+)/$', views.test_as_pdf,name='test_pdf'),
]
