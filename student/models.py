from django.db import models

from django.utils import timezone

from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType

from randomtest.models import UserProfile,QuestionType,UserProfile
from teacher.models import PublishedClass,ProblemObject,Unit,ProblemSet,SlideGroup
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

class UserUnit(models.Model):
    unit = models.ForeignKey(Unit)
    user_class = models.ForeignKey(UserClass)
    total_points = models.IntegerField()
    points_earned = models.IntegerField()
    order = models.IntegerField(default = 0)
    num_problems = models.IntegerField(default=0)
    num_correct = models.IntegerField(default=0)
    num_problemsets = models.IntegerField(default=0)
    class Meta:
        ordering = ['order']


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
#    user_unit = models.ForeignKey(UserUnit)
    total_points = models.IntegerField()
    points_earned = models.IntegerField()
    order = models.IntegerField(default = 0)
    num_problems = models.IntegerField(default=0)
    num_correct = models.IntegerField(default=0)
    is_initialized = models.BooleanField(default=0)
    class Meta:
        ordering = ['order']


class UserSlides(models.Model):
    userunitobject = models.OneToOneField(
        UserUnitObject,
        on_delete=models.CASCADE,
#        primary_key=True,
        null = True,
    )
    slides = models.ForeignKey(SlideGroup)
#    user_unit = models.ForeignKey(UserUnit)
    order = models.IntegerField(default = 0)
    num_slides = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']

class Response(models.Model):
    problem_object = models.ForeignKey(ProblemObject)
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
