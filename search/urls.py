from django.conf.urls import include,url
from django.contrib.auth.decorators import login_required

from . import views
#from views import TestDelete

urlpatterns = [
    url(r'^$', views.searchform, name='searchform'),
    url(r'^results/$', views.searchresults, name='searchresults'),
    url(r'^advanced_results/$', views.advanced_searchresults, name='advancedsearchresults'),
    url(r'^results/add_to_group/$', views.add_to_group, name='add_to_group'),
    url(r'^view_presets/$', views.view_presets, name='view_presets'),
    url(r'^advanced_results/add_to_group/$', views.add_to_group, name='add_to_group'),
    url(r'^ajax/load_sol/(?P<pk>\d+)/$', views.load_sols, name='search_load_solution'),
    url(r'^ajax/add-preset/$', views.add_preset, name='add_preset'),
    url(r'^ajax/load-edit-preset/$', views.load_edit_preset, name='load_edit_preset'),
    url(r'^ajax/save-preset/$', views.save_preset, name='save_preset'),
]
