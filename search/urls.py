from django.conf.urls import include,url

from . import views
#from views import TestDelete

urlpatterns = [
    url(r'^$', views.searchform, name='searchform'),
    url(r'^results/$', views.searchresults, name='searchresults'),
]
