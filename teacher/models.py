from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType

from randomtest.models import Problem,Solution,QuestionType
from randomtest.utils import newtexcode, compileasy
# Create your models here.

class Class(models.Model):#This should be reserved for drafts of classes; also, curated (i.e., professionally done) classes will appear here, which can be copied directly (or used as a template)/starting point
    name = models.CharField(max_length = 100)
    created_date = models.DateTimeField(default = timezone.now)
    units = models.ManyToManyField('Unit',blank = True)# or foreignkey
    def __str__(self):
        return self.name
#Should I include a Version number?
    def publish(self,userprofile):
        p=PublishedClass(name=self.name,parent_class = self)
        p.save()
        class_points = 0
        class_prob_num = 0
        for u in self.units.all():
            new_unit = u.publish(p)
            class_points += new_unit.total_points
            class_prob_num += new_unit.num_problems
        p.total_points = class_points
        p.num_problems = class_prob_num
        p.save()
        userprofile.my_published_classes.add(p)
        userprofile.save()
        return p

class PublishedClass(models.Model):#class?
    parent_class = models.ForeignKey(Class, null=True,on_delete=models.SET_NULL)
    name = models.CharField(max_length = 100)
    enrolled_students = models.ManyToManyField(User, blank = True)# or userprofile?
    created_date = models.DateTimeField(default = timezone.now)
    units = models.ManyToManyField('Unit',blank=True)
    total_points = models.IntegerField(default = 0)
    num_problems = models.IntegerField(default = 0)
    def __str__(self):
        return self.name

class Unit(models.Model):#with order
    parent_unit = models.ForeignKey("self",null=True,on_delete=models.SET_NULL)
    name = models.CharField(max_length = 100)
    order = models.IntegerField(default = 0)
    total_points = models.IntegerField(default=0)
    num_problems = models.IntegerField(default=0)
    num_problemsets = models.IntegerField(default=0)
    is_published = models.BooleanField(default = 0)
    class Meta:
        ordering = ['order']
    def publish(self,published_class):
        new_unit = Unit(name=self.name,order=self.order,is_published = 1,parent_unit = self)
        new_unit.save()
        published_class.units.add(new_unit)
        published_class.save()

        unit_points = 0
        unit_num_problems = 0
        num_problemsets = 0
        for uo in self.unit_objects.all():
            try:
                sg = uo.slidegroup
                new_uo = uo.publish(new_unit)
            except:
                pset = uo.problemset
                new_uo = uo.publish(new_unit)
                num_problemsets += 1
                unit_num_problems += new_uo.problemset.num_problems
                unit_points += new_uo.problemset.total_points
        new_unit.total_points = unit_points
        new_unit.num_problems = unit_num_problems
        new_unit.num_problemsets = num_problemsets
        new_unit.save()
        return new_unit

class UnitObject(models.Model):#generic; with order...can be slides or Pset
    parent_unitobject = models.ForeignKey("self",null=True,on_delete=models.SET_NULL)
    order = models.IntegerField(default = 0)
#    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#    object_id = models.PositiveIntegerField()
#    content_object = GenericForeignKey('content_type', 'object_id')
    unit = models.ForeignKey(Unit,related_name='unit_objects')
    is_published = models.BooleanField(default = 0)
    class Meta:
        ordering = ['order']
    def publish(self,published_unit):
        new_unit_object = UnitObject(unit = published_unit,order = self.order,parent_unitobject = self,is_published = 1)
        new_unit_object.save()
        try:
            sg = self.slidegroup
            sg.publish(new_unit_object)
        except:
            pset = self.problemset
            pset.publish(new_unit_object)
        return new_unit_object

class SlideGroup(models.Model):#like Handout, but more punctuated; problems can be included, but only short answer and multiple choice will be checked
    unit_object = models.OneToOneField(
        UnitObject,
        on_delete=models.CASCADE,
        null = True,
    )
    parent_slidegroup = models.ForeignKey("self",null=True,on_delete=models.SET_NULL)
    name = models.CharField(max_length = 100)
    created_date = models.DateTimeField(default = timezone.now)
