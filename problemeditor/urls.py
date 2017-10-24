from django.conf.urls import include,url

from . import views
from .forms import AddProblemForm1,AddProblemForm2MC,AddProblemForm2SA,AddProblemForm2PF,AddProblemForm2MCSA,AddProblemForm3,ChangeQuestionTypeForm1,ChangeQuestionTypeForm2MC,ChangeQuestionTypeForm2SA,ChangeQuestionTypeForm2PF,ChangeQuestionTypeForm2MCSA,UploadContestForm
from .views import AddProblemWizard,ChangeQuestionTypeWizard,show_mc_form_condition,show_sa_form_condition,show_pf_form_condition,show_mcsa_form_condition
from .views import show_mc_form_condition2,show_sa_form_condition2,show_pf_form_condition2,show_mcsa_form_condition2

from django.contrib.auth.decorators import login_required,user_passes_test

addproblem_forms = [AddProblemForm1,
                    AddProblemForm2MC,
                    AddProblemForm2SA,
                    AddProblemForm2PF,
                    AddProblemForm2MCSA,
                    AddProblemForm3,
                    ]
changequestiontype_forms = [ChangeQuestionTypeForm1,
                            ChangeQuestionTypeForm2MC,
                            ChangeQuestionTypeForm2SA,
                            ChangeQuestionTypeForm2PF,
                            ChangeQuestionTypeForm2MCSA,
                            ]

urlpatterns = [
    url(r'^myactivity/$', views.my_activity, name='my_activity'),
    url(r'^$', views.typeview, name='typeview'),
    url(r'^contest/bytag/(?P<type>\w+)/$', views.tagview, name='tagview'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/$', views.typetagview, name='typetagview'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/remove_duplicate/$', views.remove_duplicate_problem, name='remove_duplicate'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/add_duplicate/$', views.add_duplicate_problem, name='add_duplicate'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/load-edit-answer/$', views.load_edit_answer, name='load_edit_answer'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/load-edit-latex/$', views.load_edit_latex, name='load_edit_latex'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/save-latex/$', views.save_latex, name='save_latex'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/save-answer/$', views.save_answer, name='save_answer'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/load_sol/(?P<pk>\w+)/$', login_required(views.SolutionView.as_view()), name='load_solution'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/load-new-solution/$', views.load_new_solution, name='load_new_solution'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/save-new-solution/$', views.save_new_solution, name='save_new_solution'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/delete-solution/$', views.delete_sol, name='delete_sol'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/$', views.problemview, name='problemview'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/remove_duplicate/(?P<pk>\w+)/$', views.remove_duplicate, name='rm_duplicate'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/edittext/$', views.editproblemtextview, name='editproblemview'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/editanswer/$', views.editanswerview, name='editanswerview'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/newsolution/$', views.newsolutionview, name='newsolutionview'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/editsolution/(?P<spk>\w+)/$', views.editsolutionview, name='editsolutionview'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/edit_solution/(?P<spk>\w+)/$', login_required(views.SolutionUpdateView.as_view()), name='edit_solution_bytag'),####modal version
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/deletesolution/(?P<spk>\w+)/$', views.SolutionDeleteView.as_view(), name='delete_solution'),

    url(r'^contest/bytest/(?P<type>\w+)/$', views.testview, name='testview'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<testlabel>\w+)/$', views.testlabelview, name='testlabelview'),#want to make this display the problems...maybe?...or maybe have a summary view, too?
    url(r'^contest/bytest/(?P<type>\w+)/(?P<testlabel>\w+)/add_duplicate/$', views.add_duplicate_problem, name='add_duplicate'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<testlabel>\w+)/load-edit-answer/$', views.load_edit_answer, name='load_edit_answer'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<testlabel>\w+)/load-edit-latex/$', views.load_edit_latex, name='load_edit_latex'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<testlabel>\w+)/save-latex/$', views.save_latex, name='save_latex'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<testlabel>\w+)/save-answer/$', views.save_answer, name='save_answer'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<testlabel>\w+)/load_sol/(?P<pk>\w+)/$', login_required(views.SolutionView.as_view()), name='load_solution'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<testlabel>\w+)/load-new-solution/$', views.load_new_solution, name='load_new_solution'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<testlabel>\w+)/save-new-solution/$', views.save_new_solution, name='save_new_solution'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<testlabel>\w+)/delete-solution/$', views.delete_sol, name='delete_sol'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/$', views.problemview, name='problemview'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/remove_duplicate/(?P<pk>\w+)/$', views.remove_duplicate, name='rm_duplicate'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/edittext/$', views.editproblemtextview, name='editproblemview'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/editanswer/$', views.editanswerview, name='editanswerview'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/newsolution/$', views.newsolutionview, name='newsolutionview'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/editsolution/(?P<spk>\w+)/$', views.editsolutionview, name='editsolutionview'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/edit_solution/(?P<spk>\w+)/$', login_required(views.SolutionUpdateView.as_view()), name='edit_solution'),####modal version
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/deletesolution/(?P<spk>\w+)/$', views.SolutionDeleteView.as_view(), name='delete_solution'),
    url(r'^CM/bytopic/(?P<type>\w+)/$', views.CMtopicview, name='CMtopicview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/$', views.detailedproblemview, name='detailedproblemview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/edittext/$', views.editproblemtextpkview, name='editproblemtextpkview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/editsolution/(?P<spk>\w+)/$', views.editsolutionpkview, name='editsolutionpkview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/newsolution/$', views.newsolutionpkview, name='newsolutionpkview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/editreview/(?P<apk>\w+)/$', views.editreviewpkview, name='editreviewpkview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/newreview/$', views.newreviewpkview, name='newreviewpkview'),
