from django.conf.urls import include,url

from . import views

urlpatterns = [
    url(r'^$', views.typeview, name='typeview'),
    url(r'^bytag/(?P<type>\w+)/$', views.tagview, name='tagview'),
    url(r'^bytest/(?P<type>\w+)/$', views.testview, name='testview'),
    url(r'^bytag/(?P<type>\w+)/(?P<tag>\w+)/$', views.typetagview, name='typetagview'),
    url(r'^bytest/(?P<type>\w+)/(?P<testlabel>\w+)/$', views.testlabelview, name='testlabelview'),
    url(r'^bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/$', views.problemview, name='problemview'),
    url(r'^bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/$', views.problemview, name='problemview'),
    url(r'^bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/solutions/$', views.solutionview, name='solutionview'),
    url(r'^bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/solutions/$', views.solutionview, name='solutionview'),
    url(r'^bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/solutions/new/$', views.newsolutionview, name='newsolutionview'),
    url(r'^bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/solutions/new/$', views.newsolutionview, name='newsolutionview'),
#    url(r'^bytag/(?P<type>\w+)/untagged/$', views.untaggedview, name='untaggedview'),
#    url(r'^bytest/(?P<type>\w+)/untagged/$', views.untaggedview, name='untaggedview'),


#    url(r'^untagged/(?P<type>\w+)/$', views.untaggedview, name='untaggedview'),
]
