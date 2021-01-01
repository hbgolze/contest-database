from django.conf.urls import include,url

from django.contrib.auth.decorators import login_required

from . import views

import groups.views as gviews

urlpatterns = [
    url(r'^$', views.teacherview, name='teacherview'),
    url(r'^sync/(?P<pk>\d+)/$', views.sync_class, name='sync_class'),
    url(r'^editclass/(?P<pk>\d+)/$', views.classeditview, name='classeditview'),
    url(r'^editclass/(?P<pk>\d+)/latex/$', views.latexclassview, name='latexclassview'),
    url(r'^editclass/(?P<pk>\d+)/pdf/$', views.class_as_pdf, name='class_as_pdf'),
    url(r'^editclass/(?P<pk>\d+)/add-unit/$', views.newunitview, name='newunitview'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/$', views.uniteditview, name='uniteditview'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/add-problemset/$', views.newproblemsetview, name='newproblemsetview'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/add-slides/$', views.newslidesview, name='newslidesview'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/add-test/$', views.newtestview, name='newtestview'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/problemsetlatex/(?P<ppk>\d+)/$', views.latexpsetview, name='latexpsetview'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/newproblemsetlatex/(?P<ppk>\d+)/$', views.newlatexpsetview, name='newlatexpsetview'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/problemsetanswerkeylatex/(?P<ppk>\d+)/$', views.latexpsetanswerkeyview, name='latexpsetanswerkeyview'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/problemset/(?P<ppk>\d+)/$', views.problemseteditview, name='problemseteditview'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/problemset/(?P<ppk>\d+)/load-original-problem/$', views.loadoriginalproblemform, name='load-original-problem'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/problemset/(?P<ppk>\d+)/add-original-problem/$', views.addoriginalproblem, name='add-original-problem'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/problemset/(?P<ppk>\d+)/find-num-probs-matching-tag/$', views.numprobsmatching, name='numprobsmatching'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/problemset/(?P<ppk>\d+)/add-tagged-problems/$', views.reviewmatchingproblems, name='reviewmatchingproblems'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/problemset/(?P<ppk>\d+)/review-problem-group/$', views.reviewproblemgroup, name='reviewproblemgroup'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/problemset/(?P<ppk>\d+)/edit-point-value/(?P<pppk>\d+)/$', views.update_point_value, name='edit-point-value'),
#    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/problemset/(?P<ppk>\d+)/edit-question-type/(?P<pppk>\d+)/$', views.editquestiontype, name='edit-question-type'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/problemset/(?P<ppk>\d+)/change-qt-original-problem/$', views.loadcqtoriginalproblemform, name='loadcqtoriginalproblemform'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/problemset/(?P<ppk>\d+)/pdf/$', views.pset_as_pdf, name='pset_as_pdf'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/problemset/(?P<ppk>\d+)/latex/$', views.pset_as_latex, name='pset_as_latex'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/problemset/(?P<ppk>\d+)/sol-pdf/$', views.pset_sols_as_pdf, name='pset_sols_as_pdf'),
#slides
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slideslatex/(?P<ppk>\d+)/$', views.latexslidesview, name='latexslidesview'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/$', views.slideseditview, name='slideseditview'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/add-slide/$', views.newslideview, name='addslide'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/edit-slide/(?P<sspk>\d+)/$', views.editslideview, name='editslideview'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/edit-slide/(?P<sspk>\d+)/edit-textblock/(?P<tpk>\d+)/$', login_required(views.TextBlockUpdateView.as_view()),name="update_textblock"),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/edit-slide/(?P<sspk>\d+)/edit-theorem/(?P<tpk>\d+)/$', login_required(views.TheoremUpdateView.as_view()),name="update_theorem"),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/edit-slide/(?P<sspk>\d+)/edit-proof/(?P<tpk>\d+)/$', login_required(views.ProofUpdateView.as_view()),name="update_proof"),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/edit-slide/(?P<sspk>\d+)/load-original-problem/$', views.loadoriginalexampleproblemform, name='load-original-example-problem'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/edit-slide/(?P<sspk>\d+)/exampleoriginalqt/$', views.exampleoriginalqt, name='exampleoriginalqt'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/edit-slide/(?P<sspk>\d+)/exampleproblemlabel/$', views.exampleproblemlabel, name='exampleproblemlabel'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/edit-slide/(?P<sspk>\d+)/example-problem-groups/$', views.exampleproblemgroups, name='exampleproblemgroups'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/edit-slide/(?P<sspk>\d+)/load-problem-group/$', views.exampleproblemgroupproblems, name='loadproblemgroup'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/edit-slide/(?P<sspk>\d+)/add-problem/$', views.exampleaddproblem, name='exampleaddproblem'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/edit-slide/(?P<sspk>\d+)/load-bytag/$', views.examplebytag, name='examplebytag'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/edit-slide/(?P<sspk>\d+)/load-problems-bytag/$', views.examplebytagproblems, name='examplebytagproblems'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/edit-slide/(?P<sspk>\d+)/edit-exampleproblem/(?P<sopk>\d+)/$', views.editexampleproblem, name='editexampleproblem'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/slides/(?P<spk>\d+)/edit-slide/(?P<sspk>\d+)/change-qt/$', views.loadcqtexampleproblemform, name='loadcqtexampleproblemform'),
# all functions must be added...unless consolidation.
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<tpk>\d+)/$', views.testeditview, name='testeditview'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/load-original-problem/$', views.testloadoriginalproblemform, name='test-load-original-problem'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/add-original-problem/$', views.testaddoriginalproblem, name='testadd-original-problem'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/find-num-probs-matching-tag/$', views.testnumprobsmatching, name='testnumprobsmatching'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/add-tagged-problems/$', views.testreviewmatchingproblems, name='testreviewmatchingproblems'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/review-problem-group/$', views.testreviewproblemgroup, name='testreviewproblemgroup'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/edit-point-value/(?P<pppk>\d+)/$', views.testupdate_point_value, name='testedit-point-value'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/edit-blank-point-value/(?P<pppk>\d+)/$', views.testupdate_blank_value, name='testedit-blank-value'),
#    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/edit-question-type/(?P<pppk>\d+)/$', views.testeditquestiontype, name='testedit-question-type'),
    url(r'^editclass/(?P<pk>\d+)/units/(?P<upk>\d+)/test/(?P<ppk>\d+)/change-qt-original-problem/$', views.testloadcqtoriginalproblemform, name='testloadcqtoriginalproblemform'),

