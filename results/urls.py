from django.urls import path

from . import views
#from views import TestDelete

urlpatterns = [
    path('', views.all_contests, name='all_contests'),
    path('<str:contest_name>/', views.contest_view, name='contest_view'),
    path('<str:contest_name>/organizations/', views.organization_view, name='organization_view'),
    path('<str:contest_name>/organizations/<str:org_pk>/', views.organization_team_view, name='organization_team_view'),
    path('<str:contest_name>/indiv_problems/', views.individual_ranks, name='individual_ranks'),
    path('<str:contest_name>/<str:year>/', views.contestyear_view, name='contestyear_view'),
]
