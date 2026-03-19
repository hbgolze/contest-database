from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('', views.classview, name='studentview'),
    path('problemset/<int:pk>/', views.problemsetview, name='problemsetview'),
    path('problemset/<int:pk>/load_sol/<int:ppk>/', login_required(views.SolutionView.as_view()), name='student_load_solution'),
    path('problemset/<int:pk>/toggle_star/', views.toggle_star, name='student_toggle_star'),
    path('problemset/<int:pk>/checkanswer/', views.checkanswer, name='student_checkanswer'),
#    path('problemset/<int:pk>/load-proof-response/', views.load_proof_response, name='load_proof_response'),
#    path('problemset/<int:pk>/save-proof-response/', views.save_proof_response, name='save_proof_response'),
    path('slides/<int:pk>/', views.slidesview, name='slidesview'),
    path('test/<int:pk>/', views.testview, name='testview'),
    path('test/<int:pk>/grade_test/', views.grade_test, name='gradetestview'),
    path('test/<int:pk>/saveresponse/', views.saveresponse, name='student_save_response'),
    path('test/<int:pk>/load_sol/<int:ppk>/', login_required(views.SolutionView.as_view()), name='student_load_solution'),
    path('ajax/load-proof-response/', views.load_proof_response, name='load_proof_response'),
    path('ajax/save-proof-response/', views.save_proof_response, name='save_proof_response'),
]