#    unit_objects = GenericRelation(UnitObject)#??????
    num_slides = models.IntegerField(default = 0)
    is_published = models.BooleanField(default = 0)
    def __str__(self):
        return self.name
    def publish(self,published_unit_object):
        new_slide_group = SlideGroup(name = self.name,num_slides = self.slides.count(),unit_object = published_unit_object,parent_slidegroup = self, is_published = 1)
        new_slide_group.save()
        for s in self.slides.all():
            s.publish(new_slide_group)

class Slide(models.Model):#(i.e., slide 1...etc)
    title = models.CharField(max_length = 100)
    order = models.IntegerField(default = 0)
    parent_slide = models.ForeignKey("self",null=True,on_delete=models.SET_NULL)
    slidegroup = models.ForeignKey(SlideGroup,related_name='slides')
    top_order_number = models.IntegerField(default = 0)
    is_published = models.BooleanField(default = 0)
    class Meta:
        ordering = ['order']
    def __str__(self):
        return self.title
    def publish(self,published_slidegroup):
        new_slide = Slide(title = self.title, order = self.order,  parent_slide = self, slidegroup = published_slidegroup,top_order_number = self.top_order_number, is_published=1)
        new_slide.save()
        for so in self.slide_objects.all():
            so.publish(new_slide)

class SlideObject(models.Model):#placeholder for components
    order = models.IntegerField(default = 0)
    parent_slideobject = models.ForeignKey("self",null=True,on_delete=models.SET_NULL)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    slide = models.ForeignKey(Slide,related_name='slide_objects')
    is_published = models.BooleanField(default = 0)
    class Meta:
        ordering = ['order']
    def publish(self,published_slide):
        published_object = self.content_object.publish()
        new_so = SlideObject(content_object= published_object, slide = published_slide, order = self.order, parent_slideobject = self, is_published = 1)
        new_so.save()

#theorem, problem, image, textblock,proof,solution (are these dependent?)

class TextBlock(models.Model):
    parent_textblock = models.ForeignKey("self",null=True,on_delete=models.SET_NULL)
    text_code = models.TextField(blank=True)
    text_display = models.TextField(blank=True)
    is_published = models.BooleanField(default = 0)
    def publish(self):
        new_textblock = TextBlock(text_code = self.text_code,text_display="",parent_textblock = self, is_published = 1)
        new_textblock.save()
        new_textblock.text_display = newtexcode(new_textblock.text_code, 'textblock_'+str(new_textblock.pk), "")
        new_textblock.save()
        compileasy(new_textblock.text_code,'textblock_'+str(new_textblock.pk))
        return new_textblock

class Proof(models.Model):
    parent_proof = models.ForeignKey("self",null=True,on_delete=models.SET_NULL)
    prefix = models.CharField(max_length=20)#Proof, Solution
    proof_code = models.TextField(blank=True)
    proof_display = models.TextField(blank=True)
    isSolution = models.BooleanField(default=0)
    solution = models.ForeignKey(Solution,blank=True,null=True)
    is_published = models.BooleanField(default = 0)
    def publish(self):
        new_proof = Proof(prefix=self.prefix,proof_code = self.proof_code,proof_display="",parent_proof=self, is_published = 1)
        new_proof.save()
        new_proof.proof_display = newtexcode(new_proof.proof_code, 'proofblock_'+str(new_proof.pk), "")
        new_proof.save()
        compileasy(new_proof.proof_code,'proofblock_'+str(new_proof.pk))
        return new_proof

