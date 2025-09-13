from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.utils.timezone import now
from .models import Drill, DrillTask, DrillProblem, DrillAssignment, DrillProfile, DrillRecord, YearFolder,DrillRecordProblem,DrillProblemSolution,Category
from django.http import HttpResponse,JsonResponse
from django.conf import settings

from django.template.loader import get_template,render_to_string
from django.template import Template, Context
from django.contrib.auth.decorators import permission_required
from random import shuffle
from randomtest.utils import compileasy,newtexcode, newsoltexcode, compiletikz
from randomtest.models import Type,Round,Problem,ContestTest,QuestionType

from .forms import SolutionForm

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')
import numpy as np

from io import BytesIO
import base64

import tempfile
from subprocess import Popen,PIPE
import os,os.path

from django.contrib.admin.models import LogEntry, ADDITION,CHANGE,DELETION
from django.contrib.contenttypes.models import ContentType

class DrillIndexView(View):
    def get(self, request):
        categories = Category.objects.all()
        year_folders = YearFolder.objects.all()
        return render(request, 'drills/index.html', {'categories': categories, 'current_year': now().year, 'year_folders': year_folders,'nbar':'drills'})

class ViewDrillView(View):
    def get(self, request, drill_id):
        drill = get_object_or_404(Drill, id=drill_id)
        problems = drill.drill_problems.all().order_by('order')
        return render(request, 'drills/view_drill.html', {'drill': drill, 'drill_problems': problems,'nbar':'drills'})

###partially edited
class CreateDrillAssignmentView(View):
    def get(self, request):
        year_pk = request.GET.get('year_pk')
        yf = get_object_or_404(YearFolder,pk = year_pk)
        tasks = yf.category.drill_tasks.exclude(topic='Bonus')
        bag = []
        task_counts = {}
        last_usages = {}
        for t in tasks:
            problems = t.drillproblem_set.filter(drill__year_folder=yf)
            assignments = t.drillassignment_set.filter(year = yf)
            uses = [p.drill.number for p in problems] + [a.number for a in assignments]
            last_usage = 0
            if len(uses) > 0:
                last_usage = max(uses) 
            task_counts[str(t.pk)] = len(uses)
            last_usages[str(t.pk)] = last_usage
            if len(uses) == 0:
                for j in range(0,20):
                    bag.append(t)
            else:
                if max(uses) <= yf.top_number - 5:
                    for j in range(0,yf.top_number - 5 - max(uses)+1):
                        bag.append(t)
        shuffle(bag)
        R = []
        counter = 0
        while len(R) < 25:
            if (bag[counter],task_counts[str(bag[counter].pk)],last_usages[str(bag[counter].pk)]) not in R:
                R.append((bag[counter],task_counts[str(bag[counter].pk)],last_usages[str(bag[counter].pk)]))
            counter += 1

        name = str(yf.year) + ' ' + yf.category.name + ' Drill '+str(yf.top_number+1)
        author = request.GET.get('author')
        return render(request, 'drills/create_assignment.html', {'tasks': R, 'name' : name, 'author': author, 'year': yf,'nbar':'drills'})

    def post(self, request):
        selected_tasks = request.POST.getlist('selected_tasks[]')
        author = request.POST.get('author')
        year_pk = request.POST.get('year_pk')
        yf = get_object_or_404(YearFolder,pk = year_pk)
        assignment = DrillAssignment.objects.create(author=author,year = yf, number = yf.top_number + 1)
        yf.top_number = yf.top_number + 1
        yf.save()
        tasks = DrillTask.objects.filter(pk__in=selected_tasks)
        for t in tasks:
            assignment.problem_tasks.add(t)
        assignment.save()
        return redirect('view_assigned_drill',assignment_id=assignment.id)


class ViewAssignedDrillView(View):
    def get(self, request, assignment_id):
        assignment = get_object_or_404(DrillAssignment, id=assignment_id)
        return render(request, 'drills/view_assigned_drill.html', {'assignment': assignment})
    def post(self,request,assignment_id):
        assignment = get_object_or_404(DrillAssignment, id=assignment_id)
        ids=[]
        for i in request.POST:
            if 'problem_text' in i:
                id = i.split('_')[2]
                ids.append(id)
        counter = 1
        year_folder = assignment.year
        y = year_folder.year
        num = assignment.number
        drill = Drill.objects.create(year_folder = year_folder,year = y,number = num,readable_label=str(y)+' ' + year_folder.category.name + ' Drill '+ str(num),author = assignment.author,problem_count = len(ids))
        for id in ids:
            task = get_object_or_404(DrillTask,id=id)
            problem_text = request.POST.get('problem_text_'+id)
            answer = request.POST.get('answer_'+id)
            p = DrillProblem.objects.create(order = counter,label=str(y) + year_folder.category.name.replace(' ','') + 'Drill'+str(num)+'-'+str(counter),readable_label = str(y)+' ' + year_folder.category.name + ' Drill '+str(num)+' #'+str(counter),drill = drill,problem_text = problem_text,topic = task.topic, drill_task = task,answer=answer,percent_solved=0,number_solved = 0)
            compileasy(p.problem_text,'drillproblem_'+str(p.pk))
            p.display_problem_text = newtexcode(p.problem_text,'drillproblem_'+str(p.pk),'')
            p.save()
            counter+=1
        assignment.delete()
        return redirect('view_drill',drill_id=drill.id)

class CategoryIndexView(View):
    def get(self, request):
        categories = Category.objects.all()
        return render(request, 'drills/task_manager_index.html', {'categories': categories,'nbar':'drills'})
    