#problemgroups
    url(r'^mystudents/$', views.studentmanager, name='studentmanager'),
    url(r'^mystudents/(?P<username>\w+)/$', views.studentclassview, name='studentclassview'),
    url(r'^mystudents/(?P<username>\w+)/problemset/(?P<upk>\w+)/$', views.studentproblemsetview, name='studentproblemsetview'),
    url(r'^mystudents/(?P<username>\w+)/problemset/(?P<upk>\w+)/load_grade/$', views.load_grade, name='load_grade'),
    url(r'^mystudents/(?P<username>\w+)/problemset/(?P<upk>\w+)/save_grade/$', views.save_grade, name='save_grade'),
    url(r'^mystudents/(?P<username>\w+)/problemset/(?P<upk>\d+)/load_sol/(?P<ppk>\d+)/$', login_required(views.SolutionView.as_view()), name='teacher_load_solution'),
    url(r'^mystudents/(?P<username>\w+)/slides/(?P<uspk>\w+)/$', views.slidesview, name='userslidesview'),
    url(r'^publishclass/(?P<pk>\d+)/$', views.publishview, name='publishview'),
    url(r'^class/(?P<pk>\d+)/$', views.currentclassview, name='currentclass'),
    url(r'^class/(?P<pk>\d+)/roster/$', views.rosterview, name='rosterview'),
    url(r'^class/(?P<pk>\d+)/roster/assignment/(?P<ppk>\d+)/$', views.assignmentview, name='assignmentview'),
    url(r'^class/(?P<pk>\d+)/roster/get-student-list/$', views.getstudentlist, name='getstudentlist'),
    url(r'^class/(?P<pk>\d+)/roster/add-student/$', views.addstudenttoclass, name='addstudent'),
    url(r'^class/(?P<pk>\d+)/roster/(?P<username>\w+)/$', views.studentoneclassview, name='studentoneclassview'),
    url(r'^class/(?P<pk>\d+)/roster/(?P<username>\w+)/problemset/(?P<upk>\w+)/$', views.studentproblemsetview, name='studentproblemsetview2'),
    url(r'^class/(?P<pk>\d+)/roster/(?P<username>\w+)/problemset/(?P<upk>\w+)/load_grade/$', views.load_grade, name='load_grade2'),
    url(r'^class/(?P<pk>\d+)/roster/(?P<username>\w+)/problemset/(?P<upk>\w+)/save_grade/$', views.save_grade, name='save_grade2'),
    url(r'^class/(?P<pk>\d+)/roster/(?P<username>\w+)/problemset/(?P<upk>\d+)/load_sol/(?P<ppk>\d+)/$', login_required(views.SolutionView.as_view()), name='teacher_load_solution2'),
    url(r'^class/(?P<pk>\d+)/slides/(?P<spk>\w+)/$', views.slidesview, name='slidesview'),
    url(r'^class/(?P<pk>\d+)/problemset/(?P<pspk>\w+)/$', views.teacherproblemsetview, name='teacherproblemsetview'),
    url(r'^class/(?P<pk>\w+)/problemset/(?P<pspk>\d+)/load_sol/(?P<ppk>\d+)/$', login_required(views.SolutionView.as_view()), name='teacher_load_solution2'),
    url(r'^class/(?P<pk>\d+)/problemset/(?P<pspk>\w+)/blind/(?P<popk>\w+)/$', views.blindgrade, name='blindgradingview'),
    url(r'^class/(?P<pk>\d+)/problemset/(?P<pspk>\w+)/blind/(?P<popk>\w+)/load_grade/$', views.load_grade, name='blindloadgrade'),
    url(r'^class/(?P<pk>\d+)/problemset/(?P<pspk>\w+)/blind/(?P<popk>\w+)/save_grade/$', views.save_grade, name='blindsavegrade'),
    url(r'^class/(?P<pk>\d+)/problemset/(?P<pspk>\w+)/blind/(?P<popk>\w+)/change_grade/$', views.change_grade, name='blindchangegrade'),
    url(r'^class/(?P<pk>\d+)/problemset/(?P<pspk>\w+)/alpha/(?P<popk>\w+)/$', views.alphagrade, name='alphagradingview'),
    url(r'^class/(?P<pk>\d+)/problemset/(?P<pspk>\w+)/alpha/(?P<popk>\w+)/load_grade/$', views.load_grade, name='alphaloadgrade'),
    url(r'^class/(?P<pk>\d+)/problemset/(?P<pspk>\w+)/alpha/(?P<popk>\w+)/save_grade/$', views.save_grade, name='alphasavegrade'),
    url(r'^class/(?P<pk>\d+)/problemset/(?P<pspk>\w+)/alpha/(?P<popk>\w+)/change_grade/$', views.change_grade, name='alphachangegrade'),
    url(r'^class/(?P<pk>\d+)/test/(?P<tpk>\w+)/$', views.teachertestview, name='teachertestview'),
    url(r'^class/(?P<pk>\w+)/test/(?P<tpk>\d+)/load_sol/(?P<ppk>\d+)/$', login_required(views.SolutionView.as_view()), name='teacher_load_solution3'),
