from django.conf.urls import include#,url
from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path(r'^$', views.handoutlistview, name='handoutlistview'),
    path(r'^edit/<int:pk>/$', views.handouteditview, name='handouteditview'),
    path(r'^edit/<int:pk>/edit_section/<int:spk>/$', login_required(views.SectionUpdateView.as_view()),name="update_section"),
    path(r'^edit/<int:pk>/edit_subsection/<int:spk>/$', login_required(views.SubsectionUpdateView.as_view()),name="update_subsection"),
    path(r'^edit/<int:pk>/edit_textblock/<int:spk>/$', login_required(views.TextBlockUpdateView.as_view()),name="update_textblock"),
    path(r'^edit/<int:pk>/edit_theorem/<int:spk>/$', login_required(views.TheoremUpdateView.as_view()),name="update_theorem"),
    path(r'^edit/<int:pk>/edit_proof/<int:spk>/$', login_required(views.ProofUpdateView.as_view()),name="update_proof"),
    path(r'^edit/<int:pk>/edit_handout/$', login_required(views.HandoutUpdateView.as_view()),name="update_handout"),

    path(r'^edit/<int:pk>/editnewtest/<int:hpk>/$', views.editnewtestview, name='h_editnewtestview'),
]
