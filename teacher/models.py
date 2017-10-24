from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType

from randomtest.models import Problem,Solution,QuestionType
# Create your models here.

class Class(models.Model):#This should be reserved for drafts of classes; also, curated (i.e., professionally done) classes will appear here, which can be copied directly (or used as a template)/starting point
    name = models.CharField(max_length = 100)
    created_date = models.DateTimeField(default = timezone.now)
    units = models.ManyToManyField('Unit',blank = True)# or foreignkey
    def __str__(self):
        return self.name
#Should I include a Version number?


class PublishedClass(models.Model):#class?
    name = models.CharField(max_length = 100)
    enrolled_students = models.ManyToManyField(User, blank = True)# or userprofile?
    created_date = models.DateTimeField(default = timezone.now)
    units = models.ManyToManyField('Unit',blank=True)
    total_points = models.IntegerField(default = 0)
    num_problems = models.IntegerField(default = 0)
    def __str__(self):
        return self.name

class Unit(models.Model):#with order
    name = models.CharField(max_length = 100)
    order = models.IntegerField(default = 0)
    total_points = models.IntegerField(default=0)
    num_problems = models.IntegerField(default=0)
    num_problemsets = models.IntegerField(default=0)
    class Meta:
        ordering = ['order']


class UnitObject(models.Model):#generic; with order...can be slides or Pset
    order = models.IntegerField(default = 0)
#    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#    object_id = models.PositiveIntegerField()
#    content_object = GenericForeignKey('content_type', 'object_id')
    unit = models.ForeignKey(Unit,related_name='unit_objects')
    class Meta:
        ordering = ['order']

class SlideGroup(models.Model):#like Handout, but more punctuated; problems can be included, but only short answer and multiple choice will be checked
    unit_object = models.OneToOneField(
        UnitObject,
        on_delete=models.CASCADE,
        null = True,
    )
    name = models.CharField(max_length = 100)
    created_date = models.DateTimeField(default = timezone.now)
#    unit_objects = GenericRelation(UnitObject)#??????
    num_slides = models.IntegerField(default = 0)
    def __str__(self):
        return self.name

class Slide(models.Model):#(i.e., slide 1...etc)
    title = models.CharField(max_length = 100)
    order = models.IntegerField(default = 0)
    slidegroup = models.ForeignKey(SlideGroup,related_name='slides')
    top_order_number = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']
    def __str__(self):
        return self.title

class SlideObject(models.Model):#placeholder for components
    order = models.IntegerField(default = 0)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    slide = models.ForeignKey(Slide,related_name='slide_objects')
    class Meta:
        ordering = ['order']

#theorem, problem, image, textblock,proof,solution (are these dependent?)

class TextBlock(models.Model):
    text_code = models.TextField(blank=True)
    text_display = models.TextField(blank=True)

class Proof(models.Model):
    prefix = models.CharField(max_length=20)#Proof, Solution
    proof_code = models.TextField(blank=True)
    proof_display = models.TextField(blank=True)
    isSolution = models.BooleanField(default=0)
    solution = models.ForeignKey(Solution,blank=True,null=True)

class Theorem(models.Model):
    name=models.CharField(max_length=150, default="")
    prefix = models.CharField(max_length=20)#Theorem, Proposition, Lemma, Corollary
    theorem_code = models.TextField(blank=True)
    theorem_display = models.TextField(blank=True)
    def __str__(self):
        return self.name