class Theorem(models.Model):
    parent_theorem = models.ForeignKey("self",null=True,on_delete=models.SET_NULL)
    name=models.CharField(max_length=150, default="")
    prefix = models.CharField(max_length=20)#Theorem, Proposition, Lemma, Corollary
    theorem_code = models.TextField(blank=True)
    theorem_display = models.TextField(blank=True)
    is_published = models.BooleanField(default = 0)
    def __str__(self):
        return self.name
    def publish(self):
        new_theorem = Theorem(name=self.name,prefix=self.prefix,theorem_code = self.theorem_code,theorem_display="",parent_theorem = self, is_published = 1)
        new_theorem.save()
        new_theorem.theorem_display = newtexcode(new_theorem.theorem_code, 'theoremblock_'+str(new_theorem.pk), "")
        new_theorem.save()
        compileasy(new_theorem.theorem_code,'theoremblock_'+str(new_theorem.pk))
        return new_theorem

class ExampleProblem(models.Model):
    parent_exampleproblem = models.ForeignKey("self",null=True,on_delete=models.SET_NULL)
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
    is_published = models.BooleanField(default = 0)
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
    def publish(self):
        new_example = ExampleProblem(name=self.name,prefix=self.prefix,problem_code = self.problem_code,problem_display="",isProblem=self.isProblem, problem=self.problem,question_type=self.question_type,mc_answer = self.mc_answer,sa_answer = self.sa_answer,answer_A = self.answer_A,answer_B = self.answer_B,answer_C = self.answer_C,answer_D = self.answer_D,answer_E = self.answer_E,author=self.author,parent_exampleproblem = self, is_published = 1)
        new_example.save()
        new_example.problem_display = newtexcode(new_example.problem_code, 'exampleproblem_'+str(new_example.pk), "")
        new_example.save()
        compileasy(new_example.problem_code,'exampleproblem_'+str(new_example.pk))
        return new_example

class ImageModel(models.Model):
    parent_image = models.ForeignKey("self",null=True,on_delete=models.SET_NULL)
    image = models.ImageField(upload_to='images')
    is_published = models.BooleanField(default = 0)
    def publish(self):
        new_image = ImageModel(image = self.image,parent_image = self, is_published = 1)
        new_image.save()
        return new_image

class ProblemSet(models.Model):#like NewTest
    parent_problemset = models.ForeignKey("self",null=True,on_delete=models.SET_NULL)
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
    is_published = models.BooleanField(default = 0)
    def __str__(self):
        return self.name
    def publish(self,published_unit_object):
        new_problemset = ProblemSet(name = self.name,default_point_value = self.default_point_value,unit_object = published_unit_object, parent_problemset = self, is_published = 1)
        new_problemset.save()
        total_points=0
        for po in self.problem_objects.all():
            new_po = po.publish(new_problemset)
            new_problemset.problem_objects.add(new_po)
            total_points += po.point_value
        new_problemset.total_points = total_points
        new_problemset.num_problems = new_problemset.problem_objects.count()
        new_problemset.save()
            

class ProblemObject(models.Model):
    parent_problemobject = models.ForeignKey("self",null=True,on_delete=models.SET_NULL)
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
    is_published = models.BooleanField(default = 0)
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
    def publish(self,published_pset):
        new_po = ProblemObject(order = self.order,point_value=self.point_value,problem_code = self.problem_code,problem_display="",isProblem=self.isProblem, problem=self.problem,question_type=self.question_type,mc_answer = self.mc_answer,sa_answer = self.sa_answer,answer_A = self.answer_A,answer_B = self.answer_B,answer_C = self.answer_C,answer_D = self.answer_D,answer_E = self.answer_E,author=self.author,parent_problemobject = self, is_published = 1)
        new_po.save()
        if new_po.isProblem == 0:
            if new_po.question_type.question_type =='multiple choice':
                new_po.problem_display = newtexcode(po.problem_code, 'originalproblem_'+str(new_po.pk), new_po.answers())
            else:
                new_po.problem_display = newtexcode(po.problem_code, 'originalproblem_'+str(new_po.pk), "")
            new_po.save()
            compileasy(new_po.problem_code,'originalproblem_'+str(new_po.pk))
        return new_po
#perhaps newresponse should have a generic reference....
#units....manytomany or foreign key?
#standalone units? or just allow copying from another Class?
#standalone slides?
