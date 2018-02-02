from django.conf.urls import include,url

from . import views
#from views import TestDelete

urlpatterns = [
    url(r'^$', views.tableview, name='g_tableview'),
    url(r'^tags/$', views.tagtableview, name='tagtableview'),
    url(r'^tags/(?P<pk>\d+)/$', views.viewtaggroup, name='viewtaggroup'),
    url(r'^(?P<pk>\d+)/$', views.viewproblemgroup, name='viewproblemgroup'),
    url(r'^(?P<pk>\d+)/delete/$', views.deletegroup, name='deletegroup'),
    url(r'^ajax/savegroup/$', views.savegroup, name='savegroup'),
    url(r'^ajax/create-test/$', views.create_test, name='g_createtest'),
    url(r'^ajax/edit-sharing/$', views.load_sharing_modal, name='edit_sharing'),
    url(r'^ajax/share-with-user/$', views.share_with_user, name='share_with_user'),
    url(r'^ajax/change-permission/$', views.change_permission, name='change_permission'),
]