class DrillTaskManagerView(View):
    def get(self, request, cat_pk):
        category = get_object_or_404(Category,pk = cat_pk)
        tasks = category.drill_tasks.all().order_by('topic')
        return render(request, 'drills/task_manager.html', {'category':category, 'tasks': tasks,'nbar':'drills'})

class ResultsIndexView(View):
    def get(self, request):
        years = YearFolder.objects.all()
        return render(request, 'drills/results_index.html', {'years': years,'nbar':'drills'})

class IndividualDrillResultsView(View):
    def get(self, request, drill_id):
        drill = get_object_or_404(Drill, id=drill_id)
        records = DrillRecord.objects.filter(drill=drill)

        return render(request, 'drills/individual_results.html', {'drill': drill, 'records': records,'nbar':'drills'})

class DrillProfileView(View):
    def get(self, request, profile_id):
        profile = get_object_or_404(DrillProfile, id=profile_id)
        records = DrillRecord.objects.filter(drill_profile=profile)
        return render(request, 'drills/profile.html', {'profile': profile, 'records': records,'nbar':'drills'})

class DrillRankingsView(View):
    def get(self, request):
        profiles = DrillProfile.objects.all()
        return render(request, 'drills/rankings.html', {'profiles': profiles,'nbar':'drills'})

class GradeDrillView(View):
    def get(self, request, drill_id):
        drill = get_object_or_404(Drill, id=drill_id)
        drill_records = drill.drill_records.order_by('drill_profile__name')
        ids = [i.drill_profile.id for i in drill_records]
        blank_profiles = drill.year_folder.profiles.exclude(id__in = ids).order_by('name')# change to yearfolder
        return render(request, 'drills/grade_drill.html', {'drill': drill, 'drill_records': drill_records,'blank_profiles':blank_profiles,'nbar':'drills'})
    def post(self,request, drill_id):
        drill = get_object_or_404(Drill, id=drill_id)
        selected_profiles = request.POST.getlist('checks')[0].split(',')
        grades={}
        for i in request.POST:
            if 'grade' in i:
                j = i.split('_')
                grades[j[1]+'_'+j[2]]=request.POST.get(i,'')
        for i in grades:
            try:
                if grades[i]=='':
                    pass
                else:
                    g = int(grades[i])
            except ValueError:
                return JsonResponse({"error": "Not all scores were integers."}, status=400)
        if '' in selected_profiles:
            return JsonResponse({'error': 'No profiles selects'},status=400)
        for profile_id in selected_profiles:
            dp = get_object_or_404(DrillProfile,id = profile_id)
            if dp.drillrecord_set.filter(drill__pk = drill.pk).exists():
                drill_record = dp.drillrecord_set.get(drill__pk = drill.pk)
                for drp in drill_record.drill_record_problems.all():
                    if grades[str(profile_id)+'_'+str(drp.drill_problem.id)] == "":
                        drp.status = -1
                    elif int(grades[str(profile_id)+'_'+str(drp.drill_problem.id)]) > 0:
                        drp.status = 1
                    else:
                        drp.status = 0
                    drp.save()
            else:
                drill_record = DrillRecord(drill_profile = dp,drill = drill,score = 0)
                drill_record.save()
                for i in range(1,drill.problem_count + 1):
                    drill_problem = drill.drill_problems.get(order = i)
                    status = -1
                    if grades[str(profile_id)+'_'+str(drill_problem.id)] == "":
                        status = -1
                    elif int(grades[str(profile_id)+'_'+str(drill_problem.id)]) > 0:
                        status = 1
                    else:
                        status = 0
                    drp = DrillRecordProblem(drillrecord = drill_record,order = i,drill_problem = drill_problem,status=status)
                    drp.save()
            score = 0
            drill_record.update_score()
        drill.update_stats()
        drill_records = drill.drill_records.order_by('drill_profile__name')
        blank_profiles = drill.year_folder.profiles.exclude(id__in = drill_records.values('id')).order_by('name')
        return render(request, 'drills/grade_drill.html', {'drill': drill, 'drill_records': drill_records,'blank_profiles':blank_profiles,'nbar':'drills'})


class ManageProfilesView(View):
    def get(self, request):
        profiles = DrillProfile.objects.all()
        years = YearFolder.objects.all()
        categories = Category.objects.all()
        return render(request, 'drills/manage_profiles.html', {'profiles': profiles, 'years': years,'nbar':'drills','categories': categories})

class StudentScoresView(View):
    def get(self, request, year_pk):
        year = get_object_or_404(YearFolder, pk=year_pk)
        rows = []
        for profile in year.profiles.all():
            row = [profile]+[[(-1,0)]*year.drills.count()]+[0]+[0]+[0]
            bonus = 0
            for record in profile.drillrecord_set.filter(drill__year_folder = year):
                #row[1][record.drill.number-1] = record
                row[1][record.drill.number-1] = (record.score,record.bonus_score)
                bonus += record.total_score
            row[-3] = sum([row[1][i][0] for i in range(0,len(row[1]))]) + row[1].count((-1,0))
            row[-2] = bonus
            row[-1] = row[-3]/(max(1,10*profile.drillrecord_set.filter(drill__year_folder = year).count()))*100#assumes 10 problems per drill
            rows.append(row)
        rows = sorted(rows,key=lambda x:-x[2])
        
        return render(request, 'drills/student_scores.html', {'year': year,'rows':rows,'nbar':'drills'})

