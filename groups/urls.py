from django.conf.urls import include,url

from . import views
#from views import TestDelete

urlpatterns = [
    url(r'^$', views.tableview, name='g_tableview'),
    url(r'^archived/$', views.archivedtableview, name='g_archived_tableview'),
    url(r'^tags/$', views.tagtableview, name='tagtableview'),
    url(r'^tags/(?P<pk>\d+)/$', views.viewtaggroup, name='viewtaggroup'),
    url(r'^(?P<pk>\d+)/$', views.viewproblemgroup, name='viewproblemgroup'),
    url(r'^(?P<pk>\d+)/edit/$', views.edit_pg_view, name='editproblemgroup'),
    url(r'^ajax/savegroup/$', views.savegroup, name='savegroup'),
    url(r'^ajax/create-test/$', views.create_test, name='g_createtest'),
    url(r'^ajax/edit-sharing/$', views.load_sharing_modal, name='edit_sharing'),
    url(r'^ajax/share-with-user/$', views.share_with_user, name='share_with_user'),
    url(r'^ajax/change-permission/$', views.change_permission, name='change_permission'),
    url(r'^ajax/delete-group/$', views.delete_group, name='delete_group'),
    url(r'^ajax/remove-group/$', views.remove_group, name='remove_group'),
    url(r'^ajax/archive-group/$', views.archive_group, name='archive_group'),
    url(r'^ajax/unarchive-group/$', views.unarchive_group, name='unarchive_group'),
    url(r'^ajax/add-to-group/$', views.add_to_group, name='groups_add_to_group'),
    url(r'^ajax/fetch-problems/$', views.fetch_problems, name='groups_fetch_problems'),
    url(r'^ajax/new-problemgroup/$', views.newproblemgroup, name='groups_new_pg'),
    url(r'^(?P<pk>\d+)/pdf/$', views.test_as_pdf, name='pgpdfview'),
    url(r'^(?P<pk>\d+)/latex/$', views.latex_view, name='pglatexview'),
    url(r'^(?P<pk>\d+)/answerkey/$', views.group_answer_key_as_pdf, name='pganswerkeyview'),
]
