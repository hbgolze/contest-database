from django.conf.urls import include,url

from . import views

urlpatterns = [
    url(r'^$', views.typeview, name='typeview'),
    url(r'^tags/(?P<type>\w+)/$', views.tagview, name='tagview'),
    url(r'^tags/(?P<type>\w+)/(?P<tag>\w+)/$', views.typetagview, name='typetagview'),
    url(r'^problems/(?P<type>\w+)/(?P<label>\w+)/$', views.problemview, name='problemview'),
    url(r'^solutions/(?P<type>\w+)/(?P<label>\w+)/$', views.solutionview, name='solutionview'),
    url(r'^solutions/(?P<type>\w+)/(?P<label>\w+)/new$', views.newsolutionview, name='newsolutionview'),
    url(r'^untagged/(?P<type>\w+)/$', views.untaggedview, name='untaggedview'),
    url(r'^testlabel/(?P<type>\w+)/(?P<testlabel>\w+)/$', views.testlabelview, name='testlabelview'),
]
