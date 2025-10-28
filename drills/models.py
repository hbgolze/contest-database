from django.db import models

from randomtest.models import Type

# Create your models here.
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)
    class Meta:
        ordering = ['name']

class YearFolder(models.Model):
    year = models.IntegerField()
    top_number = models.IntegerField(default = 0)
    category = models.ForeignKey(Category,related_name='years',on_delete=models.CASCADE,null=True)
    active = models.BooleanField(default = True)
    
    def __str__(self):
        return str(self.year)
    class Meta:
        ordering = ['year']

class Drill(models.Model):
    year_folder = models.ForeignKey(YearFolder,related_name='drills',on_delete=models.CASCADE,null=True)
    year = models.IntegerField()
    number = models.IntegerField()
    readable_label = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    created_date = models.DateTimeField(default=timezone.now)
    problem_count = models.IntegerField()
    average_score = models.FloatField(default=0)
    num_participants = models.IntegerField(default=0)

    def __str__(self):
        return self.readable_label
    def update_stats(self):
        L = []
        for dr in self.drill_records.all():
            L.append(dr.score)
        self.average_score = sum(L)/len(L)
        self.num_participants = len(L)
        self.save()
        for p in self.drill_problems.all():
            p.update_stats()
    class Meta:
        ordering = ['number']

class DrillTask(models.Model):
    TOPIC_CHOICES = [
        ('Algebra', 'Algebra'),
        ('Arithmetic','Arithmetic'),
        ('Geometry', 'Geometry'),
        ('Combinatorics', 'Combinatorics'),
        ('Number Theory', 'Number Theory'),
        ('Bonus', 'Bonus'),
    ]
    description = models.TextField()
    topic = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    category = models.ForeignKey(Category,related_name='drill_tasks',on_delete=models.CASCADE,null=True)
    
    def __str__(self):
        return self.description
    def most_recent_usage(self,year):
        problems = self.drillproblem_set.filter(drill__year_folder=year)
        uses = [p.drill.number for p in problems]
        if len(uses) > 0:
            return max(uses)
        else:
            return 'N/A'

class DrillProblem(models.Model):
    TOPIC_CHOICES = [
        ('Algebra', 'Algebra'),
        ('Arithmetic', 'Arithmetic'),
        ('Geometry', 'Geometry'),
        ('Combinatorics', 'Combinatorics'),
        ('Number Theory', 'Number Theory'),
        ('Bonus', 'Bonus'),
    ]
    order = models.IntegerField()
    label = models.CharField(max_length=255)
    readable_label = models.CharField(max_length=255)
    drill = models.ForeignKey(Drill, related_name = 'drill_problems',on_delete=models.CASCADE)
    problem_text = models.TextField()
    display_problem_text = models.TextField()
    topic = models.CharField(max_length=255)
    drill_task = models.ForeignKey(DrillTask, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)
    percent_solved = models.FloatField()
    number_solved = models.IntegerField()
    is_bonus = models.BooleanField(default=False)

    def __str__(self):
        return self.readable_label
    def update_stats(self):
        problem_records = self.drillrecordproblem_set.all()
        self.number_solved = problem_records.filter(status=1).count()
        self.percent_solved = 100*self.number_solved/(max(1,problem_records.count()))
        self.save()
    def update_order(self,i):
        self.order = i
        self.label = str(self.drill.year_folder.year) + self.drill.year_folder.category.replace(' ','') + 'Drill'+str(self.drill.number)+'-'+str(i)
        self.readable_label = str(self.drill.year_folder.year) + ' ' + self.drill.year_folder.category + ' Drill '+str(self.drill.number)+' #'+str(i)
        self.save()
        for drp in self.drillrecordproblem_set.all():
            drp.order = i
            drp.save()
    def renumber_solutions(self):
        i=1
        for s in self.drillproblemsolution_set.all():
            s.order = i
            s.save()
            i += 1
    class Meta:
        ordering = ['order']

