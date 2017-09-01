from django.conf.urls import include,url

from . import views
from .forms import AddProblemForm1,AddProblemForm2MC,AddProblemForm2SA,AddProblemForm2PF,AddProblemForm2MCSA,AddProblemForm3,ChangeQuestionTypeForm1,ChangeQuestionTypeForm2MC,ChangeQuestionTypeForm2SA,ChangeQuestionTypeForm2PF,ChangeQuestionTypeForm2MCSA
from .views import AddProblemWizard,ChangeQuestionTypeWizard,show_mc_form_condition,show_sa_form_condition,show_pf_form_condition,show_mcsa_form_condition
from .views import show_mc_form_condition2,show_sa_form_condition2,show_pf_form_condition2,show_mcsa_form_condition2

from django.contrib.auth.decorators import login_required

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
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/$', views.problemview, name='problemview'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/remove_duplicate/(?P<pk>\w+)/$', views.remove_duplicate, name='rm_duplicate'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/edittext/$', views.editproblemtextview, name='editproblemview'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/editanswer/$', views.editanswerview, name='editanswerview'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/newsolution/$', views.newsolutionview, name='newsolutionview'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/editsolution/(?P<spk>\w+)/$', views.editsolutionview, name='editsolutionview'),
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/edit_solution/(?P<spk>\w+)/$', login_required(views.SolutionUpdateView.as_view()), name='edit_solution_bytag'),####modal version
    url(r'^contest/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/deletesolution/(?P<spk>\w+)/$', views.deletesolutionview, name='deletesolutionview'),
    url(r'^contest/bytest/(?P<type>\w+)/$', views.testview, name='testview'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<testlabel>\w+)/$', views.testlabelview, name='testlabelview'),#want to make this display the problems...maybe?...or maybe have a summary view, too?
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/$', views.problemview, name='problemview'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/remove_duplicate/(?P<pk>\w+)/$', views.remove_duplicate, name='rm_duplicate'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/edittext/$', views.editproblemtextview, name='editproblemview'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/editanswer/$', views.editanswerview, name='editanswerview'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/newsolution/$', views.newsolutionview, name='newsolutionview'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/editsolution/(?P<spk>\w+)/$', views.editsolutionview, name='editsolutionview'),
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/edit_solution/(?P<spk>\w+)/$', login_required(views.SolutionUpdateView.as_view()), name='edit_solution'),####modal version
    url(r'^contest/bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/deletesolution/(?P<spk>\w+)/$', views.deletesolutionview, name='deletesolutionview'),
    url(r'^CM/bytopic/(?P<type>\w+)/$', views.CMtopicview, name='CMtopicview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/$', views.detailedproblemview, name='detailedproblemview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/edittext/$', views.editproblemtextpkview, name='editproblemtextpkview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/editsolution/(?P<spk>\w+)/$', views.editsolutionpkview, name='editsolutionpkview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/newsolution/$', views.newsolutionpkview, name='newsolutionpkview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/editreview/(?P<apk>\w+)/$', views.editreviewpkview, name='editreviewpkview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/newreview/$', views.newreviewpkview, name='newreviewpkview'),
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/deletesolution/(?P<spk>\w+)/$', views.deletesolutionpkview, name='deletesolutionpkview'),
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
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/deletesolution/(?P<spk>\w+)/$', views.deletesolutionpkview, name='deletesolutionpkview'),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/newcomment/$', views.newcommentpkview, name='newcommentpkview'),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/deletecomment/(?P<cpk>\w+)/$', views.deletecommentpkview, name='deletecommentpkview'),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/edit_solution/(?P<spk>\w+)/$', login_required(views.CMSolutionUpdateView.as_view()), name='CM_edit_solution_bytag'),####modal version
    url(r'^CM/bytopic/(?P<type>\w+)/(?P<pk>\w+)/change_question_type$',ChangeQuestionTypeWizard.as_view(changequestiontype_forms,condition_dict={'1':show_mc_form_condition2,'2':show_sa_form_condition2,'3':show_pf_form_condition2,'4':show_mcsa_form_condition2,})),
    url(r'^CM/bytag/(?P<type>\w+)/(?P<tagstatus>\w+)/(?P<pk>\w+)/change_question_type$',ChangeQuestionTypeWizard.as_view(changequestiontype_forms,condition_dict={'1':show_mc_form_condition2,'2':show_sa_form_condition2,'3':show_pf_form_condition2,'4':show_mcsa_form_condition2,})),
    url(r'^addproblemform/$',AddProblemWizard.as_view(addproblem_forms,condition_dict={'1':show_mc_form_condition,'2':show_sa_form_condition,'3':show_pf_form_condition,'4':show_mcsa_form_condition,})),
    url(r'^addcontest/(?P<type>\w+)/(?P<num>\w+)/$',views.addcontestview, name='addcontestview'),
#    url(r'^bytag/(?P<type>\w+)/untagged/$', views.untaggedview, name='untaggedview'),
#    url(r'^bytest/(?P<type>\w+)/untagged/$', views.untaggedview, name='untaggedview'),
#    url(r'^untagged/(?P<type>\w+)/$', views.untaggedview, name='untaggedview'),
]