class ExampleProblem(models.Model):
    name=models.CharField(max_length=150, default="")
    prefix = models.CharField(max_length=20,default="")#Example, Exercise
    problem_code = models.TextField(blank=True)
    problem_display = models.TextField(blank=True)
    isProblem = models.BooleanField(default=0)
    problem = models.ForeignKey(Problem,blank=True,null=True)
    question_type = models.ForeignKey(QuestionType,blank=True,null=True)
    mc_answer = models.CharField(max_length=1,default = "")
    sa_answer = models.CharField(max_length = 20, default = "")
    answer_A = models.CharField(max_length=500,blank=True)
    answer_B = models.CharField(max_length=500,blank=True)
    answer_C = models.CharField(max_length=500,blank=True)
    answer_D = models.CharField(max_length=500,blank=True)
    answer_E = models.CharField(max_length=500,blank=True)
    author = models.ForeignKey(User,related_name='example_problem',blank=True,null=True)
    created_date = models.DateTimeField(default = timezone.now)
    def __str__(self):
        return self.name
    def answers(self):
        s='\n\n$\\textbf{(A) }'+self.answer_A
        if len(self.answer_A)>0 and self.answer_A[-1]=='\\':
            s+='\\\n\\textbf{(B) }'+self.answer_B
        else:
            s+='\\qquad\\textbf{(B) }'+self.answer_B
        if len(self.answer_B)>0 and self.answer_B[-1]=='\\':
            s+='\\\n\\textbf{(C) }'+self.answer_C
        else:
            s+='\\qquad\\textbf{(C) }'+self.answer_C
        if len(self.answer_C)>0 and self.answer_C[-1]=='\\':
            s+='\\\n\\textbf{(D) }'+self.answer_D
        else:
            s+='\\qquad\\textbf{(D) }'+self.answer_D
        if len(self.answer_D)>0 and self.answer_D[-1]=='\\':
            s+='\\\n\\textbf{(E) }'+self.answer_E
        else:
            s+='\\qquad\\textbf{(E) }'+self.answer_E
        return s+'$\n\n'

class ImageModel(models.Model):
    image = models.ImageField(upload_to='images')

class ProblemSet(models.Model):#like NewTest
    unit_object = models.OneToOneField(
        UnitObject,
        on_delete=models.CASCADE,
        null = True,
    )
    name = models.CharField(max_length = 100)
    created_date = models.DateTimeField(default = timezone.now)
    problem_objects = models.ManyToManyField('ProblemObject',blank=True)
    default_point_value = models.IntegerField(default = 1)
#    unit_objects = GenericRelation(UnitObject)#??????
    total_points = models.IntegerField(default=0)
    num_problems = models.IntegerField(default=0)
    def __str__(self):
        return self.name

class ProblemObject(models.Model):
    order = models.IntegerField(default = 0)
    point_value = models.IntegerField(default = 1)
    problem_code = models.TextField(blank=True)
    problem_display = models.TextField(blank=True)
    isProblem = models.BooleanField(default=0)
    problem = models.ForeignKey(Problem,blank=True,null=True)
    question_type = models.ForeignKey(QuestionType,null=True)
    mc_answer=models.CharField(max_length=1,blank=True)
    sa_answer = models.CharField(max_length = 20,blank=True)
    answer_A = models.CharField(max_length=500,blank=True)
    answer_B = models.CharField(max_length=500,blank=True)
    answer_C = models.CharField(max_length=500,blank=True)
    answer_D = models.CharField(max_length=500,blank=True)
    answer_E = models.CharField(max_length=500,blank=True)
    author = models.ForeignKey(User,related_name='problem_object',blank=True,null=True)
    created_date = models.DateTimeField(default = timezone.now)
    class Meta:
        ordering = ['order']
    def answers(self):
        s='\n\n$\\textbf{(A) }'+self.answer_A
        if len(self.answer_A)>0 and self.answer_A[-1]=='\\':
            s+='\\\n\\textbf{(B) }'+self.answer_B
        else:
            s+='\\qquad\\textbf{(B) }'+self.answer_B
        if len(self.answer_B)>0 and self.answer_B[-1]=='\\':
            s+='\\\n\\textbf{(C) }'+self.answer_C
        else:
            s+='\\qquad\\textbf{(C) }'+self.answer_C
        if len(self.answer_C)>0 and self.answer_C[-1]=='\\':
            s+='\\\n\\textbf{(D) }'+self.answer_D
        else:
            s+='\\qquad\\textbf{(D) }'+self.answer_D
        if len(self.answer_D)>0 and self.answer_D[-1]=='\\':
            s+='\\\n\\textbf{(E) }'+self.answer_E
        else:
            s+='\\qquad\\textbf{(E) }'+self.answer_E
        return s+'$\n\n'    

#perhaps newresponse should have a generic reference....
#units....manytomany or foreign key?
#standalone units? or just allow copying from another Class?
#standalone slides?