class StudentAveragesView(View):
    def get(self, request, year_pk):
        year = get_object_or_404(YearFolder, pk=year_pk)
        student_totals={}
        num_drills = 0
        for drill in year.drills.all():
            if drill.drill_records.exists():
                num_drills += 1
        for profile in year.profiles.all():
            row = [0]*num_drills
            for record in profile.drillrecord_set.filter(drill__year_folder = year):
                row[record.drill.number-1] = record.score
            totals = [row[0]]
            for i in range(1,len(row)):
                totals.append(row[i]+totals[-1])
            student_totals[profile.name]=totals
        x = [i for i in range(1,num_drills+1)]
        fig = plt.figure(figsize=(15, 9))
        ax = plt.subplot(111)
        final_avgs = []
        for student in student_totals:
            total = student_totals[student]
            student_avgs = [total[i-1]/i for i in range(1,len(total)+1)]
            final_avgs.append((student,student_avgs[-1]))
            ax.plot(x,student_avgs,label=student)
        handles, labels = plt.gca().get_legend_handles_labels()
        final_avgs = sorted(final_avgs,key=lambda x:-x[1])
        names = [i[0] for i in final_avgs]
        order = [labels.index(i) for i in names]
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        ax.legend([handles[idx] for idx in order],[labels[idx] for idx in order],loc='center left', bbox_to_anchor=(1, 0.5))
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png =buffer.getvalue()
        plt.close()
        buffer.close()
        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')
    
        return render(request, 'drills/student_averages.html', {'year': year,'graphic':graphic,'nbar':'drills'})
    
class StudentReportsView(View):
    def get(self, request, year_pk,profile_id):
        year = get_object_or_404(YearFolder, pk=year_pk)
        profile = get_object_or_404(DrillProfile, id = profile_id)
        
        nums = []
        for drill in year.drills.all():
            nums.append(drill.problem_count)
        num_probs = max(nums+[0])
        drill_records=[]

        year_drill_records = profile.drillrecord_set.filter(drill__year_folder = year)
        for drill_record in year_drill_records.order_by('drill__number'):
            row = [drill_record,[0]*(num_probs - drill_record.drill.problem_count)]
            drill_records.append(row)
        problem_numbers = [i for i in range(1,num_probs+1)]

        topic_data = []
        for user_profile in year.profiles.all():
            topic_data.append([user_profile,user_profile.acgn(year)])
        topic_data = sorted(topic_data,key = lambda x:-x[1][2])#alg
        alg_rank = 0
        for i in range(0,len(topic_data)):
            if topic_data[i][0].id == profile.id:
                alg_rank = i+1
        topic_data = sorted(topic_data,key = lambda x:-x[1][5])#combo
        combo_rank = 0
        for i in range(0,len(topic_data)):
            if topic_data[i][0].id == profile.id:
                combo_rank = i+1
        topic_data = sorted(topic_data,key = lambda x:-x[1][8])#geo
        geo_rank = 0
        for i in range(0,len(topic_data)):
            if topic_data[i][0].id == profile.id:
                geo_rank = i+1
        topic_data = sorted(topic_data,key = lambda x:-x[1][11])#nt
        nt_rank = 0
        for i in range(0,len(topic_data)):
            if topic_data[i][0].id == profile.id:
                nt_rank = i+1
        
        acgn = profile.acgn(year)

        num_drills = 0
        drill_avgs = []
        for drill in year.drills.all():
            drill_avgs.append(drill.average_score)
            if drill.drill_records.exists():
                num_drills += 1
        x = [i for i in range(1,year.drills.count()+1)]
        fig = plt.figure(figsize=(15, 9))
        ax = plt.subplot(111)
        print(len(x),len(drill_avgs))
        ax.plot(x, drill_avgs,label="Average Scores")

        x_student = []
        scores = []
        for record in profile.drillrecord_set.filter(drill__year_folder = year):
            x_student.append(record.drill.number)
        x_student.sort()
        scores = [0]*len(x_student)
        for record in profile.drillrecord_set.filter(drill__year_folder = year):
            scores[x_student.index(record.drill.number)] = record.score

        ax.plot(x_student,scores,label=profile.name)
        handles, labels = plt.gca().get_legend_handles_labels()

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        ax.legend(handles,labels,loc='center left', bbox_to_anchor=(1, 0.5))
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png =buffer.getvalue()
        plt.close()
        buffer.close()
        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')
        
        return render(request, 'drills/student_report.html', {'year': year,'profile':profile,'problem_numbers':problem_numbers,'drill_records':drill_records,
                                                              'alg_rank':alg_rank,'combo_rank':combo_rank,'geo_rank':geo_rank,'nt_rank':nt_rank,
                                                              'acgn':acgn,'nbar':'drills','graphic':graphic})

class TopicRankingsView(View):
    def get(self, request, year_pk):
        year = get_object_or_404(YearFolder, pk=year_pk)
        topic_data = []
        for user_profile in year.profiles.all():
            topic_data.append([user_profile,user_profile.acgn(year)])
        topic_data = sorted(topic_data,key=lambda x:-x[0].score(year))
        return render(request, 'drills/topic_rankings.html', {'year': year,'topic_data':topic_data,'nbar':'drills'})

class ReorderDrillView(View):
    def get(self, request, drill_id):
        drill = get_object_or_404(Drill, id=drill_id)
        
        return render(request, 'drills/reorder_drill.html', {'drill': drill,'nbar':'drills'})
    def post(self,request,drill_id):
        drill = get_object_or_404(Drill, id=drill_id)
        ids=[]
        for i in request.POST:
            if 'problem' in i:
                id = i.split('_')[1]
                ids.append(id)
        counter = 1
        for i in ids:
            p = DrillProblem.objects.get(id=i)
            p.update_order(counter)
            counter += 1
        return redirect('view_drill',drill_id=drill_id)

