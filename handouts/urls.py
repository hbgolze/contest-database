from django.conf.urls import include,url

from . import views

urlpatterns = [
#    url(r'^$', views.tableview, name='tableview'),
    url(r'^edit/(?P<pk>\d+)/$', views.handouteditview, name='handouteditview'),
]
