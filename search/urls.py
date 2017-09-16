from django.conf.urls import include,url

from . import views
#from views import TestDelete

urlpatterns = [
    url(r'^$', views.searchform, name='searchform'),
    url(r'^results/$', views.searchresults, name='searchresults'),
    url(r'^results/add_to_group/$', views.add_to_group, name='add_to_group'),
    url(r'^results/add_tag/$', views.add_tag, name='add_tag'),
    url(r'^results/delete_tag/$', views.delete_tag, name='delete_tag'),
]