class ProblemDifficultyView(View):
    def get(self, request, year_pk):
        year = get_object_or_404(YearFolder, pk=year_pk)
        nums = []
        for drill in year.drills.all():
            nums.append(drill.problem_count)
        num_probs = max(nums+[0])
        drills=[]
        for drill in year.drills.all():
            row = [drill,num_probs - drill.problem_count]
            drills.append(row)
        problem_numbers = [i for i in range(1,num_probs+1)]
        return render(request, 'drills/problem_difficulty.html', {'year': year,'problem_numbers':problem_numbers,'drills':drills,'nbar':'drills'})

class ProblemResultsbyDifficultyView(View):
    def get(self, request, year_pk):
        year = get_object_or_404(YearFolder, pk=year_pk)
        rows = []
        problems = []
        for drill in year.drills.all():
            if drill.drill_records.exists():
                for p in drill.drill_problems.all():
                    problems.append(p)
        problems = sorted(problems, key = lambda x: -x.percent_solved)
        profiles = list(year.profiles.all())
        profiles = sorted(profiles,key = lambda x:-x.score(year))
        for profile in profiles:
            row = []
            drp = DrillRecordProblem.objects.filter(drillrecord__drill_profile = profile)
            for p in problems:
                if drp.filter(drill_problem = p).exists():
                    row.append(drp.filter(drill_problem=p)[0].status)
                else:
                    row.append(-1)
            rows.append((profile.name,row))
        return render(request, 'drills/problem_results_by_difficulty.html', {'year': year,'rows':rows,'nbar':'drills'})
 
@permission_required('drills.add_drill')
def add_profile_view(request,**kwargs):
    name = request.POST.get('name','')
    p = DrillProfile(name=name)
    p.save()
    return JsonResponse({'profile_row':render_to_string('drills/snippet_profile-row.html',{'profile':p,'years': YearFolder.objects.all(),'request':request})})


@permission_required('drills.add_drill')
def add_year_view(request,**kwargs):
    cat_pk = request.POST.get('cat_pk','')
    year = request.POST.get('year','')
    category = get_object_or_404(Category, pk = cat_pk)
    if YearFolder.objects.filter(year = year, category = category).exists():
        return JsonResponse({'error': 'Year already exists'},status=400)
    yf = YearFolder.objects.create(year = year, category = category)
    return redirect('manage_profiles')

@permission_required('drills.add_drill')
def add_year_to_profile(request):
    years = [(d,p) for d, p in request.POST.items() if d.startswith('addyear')]
    for i in years:
        profile_pk = i[0].split('_')[1]
        profile = get_object_or_404(DrillProfile,pk = profile_pk)
        yf = get_object_or_404(YearFolder,pk = i[1])
        profile.year.add(yf)
        profile.save()
    return JsonResponse({'profile_row':render_to_string('drills/snippet_profile-inner-row.html',{'profile':profile,'years': YearFolder.objects.all(),'request':request}),'profile_pk': profile_pk})


@permission_required('drills.add_drill')
def load_problems_modal(request,cat_pk, task_id):
    drill_task = get_object_or_404(DrillTask,id = task_id)
    return JsonResponse({'problem_html':render_to_string('drills/snippet_problems-html.html',{'task': drill_task})})


@permission_required('drills.add_drill')
def save_task(request, cat_pk,task_id):
    drill_task = get_object_or_404(DrillTask,id = task_id)
    topic = request.POST.get('topic')
    description = request.POST.get('description')
    drill_task.topic = topic
    drill_task.description = description
    drill_task.save()
    return JsonResponse({})


@permission_required('drills.add_drill')
def load_edit_task(request,cat_pk,task_id):
    task = get_object_or_404(DrillTask,id = task_id)
    return JsonResponse({'html_code':render_to_string('drills/snippet_load-edit-task.html',{'task': task})})


@permission_required('drills.add_drill')
def load_edit_latex(request,drill_id,problem_id):
    problem = get_object_or_404(DrillProblem,id = problem_id)
    return JsonResponse({'html_code':render_to_string('drills/snippet_load-edit-latex.html',{'problem': problem})})


@permission_required('drills.add_drill')
def save_latex(request,drill_id,problem_id):
    problem = get_object_or_404(DrillProblem,id=problem_id)
    problem_text = request.POST.get('problem_text')
    problem.problem_text = problem_text
    problem.save()
    compileasy(problem.problem_text,'drillproblem_'+str(problem.pk))
    problem.display_problem_text = newtexcode(problem.problem_text,'drillproblem_'+str(problem.pk),'')
    problem.save()
    return JsonResponse({'html_code':render_to_string('drills/snippet_drill-problem-card.html',{'problem': problem})})


@permission_required('drills.add_drill')
def load_edit_answer(request,drill_id,problem_id):
    problem = get_object_or_404(DrillProblem,id = problem_id)
    return JsonResponse({'html_code':render_to_string('drills/snippet_load-edit-answer.html',{'problem': problem})})


@permission_required('drills.add_drill')
def save_answer(request,drill_id,problem_id):
    problem = get_object_or_404(DrillProblem,id=problem_id)
    answer = request.POST.get('answer')
    problem.answer = answer
    problem.save()
    return JsonResponse({'html_code':render_to_string('drills/snippet_drill-problem-card.html',{'problem': problem})})
    

