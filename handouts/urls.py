from django.conf.urls import include,url

from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^$', views.handoutlistview, name='handoutlistview'),
    url(r'^edit/(?P<pk>\d+)/$', views.handouteditview, name='handouteditview'),
    url(r'^edit/(?P<pk>\d+)/edit_section/(?P<spk>\d+)/$', login_required(views.SectionUpdateView.as_view()),name="update_section"),
    url(r'^edit/(?P<pk>\d+)/edit_subsection/(?P<spk>\d+)/$', login_required(views.SubsectionUpdateView.as_view()),name="update_subsection"),
    url(r'^edit/(?P<pk>\d+)/edit_textblock/(?P<spk>\d+)/$', login_required(views.TextBlockUpdateView.as_view()),name="update_textblock"),
    url(r'^edit/(?P<pk>\d+)/edit_theorem/(?P<spk>\d+)/$', login_required(views.TheoremUpdateView.as_view()),name="update_theorem"),
    url(r'^edit/(?P<pk>\d+)/edit_proof/(?P<spk>\d+)/$', login_required(views.ProofUpdateView.as_view()),name="update_proof"),
    url(r'^edit/(?P<pk>\d+)/edit_handout/$', login_required(views.HandoutUpdateView.as_view()),name="update_handout"),
]
