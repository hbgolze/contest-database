from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views
#from views import TestDelete

urlpatterns = [
    path('', views.searchform, name='searchform'),
    path('results/', views.searchresults, name='searchresults'),
    path('advanced_results/', views.advanced_searchresults, name='advancedsearchresults'),
    path('results/add_to_group/', views.add_to_group, name='add_to_group'),
    path('view_presets/', views.view_presets, name='view_presets'),
    path('advanced_results/add_to_group/', views.add_to_group, name='add_to_group'),
    path('ajax/load_sol/<int:pk>/', views.load_sols, name='search_load_solution'),
    path('ajax/add-preset/', views.add_preset, name='add_preset'),
    path('ajax/load-edit-preset/', views.load_edit_preset, name='load_edit_preset'),
    path('ajax/save-preset/', views.save_preset, name='save_preset'),
]