@permission_required('drills.add_drill')
def add_task(request,cat_pk):
    category = get_object_or_404(Category,pk = cat_pk)
    topic = request.POST.get('topic')
    description = request.POST.get('description')
    task = DrillTask.objects.create(topic = topic,description=description,category = category)
    return JsonResponse({'id':task.id,'description':description,'topic':topic})


@permission_required('drills.add_drill')
def load_single_problem(request, year_pk,problem_id):
    problem = DrillProblem.objects.get(id = problem_id)
    return JsonResponse({'problem_html':render_to_string('drills/snippet_single-problem-html.html',{'problem': problem})})


@permission_required('drills.add_drill')
def load_edit_solutions(request,drill_id,problem_id):
    problem = get_object_or_404(DrillProblem,id = problem_id)
    return JsonResponse({'html_code':render_to_string('drills/snippet_load-sol.html',{'problem': problem})})

@permission_required('drills.add_drill')
def load_new_solution(request,drill_id,problem_id):
    problem = get_object_or_404(DrillProblem,id = problem_id)
    return JsonResponse({'html_code':render_to_string('drills/snippet_load-new-solution.html',{'problem': problem})})

@permission_required('drills.add_drill')
def save_new_solution(request,drill_id,problem_id):
    problem = get_object_or_404(DrillProblem,id = problem_id)
    form = request.POST
    order = 1
    if problem.drillproblemsolution_set.exists():
        s = problem.drillproblemsolution_set.order_by('-order')[0]
        order = s.order + 1
    s = DrillProblemSolution.objects.create(solution_text = request.POST.get('new_solution_text'),drill_problem = problem, order = order)
    s.display_solution_text = newsoltexcode(s.solution_text, str(problem.id)+'drillsol_'+str(s.id))
    s.save()
    compileasy(s.solution_text,str(problem.id)+'drillsol_'+str(s.id))
    compiletikz(s.solution_text,str(problem.id)+'drillsol_'+str(s.id))
    return JsonResponse({'sol_count': problem.drillproblemsolution_set.count(),
                         'html_code':render_to_string('drills/snippet_load-sol.html',{'problem': problem}),
                         'sol_id': s.id})

@permission_required('drills.add_drill')
def load_edit_single_solution(request,**kwargs):
    pk = request.POST.get('pk','')
    spk = request.POST.get('spk','')
    prob =  get_object_or_404(DrillProblem,pk=pk)
    sol =  get_object_or_404(DrillProblemSolution,pk=spk)
    form = SolutionForm(instance=sol)
    return JsonResponse({'sol_form':render_to_string('drills/snippet_load-edit-single-sol.html',{'form':form,'prob':prob})})

@permission_required('drills.add_drill')
def save_solution(request,drill_id,problem_id):
    problem = get_object_or_404(DrillProblem,id = problem_id)
    solution_id = request.POST.get('spk')
    solution = get_object_or_404(DrillProblemSolution,id = solution_id)
    solution.solution_text = request.POST.get('solution_text')
    solution.save()
    solution.display_solution_text = newsoltexcode(solution.solution_text, str(problem.id)+'drillsol_'+str(solution.id))
    solution.save()
    compileasy(solution.solution_text,str(problem.id)+'drillsol_'+str(solution.id))
    compiletikz(solution.solution_text,str(problem.id)+'drillsol_'+str(solution.id))
    s = Template('{% autoescape off %}{{solution.display_solution_text|linebreaks}}{% endautoescape %}')
    context = Context(dict(solution=solution))
    return JsonResponse({'sol_text':s.render(context),})

@permission_required('drills.add_drill')
def add_bonus(request,drill_id):
    drill = get_object_or_404(Drill,id = drill_id)
    problem_text = request.POST.get('problem_text')
    answer = request.POST.get('answer')
    if DrillTask.objects.filter(category = drill.year_folder.category,topic="Bonus",description = "Bonus").exists():
        task = DrillTask.objects.filter(category = drill.year_folder.category,topic="Bonus",description = "Bonus")[0]
    else:
        task = DrillTask.objects.create(category = drill.year_folder.category,topic="Bonus",description = "Bonus")
    counter = drill.problem_count + 1
    p = DrillProblem.objects.create(order = counter,
                                    label=str(drill.year_folder.year) + drill.year_folder.category.name.replace(' ','') + 'Drill'+str(drill.number)+'-'+str(counter),
                                    readable_label = str(drill.year_folder.year)+' ' + drill.year_folder.category.name + ' Drill '+str(drill.number)+' #'+str(counter),
                                    drill = drill,
                                    problem_text = problem_text,
                                    topic = task.topic,
                                    drill_task = task,
                                    answer = answer,
                                    percent_solved = 0,
                                    number_solved = 0,
                                    is_bonus = True)
    compileasy(p.problem_text,'drillproblem_'+str(p.pk))
    p.display_problem_text = newtexcode(p.problem_text,'drillproblem_'+str(p.pk),'')
    p.save()
    drill.problem_count = drill.problem_count + 1
    drill.save()
    drill_records = DrillRecord.objects.filter(drill = drill)
    for dr in drill_records:
        dpr = DrillRecordProblem.objects.create(drillrecord = dr, order = p.order,drill_problem = p, status = -1)
    return JsonResponse({'success':1})

@permission_required('drills.add_drill')
def edit_author(request,drill_id):
    drill = get_object_or_404(Drill,id = drill_id)
    return JsonResponse({'author':drill.author})