class DrillProblemSolution(models.Model):
    order = models.IntegerField()
    solution_text = models.TextField()
    display_solution_text = models.TextField()
    drill_problem = models.ForeignKey(DrillProblem, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Solution {self.order} for {self.drill_problem.readable_label}"
    class Meta:
        ordering = ['order']

class DrillProfile(models.Model):
    name = models.CharField(max_length=255)
    year = models.ManyToManyField(YearFolder,related_name="profiles")

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']
    def acgn(self,year):
        alg_total = DrillRecordProblem.objects.filter(drillrecord__drill_profile__id=self.id).filter(drillrecord__drill__year_folder=year).filter(drill_problem__drill_task__topic='Algebra')
        combo_total = DrillRecordProblem.objects.filter(drillrecord__drill_profile__id=self.id).filter(drillrecord__drill__year_folder=year).filter(drill_problem__drill_task__topic='Combinatorics')
        geo_total = DrillRecordProblem.objects.filter(drillrecord__drill_profile__id=self.id).filter(drillrecord__drill__year_folder=year).filter(drill_problem__drill_task__topic='Geometry')
        nt_total = DrillRecordProblem.objects.filter(drillrecord__drill_profile__id=self.id).filter(drillrecord__drill__year_folder=year).filter(drill_problem__drill_task__topic='Number Theory')
        alg_correct = alg_total.filter(status=1)
        combo_correct = combo_total.filter(status=1)
        geo_correct = geo_total.filter(status=1)
        nt_correct = nt_total.filter(status=1)
        alg_score = alg_correct.count()/max(1,alg_total.count())
        combo_score = combo_correct.count()/max(1,combo_total.count())
        geo_score = geo_correct.count()/max(1,geo_total.count())
        nt_score = nt_correct.count()/max(1,nt_total.count())
        return (alg_correct, alg_total, alg_score, combo_correct, combo_total, combo_score, geo_correct, geo_total, geo_score, nt_correct, nt_total, nt_score)
    def score(self,year):
        drill_records = self.drillrecord_set.filter(drill__year_folder = year)
        t = 0
        for i in drill_records:
            t+=i.score
        return t
        

class DrillRecord(models.Model):
    drill_profile = models.ForeignKey(DrillProfile, on_delete=models.CASCADE)
    drill = models.ForeignKey(Drill, related_name='drill_records',on_delete=models.CASCADE)
    score = models.IntegerField()# score for non-bonus problems
    total_score = models.IntegerField(default = 0)
    bonus_score = models.IntegerField(default = 0)
    
    def __str__(self):
        return f"{self.drill_profile.name} - {self.drill.readable_label}"
    class Meta:
        ordering = ['-score']
    def update_score(self):
        problems = self.drill_record_problems.filter(drill_problem__is_bonus = False)
        bonus_problems = self.drill_record_problems.filter(drill_problem__is_bonus = True)
        score,bonus_score = 0,0
        for p in problems:
            if p.status == 1:
                score += 1
        for p in bonus_problems:
            if p.status == 1:
                bonus_score += 1
        self.score = score
        self.bonus_score = bonus_score
        self.total_score = score + bonus_score
        self.save()

class DrillRecordProblem(models.Model):
    drillrecord = models.ForeignKey(DrillRecord, related_name='drill_record_problems', on_delete=models.CASCADE)
    order = models.IntegerField()
    drill_problem = models.ForeignKey(DrillProblem, on_delete=models.CASCADE)
    status = models.IntegerField(choices=[(1, 'Correct'), (0, 'Incorrect'), (-1,'Blank')])
    silly_mistake = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.drillrecord.drill_profile.name} - {self.drill_problem.readable_label}"
    class Meta:
        ordering = ['order']

class DrillAssignment(models.Model):
    number = models.IntegerField(default=1)
    problem_tasks = models.ManyToManyField(DrillTask)
    author = models.CharField(max_length=255)
    year = models.ForeignKey(YearFolder,related_name='assignments',on_delete=models.CASCADE,null=True)
    def __str__(self):
        return f"Assignment by {self.author}"
    class Meta:
        ordering = ['number']
