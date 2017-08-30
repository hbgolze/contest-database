from django.conf.urls import include,url

from . import views
#from views import TestDelete

urlpatterns = [
    url(r'^$', views.tableview, name='tableview'),
    url(r'^tags/$', views.tagtableview, name='tagtableview'),
    url(r'^tags/(?P<pk>\d+)/$', views.viewtaggroup, name='viewtaggroup'),
    url(r'^(?P<pk>\d+)/$', views.viewproblemgroup, name='viewproblemgroup'),
    url(r'^(?P<pk>\d+)/delete/$', views.deletegroup, name='deletegroup'),
]
