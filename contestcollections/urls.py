from django.conf.urls import include#,url
from django.urls import path

from django.contrib.auth.decorators import login_required

from . import views
#from views import TestDelete

urlpatterns = [
    path('', views.tableview, name='cctableview'),
    path('test/<int:pk>/', views.testview, name='cctestview'),
    path('test/pdf/<int:pk>/', views.test_as_pdf, name='ccpdfview'),
    path('test/halfpage_pdf/<int:pk>/', views.halfpage_test_as_pdf, name='cchppdfview'),
    path('test/<int:testpk>/<int:pk>/', views.solutionview, name='ccsolutionview'),
#    path('test/<int:testpk>/load_sol/<int:pk>/', views.load_solution, name='load_solution'),
    path('test/<int:testpk>/load_sol/<int:pk>/', login_required(views.SolutionView.as_view()), name='cc_load_solution'),
    path('test/<int:pk>/pdfoptions/', views.testpdfoptions, name='cctestpdfoptions'),
    path('test/<int:pk>/pdfoptions/problems/', views.problempdf, name='ccproblempdf'),
    path('test/<int:pk>/pdfoptions/solutions/', views.solutionpdf, name='ccsolutionpdf'),
    path('test/<int:pk>/pdfoptions/answerkey/', views.answerkeypdf, name='ccanswerkeypdf'),
    path('test/<int:pk>/pdfoptions/viewlatex/', views.latexview, name='ccviewlatex'),

]
