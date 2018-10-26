from django.conf.urls import include,url

from . import views
#from views import TestDelete

urlpatterns = [
    url(r'^$', views.all_contests, name='all_contests'),
    url(r'^(?P<contest_name>\w+)/$', views.contest_view, name='contest_view'),
    url(r'^(?P<contest_name>\w+)/organizations/$', views.organization_view, name='organization_view'),
    url(r'^(?P<contest_name>\w+)/organizations/(?P<org_pk>\w+)/$', views.organization_team_view, name='organization_team_view'),
    url(r'^(?P<contest_name>\w+)/(?P<year>\w+)/$', views.contestyear_view, name='contestyear_view'),
]
