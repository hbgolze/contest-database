from django.urls import path
from .views import (
    DrillIndexView, ViewDrillView, CreateDrillAssignmentView, ViewAssignedDrillView,
    DrillTaskManagerView, ResultsIndexView, IndividualDrillResultsView,
    DrillProfileView, DrillRankingsView, GradeDrillView, ManageProfilesView,
    StudentScoresView,StudentAveragesView,StudentReportsView,ReorderDrillView,
    ProblemDifficultyView,TopicRankingsView,ProblemResultsbyDifficultyView,
    add_profile_view, add_year_to_profile, load_problems_modal, save_task,
    load_edit_task, load_edit_latex, load_edit_answer, save_answer, save_latex, 
    add_task, load_single_problem, assignment_pdf_view, individual_report_pdf_view,
    drill_pdf_view, drill_latex_view, load_new_solution, load_edit_solutions,
    save_new_solution, load_edit_single_solution, delete_solution, save_solution,
    drill_solutions_latex_view, drill_solutions_pdf_view,
)
from django.contrib.auth.decorators import login_required,permission_required

urlpatterns = [
    path('', permission_required('drills.add_drill')(DrillIndexView.as_view()), name='drill_index'),
    path('drill/<int:drill_id>/', permission_required('drills.add_drill')(ViewDrillView.as_view()), name='view_drill'),
    path('drill/<int:drill_id>/pdf/', drill_pdf_view, name='view_drill_pdf'),
    path('drill/<int:drill_id>/latex/', drill_latex_view, name='view_drill_latex'),
    path('drill/<int:drill_id>/solutions_pdf/', drill_solutions_pdf_view, name='view_drill_solutions_pdf'),
    path('drill/<int:drill_id>/solutions_latex/', drill_solutions_latex_view, name='view_drill_solutions_latex'),
    path('drill/<int:drill_id>/reorder/', permission_required('drills.add_drill')(ReorderDrillView.as_view()), name='reorder_drill'),
    path('drill/<int:drill_id>/load-edit-latex/<int:problem_id>/', load_edit_latex, name='load_edit_latex'),
    path('drill/<int:drill_id>/load-edit-answer/<int:problem_id>/', load_edit_answer, name='load_edit_answer'),
    path('drill/<int:drill_id>/save-latex/<int:problem_id>/', save_latex, name='save_latex'),
    path('drill/<int:drill_id>/save-answer/<int:problem_id>/', save_answer, name='save_answer'),
    path('drill/<int:drill_id>/load-new-solution/<int:problem_id>/', load_new_solution, name='load_new_solution'),
    path('drill/<int:drill_id>/save-new-solution/<int:problem_id>/', save_new_solution, name='save_new_solution'),
    path('drill/<int:drill_id>/load-edit-solutions/<int:problem_id>/', load_edit_solutions, name='load_edit_solutions'),
    path('drill/<int:drill_id>/load-edit-single-solution/<int:problem_id>/', load_edit_single_solution, name='load_edit_single_solution'),
    path('drill/<int:drill_id>/save-solution/<int:problem_id>/', save_solution, name='save_solution'),
    path('drill/<int:drill_id>/delete-solution/<int:problem_id>/', delete_solution, name='delete_solution'),
    path('grade_drill/<int:drill_id>/', permission_required('drills.add_drill')(GradeDrillView.as_view()), name='grade_drill'),
    path('assignment/new/', permission_required('drills.add_drill')(CreateDrillAssignmentView.as_view()), name='create_assignment'),
    path('assignment/<int:assignment_id>/', permission_required('drills.add_drill')(ViewAssignedDrillView.as_view()), name='view_assigned_drill'),
    path('assignment/<int:assignment_id>/pdf/', assignment_pdf_view, name='assignment_pdf'),
    path('tasks/', permission_required('drills.add_drill')(DrillTaskManagerView.as_view()), name='task_manager'),
    path('tasks/add/', add_task, name='add_task'),
    path('tasks/<int:task_id>/problems_modal/', load_problems_modal, name='load_problems_modal'),
    path('tasks/<int:task_id>/edit/', save_task, name='save_task'),
    path('tasks/<int:task_id>/load-edit-task/', load_edit_task, name='load_edit_task'),
    path('results/', permission_required('drills.add_drill')(ResultsIndexView.as_view()), name='results_index'),
    path('results/scores/<int:year>/', permission_required('drills.add_drill')(StudentScoresView.as_view()), name='view_student_scores'),
    path('results/scores/<int:year>/student/<int:profile_id>/', permission_required('drills.add_drill')(StudentReportsView.as_view()), name='view_student_reports'),
    path('results/scores/<int:year>/student/<int:profile_id>/pdf/', individual_report_pdf_view, name='view_student_reports_pdf'),
    path('results/averages/<int:year>/', permission_required('drills.add_drill')(StudentAveragesView.as_view()), name='view_student_averages'),
    path('results/problem_difficulty/<int:year>/', permission_required('drills.add_drill')(ProblemDifficultyView.as_view()), name='problem_difficulty'),
    path('results/problem_difficulty/<int:year>/<int:problem_id>/', load_single_problem, name='load_single_problem'),
    path('results/topic_rankings/<int:year>/', permission_required('drills.add_drill')(TopicRankingsView.as_view()), name='topic_rankings'),
    path('results/problem_results_by_difficulty/<int:year>/', permission_required('drills.add_drill')(ProblemResultsbyDifficultyView.as_view()), name='problem_results_by_difficulty'),
    path('results/<int:drill_id>/', permission_required('drills.add_drill')(IndividualDrillResultsView.as_view()), name='drill_results'),
    path('manage_profiles/', permission_required('drills.add_drill')(ManageProfilesView.as_view()), name='manage_profiles'),
    path('manage_profiles/add/', add_profile_view, name='manage_profiles_add'),
    path('manage_profiles/add_year/', add_year_to_profile, name='add_year'),
    path('profile/<int:profile_id>/', permission_required('drills.add_drill')(DrillProfileView.as_view()), name='drill_profile'),
    path('rankings/', permission_required('drills.add_drill')(DrillRankingsView.as_view()), name='drill_rankings'),
    ]