@permission_required('drills.add_drill')
def save_author(request,drill_id):
    drill = get_object_or_404(Drill,id = drill_id)
    author = request.POST.get('author_name')
    drill.author = author
    drill.save()
    return JsonResponse({'author':drill.author})

@permission_required('drills.add_drill')
def edit_assignment_author(request,assignment_id):
    assignment = get_object_or_404(DrillAssignment,id = assignment_id)
    return JsonResponse({'author':assignment.author})


@permission_required('drills.add_drill')
def save_assignment_author(request,assignment_id):
    assignment = get_object_or_404(DrillAssignment,id = assignment_id)
    author = request.POST.get('author_name')
    assignment.author = author
    assignment.save()
    return JsonResponse({'author':assignment.author})

@permission_required('drills.add_drill')
def delete_solution(request,drill_id,problem_id):
    problem = get_object_or_404(DrillProblem,id = problem_id)
    solution_id = request.POST.get('spk')
    sol = get_object_or_404(DrillProblemSolution,id = solution_id)
    sol.delete()
    problem.renumber_solutions()
    return JsonResponse({'deleted':1, 'sol_count': problem.drillproblemsolution_set.count()})

@permission_required('drills.add_drill')
def assignment_pdf_view(request,assignment_id):
    top_number = 0
    if 'top_number' in request.GET:
        top_number = int(request.GET.get('top_number',''))
    drill_assignment = get_object_or_404(DrillAssignment, id = assignment_id)
    context = {
        'assignment':drill_assignment,
        'top_number' : top_number,
        }
    
    assignment_name = str(drill_assignment.year.year)+ ' ' + drill_assignment.year.category.name + ' Drill '+str(drill_assignment.number)
    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('drills/my_assignment_latex.tex')
    rendered_tpl = template.render(context).encode('utf-8')
    with tempfile.TemporaryDirectory() as tempdir:
        fa = open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        context = {
            'tempdirect':tempdir,
            'assignment':drill_assignment,
            'top_number' : top_number,
            }
        template = get_template('drills/my_assignment_latex.tex')
        rendered_tpl = template.render(context).encode('utf-8')
        ftex = open(os.path.join(tempdir,'texput.tex'),'wb')
        ftex.write(rendered_tpl)
        ftex.close()
        for i in range(1):
            process = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process.communicate()[0]
        L=os.listdir(tempdir)

        for i in range(0,len(L)):
            if L[i][-4:] == '.asy':
                process1 = Popen(
                    ['asy', L[i]],
                    stdin = PIPE,
                    stdout = PIPE,
                    cwd = tempdir,
                    )
                stdout_value = process1.communicate()[0]
        for i in range(2):
            process2 = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process2.communicate()[0]

        if 'texput.pdf' in os.listdir(tempdir):
            with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
                pdf = f.read()
                r = HttpResponse(content_type = 'application/pdf')
                r.write(pdf)
                r['Content-Disposition'] = 'attachment;filename="'+assignment_name.replace(' ','')+'.pdf"'
                return r
        else:
            with open(os.path.join(tempdir, 'texput.log')) as f:
                error_text = f.read()
                return render(request,'randomtest/latex_errors.html',{'nbar':'drills','name':assignment_name,'error_text':error_text})#####Perhaps the error page needs to be customized...  

