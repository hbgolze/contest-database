from django.db import models

from django.utils import timezone
from datetime import timedelta

from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType

from randomtest.models import UserProfile,QuestionType,UserProfile
# Create your models here.
class UserClass(models.Model):
    published_class = models.ForeignKey('teacher.PublishedClass',null=True,on_delete=models.SET_NULL)
    userprofile = models.ForeignKey(UserProfile,related_name = 'userclasses',null=True,on_delete=models.SET_NULL)
    total_points = models.IntegerField()
    points_earned = models.IntegerField()
    date_created = models.DateTimeField(default = timezone.now)
    num_problems = models.IntegerField(default=0)
    num_correct = models.IntegerField(default=0)
    class Meta:
        ordering = ['date_created']
    def update_stats(self):
        num_problems = 0
        points_earned = 0
        total_points = 0
        num_correct = 0
        for uu in self.userunit_set.all():
            uu.update_stats()
            total_points += uu.total_points
            points_earned += uu.points_earned
            num_correct += uu.num_correct
            num_problems += uu.num_problems
        self.points_earned = points_earned
        self.total_points = total_points
        self.num_correct = num_correct
        self.num_problems = num_problems
        self.save()
    def response_initialize(self):
        for uu in self.userunit_set.all():
            uu.response_initialize()

class UserUnit(models.Model):
    unit = models.ForeignKey('teacher.Unit',null=True,on_delete=models.SET_NULL)
    published_unit = models.ForeignKey('teacher.PublishedUnit',null=True,on_delete=models.SET_NULL)
    user_class = models.ForeignKey(UserClass,null=True,on_delete=models.CASCADE)
    total_points = models.IntegerField()
    points_earned = models.IntegerField()
    order = models.IntegerField(default = 0)
    num_problems = models.IntegerField(default=0)
    num_correct = models.IntegerField(default=0)
    num_problemsets = models.IntegerField(default=0)
    class Meta:
        ordering = ['order']
    def update_stats(self):
        num_problems = 0
        points_earned = 0
        total_points = 0
        num_correct = 0
        num_problemsets = 0
        for uo in self.userunitobject_set.all():
            try:
                u_pset = uo.userproblemset
                u_pset.update_stats()
                total_points += u_pset.total_points
                points_earned += u_pset.points_earned
                num_correct += u_pset.num_correct
                num_problems += u_pset.num_problems
                num_problemsets += 1
            except:
                a=0
        self.points_earned = points_earned
        self.total_points = total_points
        self.num_correct = num_correct
        self.num_problems = num_problems
        self.num_problemsets = num_problemsets
        self.order = self.published_unit.order# not updating stats, but prevents redundancy
        self.save()
    def response_initialize(self):
        for uo in self.userunitobject_set.all():
            try:
                u_pset = uo.userproblemset
                u_pset.response_initialize()
            except:
                a=0

class UserUnitObject(models.Model):
    unit_object = models.ForeignKey('teacher.PublishedUnitObject',null = True,on_delete=models.SET_NULL)
    user_unit = models.ForeignKey(UserUnit,null=True,on_delete=models.CASCADE)
    order = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']

class UserProblemSet(models.Model):
    userunitobject = models.OneToOneField(
        UserUnitObject,
        on_delete=models.CASCADE,
#        primary_key=True,
        null = True,
    )
    problemset = models.ForeignKey('teacher.ProblemSet',null = True,on_delete=models.SET_NULL)
    published_problemset = models.ForeignKey('teacher.PublishedProblemSet',null = True,on_delete=models.SET_NULL)
    total_points = models.IntegerField()
    points_earned = models.IntegerField()
    num_problems = models.IntegerField(default = 0)
    num_correct = models.IntegerField(default = 0)
    is_initialized = models.BooleanField(default = 0)
    in_progress = models.BooleanField(default = 0)
    is_graded = models.BooleanField(default = 0)
    start_time = models.DateTimeField(null = True)
    def update_stats(self):
        print(self.pk,'update ups start')
        self.num_problems = self.published_problemset.problem_objects.count()
        total_points = 0
        for po in self.published_problemset.problem_objects.all():
            total_points += po.point_value
        points = 0
        num_correct = 0
        for r in self.response_set.all():
            po = r.publishedproblem_object
            if po.isProblem:
                if po.question_type.question_type == 'multiple choice':
                    if r.response == po.problem.mc_answer:
                        num_correct += 1
                        points += r.point_value 
                elif po.question_type.question_type == 'short answer':
                    if r.response == po.problem.sa_answer:
                        num_correct += 1
                        points += r.point_value
            else:
                if po.question_type.question_type == 'multiple choice':
                    if r.response == po.mc_answer:
                        num_correct += 1
                        points += r.point_value
                elif po.question_type.question_type == 'short answer':
                    if r.response == po.sa_answer:
                        num_correct += 1
                        points += r.point_value
        self.points_earned = points
        self.total_points = total_points
        self.num_correct = num_correct
        print('mid')
        print('mid2')
        self.save()
        print(self.pk,'update ups end')
    def response_initialize(self):
        R = self.response_set.all()
        for p in self.published_problemset.problem_objects.all():
            if R.filter(publishedproblem_object = p).exists() == False:
                r = Response(publishedproblem_object = p, user_problemset = self,order=p.order,point_value = p.point_value,response="")
                r.save()
        self.is_initialized = True
        self.save()

