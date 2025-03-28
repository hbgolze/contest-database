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
    url(r'^ajax/edit-prob_group-name/$',views.editprobgroupname, name="editprobgroupname"),
    url(r'^ajax/edit-prob_group-description/$',views.editprobgroupdescription, name="editprobgroupdescription"),
    url(r'^ajax/save-prob_group-name/$',views.saveprobgroupname, name="saveprobgroupname"),
    url(r'^ajax/save-prob_group-description/$',views.saveprobgroupdescription, name="saveprobgroupdescription"),
    url(r'^(?P<pk>\d+)/pdf/$', views.test_as_pdf, name='pgpdfview'),
    url(r'^(?P<pk>\d+)/outlinepdf/$', views.outline_test_as_pdf, name='pgoutlinepdfview'),
    url(r'^(?P<pk>\d+)/outlinetex/$', views.outline_test_as_tex, name='pgoutlinetexview'),
    url(r'^(?P<pk>\d+)/twoatatimepdf/$', views.twoatatime_test_as_pdf, name='pgtwoatatimepdfview'),
    url(r'^(?P<pk>\d+)/drillpdf/$', views.drill_test_as_pdf, name='pgdrillpdfview'),
    url(r'^(?P<pk>\d+)/latex/$', views.latex_view, name='pglatexview'),
    url(r'^(?P<pk>\d+)/answerkey/$', views.group_answer_key_as_pdf, name='pganswerkeyview'),
    url(r'^(?P<pk>\d+)/search/$', views.searchform, name='pgsearchform'),
    url(r'^(?P<pk>\d+)/search/results/$', views.searchresults, name='searchresults'),
    url(r'^(?P<pk>\d+)/search/advanced_results/$', views.advanced_searchresults, name='advancedsearchresults'),
    url(r'^(?P<pk>\d+)/search/results/add_to_group/$', views.search_add_to_group, name='add_to_group'),
    url(r'^(?P<pk>\d+)/search/advanced_results/add_to_group/$', views.search_add_to_group, name='add_to_group'),
    url(r'^(?P<pk>\d+)/search/results/add_to_this_group/$', views.add_to_this_group, name='add_to_this_group'),
    url(r'^(?P<pk>\d+)/search/advanced_results/add_to_this_group/$', views.add_to_this_group, name='add_to_this_group'),
    url(r'^ajax/load_sol/(?P<pk>\d+)/$', views.load_sols, name='search_load_solution'),

]
