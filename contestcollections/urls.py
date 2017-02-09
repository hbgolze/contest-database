from django.conf.urls import include,url

from . import views
#from views import TestDelete

urlpatterns = [
    url(r'^$', views.tableview, name='tableview'),
    url(r'^test/(?P<pk>\d+)/$', views.testview, name='testview'),
    url(r'^test/(?P<testpk>\d+)/(?P<pk>\d+)/$', views.solutionview, name='solutionview'),
]
