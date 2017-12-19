from django.conf.urls import include,url

from . import views
from .forms import AddProblemForm1,AddProblemForm2MC,AddProblemForm2SA,AddProblemForm2PF,AddProblemForm2MCSA,AddProblemForm3,UploadContestForm
from .views import AddProblemWizard,show_mc_form_condition,show_sa_form_condition,show_pf_form_condition,show_mcsa_form_condition
from .views import show_mc_form_condition2,show_sa_form_condition2,show_pf_form_condition2,show_mcsa_form_condition2

from django.contrib.auth.decorators import login_required,user_passes_test

addproblem_forms = [AddProblemForm1,
                    AddProblemForm2MC,
                    AddProblemForm2SA,
                    AddProblemForm2PF,
                    AddProblemForm2MCSA,
                    AddProblemForm3,
                    ]

urlpatterns = [
    url(r'^myactivity/$', views.my_activity, name='my_activity'),
    url(r'^$', views.typeview, name='typeview'),
    url(r'^contest/bytag/(?P<type>\w+)/$', views.tagview, name='tagview'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/$', views.typetagview, name='typetagview'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/$', views.problemview, name='problemview'),
    url(r'^contest/bytest/(?P<type>\w+)/$', views.testview, name='testview'),
    url(r'^contest/bytest/(?P<type>\w+)/matrix/$', views.matrixview, name='matrixview'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<testlabel>\w+)/$', views.testlabelview, name='testlabelview'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/$', views.problemview, name='problemview'),
    url(r'^CM/bytopic/(?P<type>\w+)/$', views.CMtopicview, name='CMtopicview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/$', views.detailedproblemview, name='detailedproblemview'),
    url(r'^CM/bytag/(?P<type>\w+)/$', views.tagview, name='tagview'),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/$', views.CMtypetagview, name='typetagview'),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/$', views.detailedproblemview, name='detailedproblemview'),
    url(r'^addproblemform/$',AddProblemWizard.as_view(addproblem_forms,condition_dict={'1':show_mc_form_condition,'2':show_sa_form_condition,'3':show_pf_form_condition,'4':show_mcsa_form_condition,})),
    url(r'^addcontest/(?P<type>\w+)/(?P<num>\w+)/$',views.addcontestview, name='addcontestview'),
    url(r'^uploadcontest/$',views.uploadcontestview, name='uploadcontestview'),

    url(r'^tameuploadcontest/$',views.tameupload, name='tameupload'),
    url(r'^tameuploadcontest/preview/$',views.uploadpreview, name='uploadpreview'),
    url(r'^duplicateview/(?P<type_name>\w+)/$',views.duplicate_view, name='duplicate_view'),
    url(r'^redirectproblem/(?P<pk>\w+)/$',views.redirectproblem, name='redirect_problem_view'),
    url(r'^tags/$',views.tageditview,name='tageditview'),

    url(r'^tags/edit_tag/(?P<pk>\d+)/$', login_required(views.TagUpdateView.as_view()),name="update_tag"),
    url(r'^tags/add_tag/(?P<pk>\d+)/$', login_required(views.TagCreateView.as_view()),name="add_new_tag"),
    url(r'^tags/delete_tag/(?P<pk>\d+)/$', user_passes_test(lambda u: u.is_superuser)(views.TagDeleteView.as_view()),name="delete_tag"),
    url(r'^tags/info_tag/(?P<pk>\d+)/$', views.taginfoview,name="info_tag"),
    url(r'^tags/([\w-]+)/$', views.TagProblemList.as_view(),name="tag_problem_view"),
###########
    url(r'^ajax/remove_duplicate/$', views.remove_duplicate_problem, name='remove_duplicate'),
    url(r'^ajax/add_duplicate/$', views.add_duplicate_problem, name='add_duplicate'),
    url(r'^ajax/load-edit-answer/$', views.load_edit_answer, name='load_edit_answer'),
    url(r'^ajax/load-edit-latex/$', views.load_edit_latex, name='load_edit_latex'),
    url(r'^ajax/save-latex/$', views.save_latex, name='save_latex'),
    url(r'^ajax/save-answer/$', views.save_answer, name='save_answer'),
    url(r'^ajax/load_sol/(?P<pk>\w+)/$', login_required(views.SolutionView.as_view()), name='load_solution'),
    url(r'^ajax/load-edit-sol/$', views.load_edit_sol, name='load_edit_solution'),
    url(r'^ajax/save-sol/$', views.save_sol, name='save_solution'),
    url(r'^ajax/load-new-solution/$', views.load_new_solution, name='load_new_solution'),
    url(r'^ajax/save-new-solution/$', views.save_new_solution, name='save_new_solution'),
    url(r'^ajax/delete-solution/$', views.delete_sol, name='delete_sol'),
    url(r'^ajax/add_tag/$', views.add_tag, name='add_tag'),
    url(r'^ajax/delete_tag/$', views.delete_tag, name='delete_tag'),
    url(r'^ajax/change-qt/$', views.change_qt, name='change_qt'),
    url(r'^ajax/change-qt-load/$', views.change_qt_load, name='change_qt_load'),
    url(r'^ajax/save-qt/$', views.save_qt, name='save_qt'),
    url(r'^ajax/load-change-difficulty/$', views.load_change_difficulty, name='load_change_difficulty'),
    url(r'^ajax/save-difficulty/$', views.save_difficulty, name='save_difficulty'),
    url(r'^ajax/load-edit-review/$', views.load_edit_review, name='load_edit_review'),
    url(r'^ajax/new-review/$', views.new_review, name='new_review'),
    url(r'^ajax/save-new-review/$', views.save_new_review, name='save_new_review'),
    url(r'^ajax/save-review/$', views.save_review, name='save_review'),
    url(r'^ajax/new-comment/$', views.new_comment, name='new_comment'),
    url(r'^ajax/save-comment/$', views.save_comment, name='save_comment'),
    url(r'^ajax/delete-comment/$', views.delete_comment, name='delete_comment'),
#    url(r'^tameuploadcontest/preview/$',views.ContestUploadPreview(UploadContestForm), name='uploadpreview'),
#    url(r'^bytag/(?P<type>\w+)/untagged/$', views.untaggedview, name='untaggedview'),
#    url(r'^bytest/(?P<type>\w+)/untagged/$', views.untaggedview, name='untaggedview'),
#    url(r'^untagged/(?P<type>\w+)/$', views.untaggedview, name='untaggedview'),
]