##^^Needs basically the same stuff as problemset,but need to decide if new response environment needed first...^^##
    url(r'^migrate_response/(?P<username>\w+)/(?P<npk>\w+)/$',views.migrate_response,name="migrate_response"),
    url(r'^migrate_response/(?P<username>\w+)/(?P<npk>\w+)/add_response/$',views.move_response,name="move_response"),
    url(r'^ajax/load-edit-duedate/$',views.load_edit_duedate, name="load_edit_duedate"),
    url(r'^ajax/save-duedate/$',views.save_duedate, name="save_duedate"),
    url(r'^ajax/delete-duedate/$',views.delete_duedate, name="delete_duedate"),
    url(r'^ajax/load-edit-startdate/$',views.load_edit_startdate, name="load_edit_startdate"),
    url(r'^ajax/save-startdate/$',views.save_startdate, name="save_startdate"),
    url(r'^ajax/delete-startdate/$',views.delete_startdate, name="delete_startdate"),
    url(r'^ajax/load-edit-timelimit/$',views.load_edit_timelimit, name="load_edit_timelimit"),
    url(r'^ajax/save-timelimit/$',views.save_timelimit, name="save_timelimit"),
    url(r'^ajax/delete-timelimit/$',views.delete_timelimit, name="delete_timelimit"),
    url(r'^ajax/problemobject/load-edit-questiontype/$',views.loadeditquestiontype, name="po_load_edit_qt"),
    url(r'^ajax/problemobject/load-new-sol/$',views.load_new_solution_form, name="class_load_new_solution_form"),
    url(r'^ajax/problemobject/save-new-sol/$',views.save_new_solution, name="class_save_new_solution"),
    url(r'^ajax/problemobject/load-view-sols/$',views.load_manage_solutions, name="class_load_manage_solutions"),
    url(r'^ajax/problemobject/display-sol/$',views.display_solution, name="class_display_solution"),
    url(r'^ajax/problemobject/undisplay-sol/$',views.undisplay_solution, name="class_undisplay_solution"),
    url(r'^ajax/problemobject/delete-sol/$',views.delete_solution, name="class_delete_solution"),
    url(r'^ajax/problemobject/edit-sol/$',views.load_edit_sol, name="class_load_edit_solution"),
    url(r'^ajax/problemobject/save-edited-sol/$',views.save_edited_solution, name="class_save_edited_solution"),
    url(r'^ajax/problemobject/move-problem/$',views.move_problem, name="move_prob"),
    url(r'^ajax/problemobject/copy-problem/$',views.copy_problem, name="copy_prob"),

    url(r'^ajax/edit-class-name/$',views.editclassname, name="editclassname"),
    url(r'^ajax/save-class-name/$',views.saveclassname, name="saveclassname"),
    url(r'^ajax/edit-unit-name/$',views.editunitname, name="editunitname"),
    url(r'^ajax/save-unit-name/$',views.saveunitname, name="saveunitname"),
    url(r'^ajax/edit-problemset-name/$',views.editproblemsetname, name="editproblemsetname"),
    url(r'^ajax/save-problemset-name/$',views.saveproblemsetname, name="saveproblemsetname"),
    url(r'^ajax/edit-test-name/$',views.edittestname, name="edittestname"),
    url(r'^ajax/save-test-name/$',views.savetestname, name="savetestname"),
    url(r'^ajax/edit-slidegroup-name/$',views.editslidegroupname, name="editslidegroupname"),
    url(r'^ajax/save-slidegroup-name/$',views.saveslidegroupname, name="saveslidegroupname"),
    url(r'^ajax/edit-slide-title/$',views.editslidetitle, name="editslidetitle"),
    url(r'^ajax/save-slide-title/$',views.saveslidetitle, name="saveslidetitle"),

    url(r'^ajax/edit-sharing/$', views.load_sharing_modal, name='class_edit_sharing'),
    url(r'^ajax/share-with-user/$', views.share_with_user, name='class_share_with_user'),
    url(r'^ajax/change-permission/$', views.change_permission, name='class_change_permission'),
    url(r'^ajax/confirm-delete-class/$', views.confirm_delete_class, name='confirm_delete_class'),
    url(r'^ajax/confirm-remove-class/$', views.confirm_remove_class, name='confirm_remove_class'),
    url(r'^ajax/delete-class/$', views.delete_class, name='delete_class'),
    url(r'^ajax/remove-class/$', views.remove_class, name='remove_class'),
#    url(r'^edit/(?P<pk>\d+)/edit_section/(?P<spk>\d+)/$', login_required(views.SectionUpdateView.as_view()),name="update_section"),
#    url(r'^edit/(?P<pk>\d+)/edit_subsection/(?P<spk>\d+)/$', login_required(views.SubsectionUpdateView.as_view()),name="update_subsection"),
#    url(r'^edit/(?P<pk>\d+)/edit_textblock/(?P<spk>\d+)/$', login_required(views.TextBlockUpdateView.as_view()),name="update_textblock"),
#    url(r'^edit/(?P<pk>\d+)/edit_theorem/(?P<spk>\d+)/$', login_required(views.TheoremUpdateView.as_view()),name="update_theorem"),
#    url(r'^edit/(?P<pk>\d+)/edit_proof/(?P<spk>\d+)/$', login_required(views.ProofUpdateView.as_view()),name="update_proof"),
#    url(r'^edit/(?P<pk>\d+)/edit_handout/$', login_required(views.HandoutUpdateView.as_view()),name="update_handout"),

#    url(r'^edit/(?P<pk>\d+)/editnewtest/(?P<hpk>\d+)/$', views.editnewtestview, name='h_editnewtestview'),
]