#    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/deletesolution/(?P<spk>\w+)/$', views.deletesolutionpkview, name='deletesolutionpkview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/deletesolution/(?P<spk>\w+)/$', views.SolutionDeleteView.as_view(), name='delete_solution'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/newcomment/$', views.newcommentpkview, name='newcommentpkview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/deletecomment/(?P<cpk>\w+)/$', views.deletecommentpkview, name='deletecommentpkview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/edit_solution/(?P<spk>\w+)/$', login_required(views.CMSolutionUpdateView.as_view()), name='CM_edit_solution'),####modal version
    url(r'^CM/bytag/(?P<type>\w+)/$', views.CMtagview, name='tagview'),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/$', views.CMtypetagview, name='typetagview'),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/$', views.detailedproblemview, name='detailedproblemview'),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/edittext/$', views.editproblemtextpkview, name='editproblemview'),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/editsolution/(?P<spk>\w+)/$', views.editsolutionpkview, name='solutionview'),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/newsolution/$', views.newsolutionpkview, name='newsolutionpkview'),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/editreview/(?P<apk>\w+)/$', views.editreviewpkview, name='reviewview'),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/newreview/$', views.newreviewpkview, name='newreviewpkview'),
#    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/deletesolution/(?P<spk>\w+)/$', views.deletesolutionpkview, name='deletesolutionpkview')
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/deletesolution/(?P<spk>\w+)/$', views.SolutionDeleteView.as_view(), name='delete_solution'),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/newcomment/$', views.newcommentpkview, name='newcommentpkview'),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/deletecomment/(?P<cpk>\w+)/$', views.deletecommentpkview, name='deletecommentpkview'),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/edit_solution/(?P<spk>\w+)/$', login_required(views.CMSolutionUpdateView.as_view()), name='CM_edit_solution_bytag'),####modal version
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/change_question_type$',ChangeQuestionTypeWizard.as_view(changequestiontype_forms,condition_dict={'1':show_mc_form_condition2,'2':show_sa_form_condition2,'3':show_pf_form_condition2,'4':show_mcsa_form_condition2,})),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tagstatus>\w+)/(?P<pk>\w+)/change_question_type$',ChangeQuestionTypeWizard.as_view(changequestiontype_forms,condition_dict={'1':show_mc_form_condition2,'2':show_sa_form_condition2,'3':show_pf_form_condition2,'4':show_mcsa_form_condition2,})),
    url(r'^addproblemform/$',AddProblemWizard.as_view(addproblem_forms,condition_dict={'1':show_mc_form_condition,'2':show_sa_form_condition,'3':show_pf_form_condition,'4':show_mcsa_form_condition,})),
    url(r'^addcontest/(?P<type>\w+)/(?P<num>\w+)/$',views.addcontestview, name='addcontestview'),
    url(r'^uploadcontest/$',views.uploadcontestview, name='uploadcontestview'),

    url(r'^tameuploadcontest/$',views.tameupload, name='tameupload'),
    url(r'^tameuploadcontest/preview/$',views.uploadpreview, name='uploadpreview'),
    url(r'^duplicateview/(?P<type_name>\w+)/$',views.duplicate_view, name='duplicate_view'),
    url(r'^redirectproblem/(?P<pk>\w+)/$',views.redirectproblem, name='redirect_problem_view'),
    url(r'^tags/$',views.tageditview,name='tageditview'),

    url(r'^tags/edit_tag/(?P<pk>\d+)/$', login_required(views.TagUpdateView.as_view()),name="update_tag"),
    url(r'^tags/add_tag/(?P<pk>\d+)/$', login_required(views.TagCreateView.as_view()),name="add_tag"),
    url(r'^tags/delete_tag/(?P<pk>\d+)/$', user_passes_test(lambda u: u.is_superuser)(views.TagDeleteView.as_view()),name="delete_tag"),
    url(r'^tags/info_tag/(?P<pk>\d+)/$', views.taginfoview,name="info_tag"),
    url(r'^tags/([\w-]+)/$', views.TagProblemList.as_view(),name="tag_problem_view"),
#    url(r'^tameuploadcontest/preview/$',views.ContestUploadPreview(UploadContestForm), name='uploadpreview'),
#    url(r'^bytag/(?P<type>\w+)/untagged/$', views.untaggedview, name='untaggedview'),
#    url(r'^bytest/(?P<type>\w+)/untagged/$', views.untaggedview, name='untaggedview'),
#    url(r'^untagged/(?P<type>\w+)/$', views.untaggedview, name='untaggedview'),
]