@permission_required('drills.add_drill')
def individual_report_pdf_view(request,year_pk,profile_id):
    no_average = 0
    if 'no_average' in request.GET:
        no_average = 1
    profile = get_object_or_404(DrillProfile, id = profile_id)
    year = get_object_or_404(YearFolder, pk = year_pk)

    nums = []
    for drill in year.drills.all():
        nums.append(drill.problem_count)
    num_probs = max(nums+[0])
    drill_records=[]

    year_drill_records = profile.drillrecord_set.filter(drill__year_folder = year)
    for drill_record in year_drill_records.order_by('drill__number'):
        row = [drill_record,[0]*(num_probs - drill_record.drill.problem_count)]
        drill_records.append(row)
    problem_numbers = [i for i in range(1,num_probs+1)]

    topic_data = []
    for user_profile in year.profiles.all():
        topic_data.append([user_profile,user_profile.acgn(year)])
    topic_data = sorted(topic_data,key = lambda x:-x[1][2])#alg
    alg_rank = 0
    for i in range(0,len(topic_data)):
        if topic_data[i][0].id == profile.id:
            alg_rank = i+1
    topic_data = sorted(topic_data,key = lambda x:-x[1][5])#combo
    combo_rank = 0
    for i in range(0,len(topic_data)):
        if topic_data[i][0].id == profile.id:
            combo_rank = i+1
    topic_data = sorted(topic_data,key = lambda x:-x[1][8])#geo
    geo_rank = 0
    for i in range(0,len(topic_data)):
        if topic_data[i][0].id == profile.id:
            geo_rank = i+1
    topic_data = sorted(topic_data,key = lambda x:-x[1][11])#nt
    nt_rank = 0
    for i in range(0,len(topic_data)):
        if topic_data[i][0].id == profile.id:
            nt_rank = i+1
    
    alg_correct, alg_total, alg_score, combo_correct, combo_total, combo_score, geo_correct, geo_total, geo_score, nt_correct, nt_total, nt_score = profile.acgn(year)
    alg_total = alg_total.order_by('-drill_problem__percent_solved')
    combo_total = combo_total.order_by('-drill_problem__percent_solved')
    geo_total = geo_total.order_by('-drill_problem__percent_solved')
    nt_total = nt_total.order_by('-drill_problem__percent_solved')
    print(drill_records)
    context = {
        'profile':profile,
        'drill_records':drill_records,
        'problem_numbers':problem_numbers,
        'alg_correct':alg_correct,
        'alg_total':alg_total,
        'alg_score':alg_score,
        'combo_correct':combo_correct,
        'combo_total':combo_total,
        'combo_score':combo_score,
        'geo_correct':geo_correct,
        'geo_total':geo_total,
        'geo_score':geo_score,
        'nt_correct':nt_correct,
        'nt_total':nt_total,
        'nt_score':nt_score,
        'no_average':no_average,
        }
    
    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('drills/my_student_report.tex')
    rendered_tpl = template.render(context).encode('utf-8')
    with tempfile.TemporaryDirectory() as tempdir:
        fa = open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        context = {
            'tempdirect':tempdir,
            'profile':profile,
            'drill_records':drill_records,
            'problem_numbers':problem_numbers,
            'alg_correct':alg_correct,
            'alg_total':alg_total,
            'alg_score':alg_score,
            'combo_correct':combo_correct,
            'combo_total':combo_total,
            'combo_score':combo_score,
            'geo_correct':geo_correct,
            'geo_total':geo_total,
            'geo_score':geo_score,
            'nt_correct':nt_correct,
            'nt_total':nt_total,
            'nt_score':nt_score,
            'no_average':no_average,
            }
        template = get_template('drills/my_student_report.tex')
        rendered_tpl = template.render(context).encode('utf-8')
        ftex = open(os.path.join(tempdir,'texput.tex'),'wb')
        ftex.write(rendered_tpl)
        ftex.close()
        for i in range(1):
            process = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process.communicate()[0]
        L=os.listdir(tempdir)

        for i in range(0,len(L)):
            if L[i][-4:] == '.asy':
                process1 = Popen(
                    ['asy', L[i]],
                    stdin = PIPE,
                    stdout = PIPE,
                    cwd = tempdir,
                    )
                stdout_value = process1.communicate()[0]
        for i in range(2):
            process2 = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process2.communicate()[0]

        if 'texput.pdf' in os.listdir(tempdir):
            with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
                pdf = f.read()
                r = HttpResponse(content_type = 'application/pdf')
                r.write(pdf)
                r['Content-Disposition'] = 'attachment;filename="'+profile.name.replace(' ','')+'.pdf"'
                return r
        else:
            with open(os.path.join(tempdir, 'texput.log')) as f:
                error_text = f.read()
                return render(request,'randomtest/latex_errors.html',{'nbar':'drills','name':profile.name,'error_text':error_text})#####Perhaps the error page needs to be customized...  


@permission_required('drills.add_drill')
def drill_pdf_view(request,drill_id):
    drill = get_object_or_404(Drill, id = drill_id)
    context = {
        'drill':drill,
        }
    
    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('drills/my_drill_latex.tex')
    rendered_tpl = template.render(context).encode('utf-8')
    with tempfile.TemporaryDirectory() as tempdir:
        fa = open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        context = {
            'tempdirect':tempdir,
            'drill':drill,
            }
        template = get_template('drills/my_drill_latex.tex')
        rendered_tpl = template.render(context).encode('utf-8')
        ftex = open(os.path.join(tempdir,'texput.tex'),'wb')
        ftex.write(rendered_tpl)
        ftex.close()
        for i in range(1):
            process = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process.communicate()[0]
        L=os.listdir(tempdir)

        for i in range(0,len(L)):
            if L[i][-4:] == '.asy':
                process1 = Popen(
                    ['asy', L[i]],
                    stdin = PIPE,
                    stdout = PIPE,
                    cwd = tempdir,
                    )
                stdout_value = process1.communicate()[0]
        for i in range(2):
            process2 = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process2.communicate()[0]

        if 'texput.pdf' in os.listdir(tempdir):
            with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
                pdf = f.read()
                r = HttpResponse(content_type = 'application/pdf')
                r.write(pdf)
                r['Content-Disposition'] = 'attachment;filename="'+drill.readable_label.replace(' ','')+'.pdf"'
                return r
        else:
            with open(os.path.join(tempdir, 'texput.log')) as f:
                error_text = f.read()
                return render(request,'randomtest/latex_errors.html',{'nbar':'drills','name':drill.readable_label,'error_text':error_text})#####Perhaps the error page needs to be customized...  
            



@permission_required('drills.add_drill')
def drill_latex_view(request,drill_id):
    drill = get_object_or_404(Drill, id = drill_id)
    context = {
        'drill':drill,
        }
    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('drills/my_drill_latex.tex')
    content = template.render(context).encode('utf-8')
    filename = drill.readable_label.replace(' ','')+".tex"
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response

