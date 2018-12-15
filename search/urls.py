from django.conf.urls import include,url

from . import views
#from views import TestDelete

urlpatterns = [
    url(r'^$', views.searchform, name='searchform'),
    url(r'^results/$', views.searchresults, name='searchresults'),
    url(r'^advanced_results/$', views.advanced_searchresults, name='advancedsearchresults'),
    url(r'^results/add_to_group/$', views.add_to_group, name='add_to_group'),
    url(r'^advanced_results/add_to_group/$', views.add_to_group, name='add_to_group'),
]
