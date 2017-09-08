from django.db import models

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from randomtest.models import Solution,Problem
from django.utils import timezone

# Create your models here.
class ProblemSet(models.Model):#could be a type of Section???
    name=models.CharField(max_length=150)

class TextBlock(models.Model):
    text_code = models.TextField(blank=True)
    text_display = models.TextField(blank=True)

class Proof(models.Model):
    prefix = models.CharField(max_length=20)#Theorem, Proposition, Lemma, Corollary, Example, Exercise
    proof_code = models.TextField(blank=True)
    proof_display = models.TextField(blank=True)
    isSolution = models.BooleanField(default=0)
    solution = models.ForeignKey(Solution,blank=True,null=True)

class Theorem(models.Model):
    name=models.CharField(max_length=150, default="")
    prefix = models.CharField(max_length=20)#Theorem, Proposition, Lemma, Corollary, Example, Exercise
    theorem_number = models.IntegerField()
    theorem_code = models.TextField(blank=True)
    theorem_display = models.TextField(blank=True)
    isProblem = models.BooleanField(default=0)
    problem = models.ForeignKey(Problem,blank=True,null=True)

    def __str__(self):
        return self.name

class SubSection(models.Model):
    name=models.CharField(max_length=150)
    def __str__(self):
        return self.name

class Section(models.Model):#possibly have an asterisk here...
    name=models.CharField(max_length=150)
    def __str__(self):
        return self.name

#class ImageModel(models.Model):
#    image = models.ImageField(upload_to='images')

class DocumentElement(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    chapter_number = models.IntegerField(default=0)
    section_number = models.IntegerField(default=0)
    subsection_number = models.IntegerField(default=0)
    order = models.IntegerField()
    class Meta:
        ordering = ['order']


class Handout(models.Model):
    name=models.CharField(max_length=150)
    document_elements = models.ManyToManyField(DocumentElement,blank=True)
    order = models.IntegerField(default=1)
    top_section_number = models.IntegerField(default=0)
    top_subsection_number = models.IntegerField(default=0)
    top_order_number = models.IntegerField(default=0)
    top_theorem_number = models.IntegerField(default=0)
    created_date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.name