class UserSlides(models.Model):
    userunitobject = models.OneToOneField(
        UserUnitObject,
        on_delete=models.CASCADE,
#        primary_key=True,
        null = True,
    )
    slides = models.ForeignKey('teacher.SlideGroup',null=True,on_delete=models.SET_NULL)
    published_slides = models.ForeignKey('teacher.PublishedSlideGroup',null=True,on_delete=models.SET_NULL)
    num_slides = models.IntegerField(default = 0)

class UserTest(models.Model):
    userunitobject = models.OneToOneField(
        UserUnitObject,
        on_delete=models.CASCADE,
#        primary_key=True,
        null = True,
    )
    test = models.ForeignKey('teacher.Test',null=True,on_delete=models.SET_NULL)
    published_test = models.ForeignKey('teacher.PublishedTest',null=True,on_delete=models.SET_NULL)
    total_points = models.IntegerField()
    points_earned = models.FloatField()
    num_problems = models.IntegerField(default = 0)
    num_correct = models.IntegerField(default = 0)
    is_initialized = models.BooleanField(default = 0)
    in_progress = models.BooleanField(default = 0)
    is_graded = models.BooleanField(default = 0)
    start_time = models.DateTimeField(null = True)
    def is_in_progress(self):
        if self.start_time == None:
            return False
        t=timezone.now()
        if t > self.start_time+timedelta(hours=self.published_test.time_limit.hour, minutes = self.published_test.time_limit.minute):
            return False
        return True
    def end_time(self):
        return self.start_time+timedelta(hours=self.published_test.time_limit.hour, minutes = self.published_test.time_limit.minute)
    def completed(self):
        if self.start_time == None:
            return False
        t=timezone.now()
        if t <= self.start_time+timedelta(hours=self.published_test.time_limit.hour, minutes = self.published_test.time_limit.minute):
            return False
        return True
    def update_stats(self):
        self.num_problems = self.published_test.problem_objects.count()
        total_points = 0
        for po in self.published_test.problem_objects.all():
            total_points += po.point_value
        points = 0
        num_correct = 0
        for r in self.response_set.all():
            po = r.publishedproblem_object
            if po.isProblem:
                if po.question_type.question_type == 'multiple choice':
                    if r.response == po.problem.mc_answer:
                        num_correct += 1
                        points += r.point_value
                elif po.question_type.question_type == 'short answer':
                    if r.response == po.problem.sa_answer:
                        num_correct += 1
                        points += r.point_value
            else:
                if r.response == po.answer:
                    num_correct += 1
                    points += r.point_value
        self.points_earned = points
        self.total_points = total_points
        self.num_correct = num_correct
        self.save()
    def response_initialize(self):
        R = self.response_set.all()
        for p in self.published_test.problem_objects.all():
            if R.filter(publishedproblem_object = p).exists() == False:
                r = Response(publishedproblem_object = p, user_test = self,order = p.order,point_value = p.point_value,response = "")
                r.save()
        self.is_initialized = True
        self.save()

#? Is order changed?
class Response(models.Model):
    problem_object = models.ForeignKey('teacher.ProblemObject',null=True,on_delete=models.SET_NULL)
    publishedproblem_object = models.ForeignKey('teacher.PublishedProblemObject',null=True,on_delete=models.SET_NULL)
    user_problemset = models.ForeignKey(UserProblemSet,null=True,on_delete=models.CASCADE)
    user_test = models.ForeignKey(UserTest,null=True,on_delete=models.CASCADE)
    response = models.CharField(max_length=50,blank=True)
    response_code = models.TextField(blank=True)
    display_response = models.TextField(blank=True)
    attempted = models.BooleanField(default = 0)
    stickied = models.BooleanField(default = 0)
    order = models.IntegerField(default = 0)
    points = models.IntegerField(default = 0)
    point_value = models.IntegerField(default = 1)
    blank_point_value = models.IntegerField(default = 0)
    is_graded = models.BooleanField(default = 0)
    modified_date = models.DateTimeField(default = timezone.now)
    num_attempts = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']

class Sticky(models.Model):
    response = models.ForeignKey(Response,null=True,on_delete=models.CASCADE)
    sticky_date = models.DateTimeField(default = timezone.now)
    problemset = models.ForeignKey(UserProblemSet,null=True,on_delete=models.CASCADE)
    test = models.ForeignKey(UserTest,null=True,on_delete=models.CASCADE)
    userprofile = models.ForeignKey(UserProfile,related_name = "student_stickies",null=True,on_delete=models.CASCADE)
    readable_label = models.CharField(max_length=30,blank=True)
    def __str__(self):
        return self.problemset.published_problemset.name+' #'+str(self.response.order)#changed to published_problemset

class UserResponse(models.Model):
    userprofile = models.ForeignKey(UserProfile,null=True,related_name = "student_responselog",on_delete=models.CASCADE)
    user_problemset = models.ForeignKey(UserProblemSet,null=True,on_delete=models.CASCADE)
    response = models.ForeignKey(Response,null=True,on_delete=models.CASCADE)#check this on_delete....
    static_response = models.CharField(max_length=10,blank=True)
    readable_label = models.CharField(max_length=30)
    modified_date = models.DateTimeField(default = timezone.now)
    correct = models.BooleanField(default = 0)
    point_value = models.IntegerField(default=0)
