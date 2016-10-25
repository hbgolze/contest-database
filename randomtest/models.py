from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Dropboxurl(models.Model):
    url=models.CharField(max_length=100)
    def __str__(self):
        return self.url

class Tag(models.Model):
    tag = models.CharField(max_length=50)
    def __str__(self):
        return self.tag

class Type(models.Model):
    type = models.CharField(max_length=10)
    label= models.CharField(max_length=20,blank=True)
    def __str__(self):
        return self.label

class QuestionType(models.Model):#multiple choice; short answer; proof
    question_type = models.CharField(max_length=20)
    def __str__(self):
        return self.question_type

class Solution(models.Model):
    solution_text = models.TextField()
    solution_number = models.IntegerField(default=1)
    problem_label = models.CharField(max_length=20,blank=True)
    tags = models.ManyToManyField(Tag,blank=True)

class Answer(models.Model):
    answer = models.CharField(max_length=10,blank=True)
    problem_label = models.CharField(max_length=20)
    def __str__(self):
        return self.answer

class Problem(models.Model):
    problem_number = models.IntegerField()
    tags = models.ManyToManyField(Tag,related_name='problems')
    year = models.IntegerField()
    types = models.ManyToManyField(Type)#type (AMC8,AMC10,AMC12,AIME,USAMO, etc... multiple types...?)
    answer = models.CharField(max_length=20)
    label = models.CharField(max_length=20)
    problem_text = models.TextField(blank=True)
    form_letter = models.CharField(max_length=2,blank=True)
    test_label = models.CharField(max_length=20,blank=True)
    question_type = models.ManyToManyField(QuestionType)
    solutions = models.ManyToManyField(Solution)
    def __str__(self):
        return self.label
    def print_tags(self):
        s = ''
        L = list(self.tags.all())
        if len(L)>0:
            s = L[0].tag
        for i in range(1,len(L)):
            s += ', '+L[i].tag
        return s

class Test(models.Model):
    name = models.CharField(max_length=50)#Perhaps use a default naming scheme
    problems = models.ManyToManyField(Problem)
    answers = models.ManyToManyField(Answer,blank=True,related_name='parent_test')
    num_problems_correct = models.IntegerField()
    types = models.ManyToManyField(Type)
    created_date = models.DateTimeField(default = timezone.now)
    last_attempted_date = models.DateTimeField(default = timezone.now)
    def __str__(self):
        return self.name
    def print_types(self):
        s = ''
        L = list(self.types.all())
        if len(L)>0:
            s = L[0].type
        for i in range(1,len(L)):
            s += ', '+L[i].type
        return s
    def delete(self, *args, **kwargs):
        A=list(self.answers.all())
        for i in range(0,len(A)):
            A[i].delete()
        super(Test, self).delete(*args, **kwargs)

class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)
    tests = models.ManyToManyField(Test, blank=True)
    # The additional attributes we wish to include.
#    website = models.URLField(blank=True)
#    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username
