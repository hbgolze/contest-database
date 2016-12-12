from django.conf.urls import include,url

from . import views
from .forms import AddProblemForm1,AddProblemForm2MC,AddProblemForm2SA,AddProblemForm2PF,AddProblemForm2MCSA,AddProblemForm3,ChangeQuestionTypeForm1,ChangeQuestionTypeForm2MC,ChangeQuestionTypeForm2SA,ChangeQuestionTypeForm2PF,ChangeQuestionTypeForm2MCSA
from .views import AddProblemWizard,ChangeQuestionTypeWizard,show_mc_form_condition,show_sa_form_condition,show_pf_form_condition,show_mcsa_form_condition
from .views import show_mc_form_condition2,show_sa_form_condition2,show_pf_form_condition2,show_mcsa_form_condition2

addproblem_forms=[AddProblemForm1,AddProblemForm2MC,AddProblemForm2SA,AddProblemForm2PF,AddProblemForm2MCSA,AddProblemForm3,]
changequestiontype_forms=[ChangeQuestionTypeForm1,ChangeQuestionTypeForm2MC,ChangeQuestionTypeForm2SA,ChangeQuestionTypeForm2PF,ChangeQuestionTypeForm2MCSA,]

urlpatterns = [
    url(r'^$', views.typeview, name='typeview'),
    url(r'^bytag/(?P<type>\w+)/$', views.tagview, name='tagview'),
    url(r'^bytag/(?P<type>\w+)/(?P<tag>\w+)/$', views.typetagview, name='typetagview'),
    url(r'^bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/$', views.problemview, name='problemview'),
    url(r'^bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/edittext/$', views.editproblemtextview, name='editproblemview'),
    url(r'^bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/solutions/$', views.solutionview, name='solutionview'),
    url(r'^bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/solutions/new/$', views.newsolutionview, name='newsolutionview'),
    url(r'^bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/solutions/edit/(?P<spk>\w+)/$', views.editsolutionview, name='editsolutionview'),
    url(r'^bytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/solutions/delete/(?P<spk>\w+)/$', views.deletesolutionview, name='deletesolutionview'),
    url(r'^bytest/(?P<type>\w+)/$', views.testview, name='testview'),
    url(r'^bytest/(?P<type>\w+)/(?P<testlabel>\w+)/$', views.testlabelview, name='testlabelview'),
    url(r'^bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/$', views.problemview, name='problemview'),
    url(r'^bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/edittext/$', views.editproblemtextview, name='editproblemview'),
    url(r'^bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/solutions/$', views.solutionview, name='solutionview'),
    url(r'^bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/solutions/new/$', views.newsolutionview, name='newsolutionview'),
    url(r'^bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/solutions/edit/(?P<spk>\w+)/$', views.editsolutionview, name='editsolutionview'),
    url(r'^bytest/(?P<type>\w+)/(?P<tag>\w+)/(?P<label>\w+)/solutions/delete/(?P<spk>\w+)/$', views.deletesolutionview, name='deletesolutionview'),
    url(r'^newproblem/',views.addproblemview, name='addproblemview'),
    url(r'^detailedview/(?P<pk>\w+)/$', views.detailedproblemview, name='detailedproblemview'),
    url(r'^detailedview/(?P<pk>\w+)/edittext/$', views.editproblemtextpkview, name='editproblemtextpkview'),
    url(r'^detailedview/(?P<pk>\w+)/editsolution/(?P<spk>\w+)/$', views.editsolutionpkview, name='editsolutionpkview'),
    url(r'^detailedview/(?P<pk>\w+)/newsolution/$', views.newsolutionpkview, name='newsolutionpkview'),
    url(r'^detailedview/(?P<pk>\w+)/deletesolution/(?P<spk>\w+)/$', views.deletesolutionpkview, name='deletesolutionpkview'),
    url(r'^detailedview/(?P<pk>\w+)/newcomment/$', views.newcommentpkview, name='newcommentpkview'),
    url(r'^detailedview/(?P<pk>\w+)/deletecomment/(?P<cpk>\w+)/$', views.deletecommentpkview, name='deletecommentpkview'),
    url(r'^detailedview/(?P<pk>\w+)/editreview/(?P<apk>\w+)/$', views.editreviewpkview, name='editreviewpkview'),
    url(r'^detailedview/(?P<pk>\w+)/newreview/$', views.newreviewpkview, name='newreviewpkview'),
    url(r'^CMbytopic/(?P<type>\w+)/$', views.CMtopicview, name='CMtopicview'),
    url(r'^CMbytopic/(?P<type>\w+)/(?P<pk>\w+)/$', views.detailedproblemview, name='detailedproblemview'),
    url(r'^CMbytopic/(?P<type>\w+)/(?P<pk>\w+)/edittext/$', views.editproblemtextpkview, name='editproblemtextpkview'),
    url(r'^CMbytopic/(?P<type>\w+)/(?P<pk>\w+)/editsolution/(?P<spk>\w+)/$', views.editsolutionpkview, name='editsolutionpkview'),
    url(r'^CMbytopic/(?P<type>\w+)/(?P<pk>\w+)/newsolution/$', views.newsolutionpkview, name='newsolutionpkview'),
    url(r'^CMbytopic/(?P<type>\w+)/(?P<pk>\w+)/editreview/(?P<apk>\w+)/$', views.editreviewpkview, name='editreviewpkview'),
    url(r'^CMbytopic/(?P<type>\w+)/(?P<pk>\w+)/newreview/$', views.newreviewpkview, name='newreviewpkview'),
    url(r'^CMbytopic/(?P<type>\w+)/(?P<pk>\w+)/deletesolution/(?P<spk>\w+)/$', views.deletesolutionpkview, name='deletesolutionpkview'),
    url(r'^CMbytopic/(?P<type>\w+)/(?P<pk>\w+)/newcomment/$', views.newcommentpkview, name='newcommentpkview'),
    url(r'^CMbytopic/(?P<type>\w+)/(?P<pk>\w+)/deletecomment/(?P<cpk>\w+)/$', views.deletecommentpkview, name='deletecommentpkview'),
    url(r'^CMbytag/(?P<type>\w+)/$', views.CMtagview, name='tagview'),
    url(r'^CMbytag/(?P<type>\w+)/(?P<tag>\w+)/$', views.CMtypetagview, name='typetagview'),
    url(r'^CMbytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/$', views.detailedproblemview, name='detailedproblemview'),
    url(r'^CMbytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/edittext/$', views.editproblemtextpkview, name='editproblemview'),
    url(r'^CMbytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/editsolution/(?P<spk>\w+)/$', views.editsolutionpkview, name='solutionview'),
    url(r'^CMbytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/newsolution/$', views.newsolutionpkview, name='newsolutionpkview'),
    url(r'^CMbytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/editreview/(?P<apk>\w+)/$', views.editreviewpkview, name='reviewview'),
    url(r'^CMbytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/newreview/$', views.newreviewpkview, name='newreviewpkview'),
    url(r'^CMbytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/deletesolution/(?P<spk>\w+)/$', views.deletesolutionpkview, name='deletesolutionpkview'),
    url(r'^CMbytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/newcomment/$', views.newcommentpkview, name='newcommentpkview'),
    url(r'^CMbytag/(?P<type>\w+)/(?P<tag>\w+)/(?P<pk>\w+)/deletecomment/(?P<cpk>\w+)/$', views.deletecommentpkview, name='deletecommentpkview'),
    url(r'^addproblemform/$',AddProblemWizard.as_view(addproblem_forms,condition_dict={'1':show_mc_form_condition,'2':show_sa_form_condition,'3':show_pf_form_condition,'4':show_mcsa_form_condition,})),
    url(r'^detailedview/(?P<pk>\w+)/change_question_type$',ChangeQuestionTypeWizard.as_view(changequestiontype_forms,condition_dict={'1':show_mc_form_condition2,'2':show_sa_form_condition2,'3':show_pf_form_condition2,'4':show_mcsa_form_condition2,})),
    url(r'^CMbytopic/(?P<type>\w+)/(?P<pk>\w+)/change_question_type$',ChangeQuestionTypeWizard.as_view(changequestiontype_forms,condition_dict={'1':show_mc_form_condition2,'2':show_sa_form_condition2,'3':show_pf_form_condition2,'4':show_mcsa_form_condition2,})),
    url(r'^CMbytag/(?P<type>\w+)/(?P<tagstatus>\w+)/(?P<pk>\w+)/change_question_type$',ChangeQuestionTypeWizard.as_view(changequestiontype_forms,condition_dict={'1':show_mc_form_condition2,'2':show_sa_form_condition2,'3':show_pf_form_condition2,'4':show_mcsa_form_condition2,})),
#    url(r'^bytag/(?P<type>\w+)/untagged/$', views.untaggedview, name='untaggedview'),
#    url(r'^bytest/(?P<type>\w+)/untagged/$', views.untaggedview, name='untaggedview'),
#    url(r'^untagged/(?P<type>\w+)/$', views.untaggedview, name='untaggedview'),
]
