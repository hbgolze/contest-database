from django.db import models

from django.utils import timezone

from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType

from randomtest.models import UserProfile,QuestionType,UserProfile
from teacher.models import PublishedClass,ProblemObject,Unit,ProblemSet,SlideGroup,PublishedProblemObject,PublishedUnit,PublishedProblemSet,PublishedSlideGroup
# Create your models here.
class UserClass(models.Model):
    published_class = models.ForeignKey(PublishedClass)
    userprofile = models.ForeignKey(UserProfile,related_name = 'userclasses')
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
    unit = models.ForeignKey(Unit)
    published_unit = models.ForeignKey(PublishedUnit,null=True)
    user_class = models.ForeignKey(UserClass)
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
        for uo in self.userunitobject_set.all():
            try:
                u_pset = uo.userproblemset
                u_pset.update_stats()
                total_points += u_pset.total_points
                points_earned += u_pset.points_earned
                num_correct += u_pset.num_correct
                num_problems += u_pset.num_problems
            except:
                a=0
        self.points_earned = points_earned
        self.total_points = total_points
        self.num_correct = num_correct
        self.num_problems = num_problems
        self.save()
    def response_initialize(self):
        for uo in self.userunitobject_set.all():
            try:
                u_pset = uo.userproblemset
                u_pset.response_initialize()
            except:
                a=0

class UserUnitObject(models.Model):
    user_unit = models.ForeignKey(UserUnit)
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
    problemset = models.ForeignKey(ProblemSet)
    published_problemset = models.ForeignKey(PublishedProblemSet,null=True)
    total_points = models.IntegerField()
    points_earned = models.IntegerField()
    order = models.IntegerField(default = 0)
    num_problems = models.IntegerField(default=0)
    num_correct = models.IntegerField(default=0)
    is_initialized = models.BooleanField(default=0)
    class Meta:
        ordering = ['order']
    def update_stats(self):
        self.num_problems = self.response_set.count()
        points = 0
        total_points = 0
        num_correct = 0
        for r in self.response_set.all():
            total_points += r.point_value
            po = r.problem_object
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
        R=self.response_set.all()
        for p in self.problemset.problem_objects.all():
            if R.filter(problem_object = p).exists()==False:
                r = Response(problem_object = p, user_problemset = self,order=p.order,point_value = p.point_value,response="")
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
    slides = models.ForeignKey(SlideGroup)
    published_slides = models.ForeignKey(PublishedSlideGroup,null=True)
    order = models.IntegerField(default = 0)
    num_slides = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']

class Response(models.Model):
    problem_object = models.ForeignKey(ProblemObject)
    publishedproblem_object = models.ForeignKey(PublishedProblemObject,null=True)
    user_problemset = models.ForeignKey(UserProblemSet)
    response = models.CharField(max_length=50,blank=True)
    response_code = models.TextField(blank=True)
    display_response = models.TextField(blank=True)
    attempted = models.BooleanField(default = 0)
    stickied = models.BooleanField(default = 0)
    order = models.IntegerField(default = 0)
    points = models.IntegerField(default = 0)
    point_value = models.IntegerField(default = 1)
    is_graded = models.BooleanField(default = 0)
    modified_date = models.DateTimeField(default = timezone.now)
    class Meta:
        ordering = ['order']

class Sticky(models.Model):
    response = models.ForeignKey(Response)
    sticky_date = models.DateTimeField(default = timezone.now)
    problemset = models.ForeignKey(UserProblemSet)
    userprofile = models.ForeignKey(UserProfile,related_name = "student_stickies",null=True)
    readable_label = models.CharField(max_length=30,blank=True)
    def __str__(self):
        return self.problemset.problemset.name+' #'+self.response.order

class UserResponse(models.Model):
    userprofile = models.ForeignKey(UserProfile,related_name = "student_responselog")
    user_problemset = models.ForeignKey(UserProblemSet)
    response = models.ForeignKey(Response)
    static_response = models.CharField(max_length=10,blank=True)
    readable_label = models.CharField(max_length=30)
    modified_date = models.DateTimeField(default = timezone.now)
    correct = models.BooleanField(default = 0)
    point_value = models.IntegerField(default=0)