@permission_required('drills.add_drill')
def drill_solutions_pdf_view(request,drill_id):
    drill = get_object_or_404(Drill, id = drill_id)
    context = {
        'drill':drill,
        }
    
    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('drills/my_drill_solutions_latex.tex')
    rendered_tpl = template.render(context).encode('utf-8')
    with tempfile.TemporaryDirectory() as tempdir:
        fa = open(os.path.join(tempdir,'asymptote.sty'),'w')
        fa.write(asyr)
        fa.close()
        context = {
            'tempdirect':tempdir,
            'drill':drill,
            }
        template = get_template('drills/my_drill_solutions_latex.tex')
        rendered_tpl = template.render(context).encode('utf-8')
        ftex = open(os.path.join(tempdir,'texput.tex'),'wb')
        ftex.write(rendered_tpl)
        ftex.close()
        for i in range(1):
            process = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process.communicate()[0]
        L=os.listdir(tempdir)

        for i in range(0,len(L)):
            if L[i][-4:] == '.asy':
                process1 = Popen(
                    ['asy', L[i]],
                    stdin = PIPE,
                    stdout = PIPE,
                    cwd = tempdir,
                    )
                stdout_value = process1.communicate()[0]
        for i in range(2):
            process2 = Popen(
                ['pdflatex', 'texput.tex'],
                stdin = PIPE,
                stdout = PIPE,
                cwd = tempdir,
            )
            stdout_value = process2.communicate()[0]

        if 'texput.pdf' in os.listdir(tempdir):
            with open(os.path.join(tempdir, 'texput.pdf'), 'rb') as f:
                pdf = f.read()
                r = HttpResponse(content_type = 'application/pdf')
                r.write(pdf)
                r['Content-Disposition'] = 'attachment;filename="'+drill.readable_label.replace(' ','')+'-sols.pdf"'
                return r
        else:
            with open(os.path.join(tempdir, 'texput.log')) as f:
                error_text = f.read()
                return render(request,'randomtest/latex_errors.html',{'nbar':'drills','name':drill.readable_label,'error_text':error_text})#####Perhaps the error page needs to be customized...  


@permission_required('drills.add_drill')
def drill_solutions_latex_view(request,drill_id):
    drill = get_object_or_404(Drill, id = drill_id)
    context = {
        'drill':drill,
        }
    asyf = open(settings.BASE_DIR+'/asymptote.sty','r')
    asyr = asyf.read()
    asyf.close()
    template = get_template('drills/my_drill_solutions_latex.tex')
    content = template.render(context).encode('utf-8')
    filename = drill.readable_label.replace(' ','')+"-sols.tex"
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response

@permission_required('drills.add_drill')
def publish_drill(request,drill_id):
    drill = get_object_or_404(Drill, id = drill_id)
    year_folder = drill.year_folder
    year = str(year_folder.year)
    category = drill.year_folder.category
    num = drill.drill_problems.count()
    
    if not Type.objects.filter(label = category.name + ' Drill').exists():
        t = Type.objects.create(type = category.name + 'Drill',
                                label = category.name + ' Drill',
                                is_contest = True,
                                default_question_type = 'sa',
                                readable_label_post_form = ' #',
                                readable_label_pre_form = category.name + ' Drill',
                                )
    else:
        typ = Type.objects.get(label = category.name + ' Drill')
    sa = QuestionType.objects.get(question_type='short answer')
    formletter = ''
    #get or create round
    if Round.objects.filter(name = category.name + ' Drill Round ' + str(drill.number)).exists():
        round = Round.objects.get(name = category.name + ' Drill Round ' + str(drill.number))
    else:
        round = Round.objects.create(name = category.name + ' Drill Round ' + str(drill.number),type = typ, default_question_type = 'sa', readable_label_pre_form = category.name + " Drill Round "+str(drill.number), readable_label_post_form = " #")
        
    label = year + round.name.replace(' ','') + formletter
    readablelabel = year + ' ' + round.readable_label_pre_form + formletter
    default_question_type = sa
    readablelabel = readablelabel.rstrip()
    post_label = round.readable_label_post_form

    if ContestTest.objects.filter(short_label=label).exists() == True:
        return JsonResponse({'error':'Contest matching parameters already exists'})

    if round.type.allow_form_letter == True:
        if round.readable_label_pre_form[-1] == ' ':
            contest_label = year + ' ' + round.name + ' ' + formletter
        else:
            contest_label =  year + ' ' + round.name + formletter
    else:
        contest_label =  year + ' ' + round.name
    contest_test = ContestTest(contest_label = contest_label, contest_type = typ, round = round,year = year, form_letter = formletter,short_label = label)
    contest_test.save()
    LogEntry.objects.log_action(
        user_id = request.user.id,
        content_type_id = ContentType.objects.get_for_model(contest_test).pk,
        object_id = contest_test.id,
        object_repr = contest_test.contest_label+' ('+str(num)+')',
        action_flag = ADDITION,
        change_message = "problemeditor/redirectcontest/"+str(contest_test.pk)+'/',
    )

    for p in drill.drill_problems.all().order_by('order'):
        i = p.order
        problem_number_label = str(i)
        new_p = Problem.objects.create(problem_text = p.problem_text,
                    answer = p.answer,
                    sa_answer = p.answer,
                    label = label + problem_number_label,
                    readable_label = readablelabel + post_label + problem_number_label,
                    type_new = typ,
                    question_type_new = sa,
                    problem_number = i,
                    year = year,
                    form_letter = formletter,
                    test_label = label,
                    top_solution_number = 0,
                    contest_test = contest_test,
        )
        new_p.round = round
        new_p.types.add(typ)
        new_p.question_type.add(sa)
        new_p.save()
        compileasy(new_p.mc_problem_text,new_p.label)
        compileasy(new_p.problem_text,new_p.label)
        compiletikz(new_p.mc_problem_text,new_p.label)
        compiletikz(new_p.problem_text,new_p.label)
        new_p.display_problem_text = newtexcode(new_p.problem_text,new_p.label,'')
        new_p.display_mc_problem_text = newtexcode(new_p.mc_problem_text,new_p.label,new_p.answers())
        new_p.save()            
        for s in p.drillproblemsolution_set.all():
            new_p.add_solution(request,s.solution_text)
    return redirect('/drills/')
