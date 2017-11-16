from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType

from randomtest.models import Problem,Solution,QuestionType
from randomtest.utils import newtexcode, compileasy
from student.models import UserClass,UserUnit,UserUnitObject,UserProblemSet,UserSlides,UserTest
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
    pub_units = models.ManyToManyField('PublishedUnit',blank=True)
    total_points = models.IntegerField(default = 0)
    num_problems = models.IntegerField(default = 0)
    def __str__(self):
        return self.name
    def sync_to_parent(self):
        self.name = self.parent_class.name
        self.save()
        parent_units_pk=[]
        for u in self.pub_units.all():
            if u.parent_unit not in self.parent_class.units.all():
                u.delete()
            else:
                u.sync_to_parent()
                parent_units_pk.append(u.parent_unit.pk)
        for u in self.parent_class.units.exclude(pk__in=parent_units_pk):
            new_unit = u.publish(self)
#        self.update_stats()
    def update_stats(self):
        total_points = 0
        num_problems = 0
        for u in self.units.all():
            u.update_stats()
            total_points +=u.total_points
            num_problems +=u.num_problems
        self.total_points = total_points
        self.num_problems = num_problems
        self.save()
    def add_student(self,student):
        self.enrolled_students.add(student)
        self.save()
        new_user_class = UserClass(published_class = self,userprofile=student.userprofile,total_points=self.total_points,points_earned=0,num_problems = self.num_problems)
        new_user_class.save()
        for unit in self.pub_units.all():
            unit.add_student(student,new_user_class)
        return new_user_class

class Unit(models.Model):#with order
    name = models.CharField(max_length = 100)
    order = models.IntegerField(default = 0)
    total_points = models.IntegerField(default=0)
    num_problems = models.IntegerField(default=0)
    num_problemsets = models.IntegerField(default=0)
    class Meta:
        ordering = ['order']
    def publish(self,published_class):
        new_unit = PublishedUnit(name=self.name,order=self.order,parent_unit = self)
        new_unit.save()
        published_class.pub_units.add(new_unit)
        published_class.save()
        unit_points = 0
        unit_num_problems = 0
        num_problemsets = 0
        for uo in self.unit_objects.all():
            try:
                sg = uo.slidegroup
                new_uo = uo.publish(new_unit)
            except SlideGroup.DoesNotExist:
                try:
                    pset = uo.problemset
                    new_uo = uo.publish(new_unit)
                    num_problemsets += 1
                    unit_num_problems += new_uo.publishedproblemset.num_problems
                    unit_points += new_uo.publishedproblemset.total_points
                except ProblemSet.DoesNotExist:
                    test = uo.test
                    new_uo = uo.publish(new_unit)
        new_unit.total_points = unit_points
        new_unit.num_problems = unit_num_problems
        new_unit.num_problemsets = num_problemsets
        new_unit.save()
        return new_unit
    def update_stats(self):
        total_points = 0
        num_problems = 0
        num_problemsets = 0
        for uo in self.unit_objects.all():
            try:
                pset = uo.problemset
                pset.update_stats()
                num_problemsets +=1
                num_problems +=pset.num_problems
                total_points +=pset.total_points
            except:
                a=0
        self.total_points = total_points
        self.num_problems = num_problems
        self.num_problemsets = num_problemsets
        self.save()

class PublishedUnit(models.Model):
    parent_unit = models.ForeignKey(Unit,null=True,on_delete=models.SET_NULL)
    name = models.CharField(max_length = 100)
    order = models.IntegerField(default = 0)
    total_points = models.IntegerField(default=0)
    num_problems = models.IntegerField(default=0)
    num_problemsets = models.IntegerField(default=0)
    def sync_to_parent(self):
        self.name = self.parent_unit.name
        self.order = self.parent_unit.order
        self.save()
        parent_uos_pk=[]
        for uo in self.unit_objects.all():
            if uo.parent_unitobject not in self.parent_unit.unit_objects.all():
                uo.delete()
            else:
                uo.sync_to_parent()
                parent_uos_pk.append(uo.parent_unitobject.pk)
        for uo in self.parent_unit.unit_objects.exclude(pk__in=parent_uos_pk):
            new_uo = uo.publish(self)
    def add_student(self,student,user_class):
        new_user_unit = UserUnit(published_unit = self,user_class = user_class,total_points=self.total_points, points_earned=0,order = self.order,num_problems = self.num_problems)
        new_user_unit.save()
        num_psets = 0
        for unit_object in self.unit_objects.all():
            new_user_unitobject = UserUnitObject(order = unit_object.order, user_unit = new_user_unit)
            new_user_unitobject.save()
            try:
                slidegroup = unit_object.publishedslidegroup
                user_slides = UserSlides(published_slides = slidegroup,order=unit_object.order,userunitobject = user_unitobject,num_slides = slidegroup.slides.count())
                user_slides.save()
            except PublishedSlideGroup.DoesNotExist:
                try:
                    pset = unit_object.publishedproblemset
                    user_problemset = UserProblemSet(published_problemset = pset, total_points = pset.total_points,points_earned = 0,order = unit_object.order,num_problems = pset.num_problems,userunitobject = new_user_unitobject)
                    user_problemset.save()
                    num_psets +=1
                except PublishedProblemSet.DoesNotExist:
                    test = unit_object.publishedtest
                    user_test = UserTest(published_test = test, total_points = test.total_points, points_earned = 0, order = unit_object.order,num_problems = test.num_problems,userunitobject = new_user_unitobject)
                    user_test.save()
        new_user_unit.num_problemsets = num_psets
        new_user_unit.save()

class UnitObject(models.Model):
    order = models.IntegerField(default = 0)
    unit = models.ForeignKey(Unit,related_name='unit_objects')
    class Meta:
        ordering = ['order']
    def publish(self,published_unit):
        new_unit_object = PublishedUnitObject(unit = published_unit,order = self.order,parent_unitobject = self)
        new_unit_object.save()
        try:
            sg = self.slidegroup
            sg.publish(new_unit_object)
        except SlideGroup.DoesNotExist:
            try:
                pset = self.problemset
                pset.publish(new_unit_object)
            except ProblemSet.DoesNotExist:
                test = self.test
                test.publish(new_unit_object)
        return new_unit_object
    def sync_to_parent(self):
        self.order = self.parent_unitobject.order
        self.save()
        try:
            sg = self.slidegroup
            sg.sync_to_parent()
        except:
            try:
                pset = self.problemset
                pset.sync_to_parent()
            except:
                a=0


class PublishedUnitObject(models.Model):
    parent_unitobject = models.ForeignKey(UnitObject,null=True,on_delete=models.SET_NULL)
    order = models.IntegerField(default = 0)
    unit = models.ForeignKey(PublishedUnit,related_name='unit_objects')
    class Meta:
        ordering = ['order']
    def sync_to_parent(self):
        self.order = self.parent_unitobject.order
        self.save()
        try:
            sg = self.publishedslidegroup
            sg.sync_to_parent()
        except SlideGroup.DoesNotExist:
            try:
                pset = self.publishedproblemset
                pset.sync_to_parent()
            except ProblemSet.DoesNotExist:
                a=0


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
    def publish(self,published_unit_object):
        new_slide_group = PublishedSlideGroup(name = self.name,num_slides = self.slides.count(),unit_object = published_unit_object,parent_slidegroup = self)
        new_slide_group.save()
        for s in self.slides.all():
            s.publish(new_slide_group)
    def sync_to_parent(self):
        self.name = self.parent_slidegroup.name
        self.save()
        parent_slide_pks=[]
        for s in self.slides.all():
            if s.parent_slide not in self.parent_slidegroup.slides.all():
                s.delete()
            else:
                s.sync_to_parent()
                parent_slide_pks.append(s.parent_slide.pk)
        for s in self.parent_slidegroup.slides.exclude(pk__in=parent_slide_pks):
            s.publish(self)

class PublishedSlideGroup(models.Model):#like Handout, but more punctuated; problems can be included, but only short answer and multiple choice will be checked
    unit_object = models.OneToOneField(
        PublishedUnitObject,
        on_delete=models.CASCADE,
        null = True,
    )
    parent_slidegroup = models.ForeignKey(SlideGroup,null=True,on_delete=models.SET_NULL)
    name = models.CharField(max_length = 100)
    created_date = models.DateTimeField(default = timezone.now)
#    unit_objects = GenericRelation(UnitObject)#??????
    num_slides = models.IntegerField(default = 0)
    def __str__(self):
        return self.name
    def sync_to_parent(self):
        self.name = self.parent_slidegroup.name
        self.save()
        parent_slide_pks=[]
        for s in self.slides.all():
            if s.parent_slide not in self.parent_slidegroup.slides.all():
                s.delete()
            else:
                s.sync_to_parent()
                parent_slide_pks.append(s.parent_slide.pk)
        for s in self.parent_slidegroup.slides.exclude(pk__in=parent_slide_pks):
            s.publish(self)

class Slide(models.Model):#(i.e., slide 1...etc)
    title = models.CharField(max_length = 100)
    order = models.IntegerField(default = 0)
    slidegroup = models.ForeignKey(SlideGroup,related_name='slides')
    top_order_number = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']
    def __str__(self):
        return self.title
    def publish(self,published_slidegroup):
        new_slide = PublishedSlide(title = self.title, order = self.order,  parent_slide = self, slidegroup = published_slidegroup,top_order_number = self.top_order_number)
        new_slide.save()
        for so in self.slide_objects.all():
            so.publish(new_slide)
    def sync_to_parent(self):
        self.title = self.parent_slide.title
        self.order = self.parent_slide.order
        self.top_order_number = self.parent_slide.top_order_number
        self.save()
        parent_slideobject_pks = []
        for so in self.slide_objects.all():
            if so.parent_slideobject not in self.parent_slide.slide_objects.all():
                so.delete()
            else:
                so.sync_to_parent()
                parent_slideobject_pks.append(so.parent_slideobject.pk)
        for so in self.parent_slide.slide_objects.exclude(pk__in=parent_slideobject_pks):
            so.publish(self)

class PublishedSlide(models.Model):#(i.e., slide 1...etc)
    title = models.CharField(max_length = 100)
    order = models.IntegerField(default = 0)
    parent_slide = models.ForeignKey(Slide,null=True,on_delete=models.SET_NULL)
    slidegroup = models.ForeignKey(PublishedSlideGroup,related_name='slides')
    top_order_number = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']
    def __str__(self):
        return self.title
    def sync_to_parent(self):
        self.title = self.parent_slide.title
        self.order = self.parent_slide.order
        self.top_order_number = self.parent_slide.top_order_number
        self.save()
        parent_slideobject_pks = []
        for so in self.slide_objects.all():
            if so.parent_slideobject not in self.parent_slide.slide_objects.all():
                so.delete()
            else:
                so.sync_to_parent()
                parent_slideobject_pks.append(so.parent_slideobject.pk)
        for so in self.parent_slide.slide_objects.exclude(pk__in=parent_slideobject_pks):
            so.publish(self)


class SlideObject(models.Model):#placeholder for components
    order = models.IntegerField(default = 0)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    slide = models.ForeignKey(Slide,related_name='slide_objects')
    class Meta:
        ordering = ['order']
    def publish(self,published_slide):
        published_object = self.content_object.publish()
        new_so = PublishedSlideObject(content_object= published_object, slide = published_slide, order = self.order, parent_slideobject = self)
        new_so.save()
    def sync_to_parent(self):
        self.order = self.parent_slideobject.order
        self.save()
        if self.content_type == ContentType.objects.get(app_label = 'teacher', model = 'textblock'):
            if self.content_object.parent_textblock is None:
                self.content_object.delete()
            else:
                self.content_object.sync_to_parent()
        if self.content_type == ContentType.objects.get(app_label = 'teacher', model = 'proof'):
            if self.content_object.parent_proof is None:
                self.content_object.delete()
            else:
                self.content_object.sync_to_parent()
        if self.content_type == ContentType.objects.get(app_label = 'teacher', model = 'theorem'):
            if self.content_object.parent_theorem is None:
                self.content_object.delete()
            else:
                self.content_object.sync_to_parent()
        if self.content_type == ContentType.objects.get(app_label = 'teacher', model = 'exampleproblem'):
            if self.content_object.parent_exampleproblem is None:
                self.content_object.delete()
            else:
                self.content_object.sync_to_parent()
        if self.content_type == ContentType.objects.get(app_label = 'teacher', model = 'imagemodel'):
            if self.content_object.parent_image is None:
                self.content_object.delete()
            else:
                self.content_object.sync_to_parent()

class PublishedSlideObject(models.Model):#placeholder for components
    order = models.IntegerField(default = 0)
    parent_slideobject = models.ForeignKey(SlideObject,null=True,on_delete=models.SET_NULL)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    slide = models.ForeignKey(PublishedSlide,related_name='slide_objects')
    class Meta:
        ordering = ['order']
    def sync_to_parent(self):
        self.order = self.parent_slideobject.order
        self.save()
        if self.content_type == ContentType.objects.get(app_label = 'teacher', model = 'publishedtextblock'):
            if self.content_object.parent_textblock is None:
                self.content_object.delete()
            else:
                self.content_object.sync_to_parent()
        if self.content_type == ContentType.objects.get(app_label = 'teacher', model = 'publishedproof'):
            if self.content_object.parent_proof is None:
                self.content_object.delete()
            else:
                self.content_object.sync_to_parent()
        if self.content_type == ContentType.objects.get(app_label = 'teacher', model = 'publishedtheorem'):
            if self.content_object.parent_theorem is None:
                self.content_object.delete()
            else:
                self.content_object.sync_to_parent()
        if self.content_type == ContentType.objects.get(app_label = 'teacher', model = 'publishedexampleproblem'):
            if self.content_object.parent_exampleproblem is None:
                self.content_object.delete()
            else:
                self.content_object.sync_to_parent()
        if self.content_type == ContentType.objects.get(app_label = 'teacher', model = 'publishedimagemodel'):
            if self.content_object.parent_image is None:
                self.content_object.delete()
            else:
                self.content_object.sync_to_parent()


#theorem, problem, image, textblock,proof,solution (are these dependent?)

class TextBlock(models.Model):
    text_code = models.TextField(blank=True)
    text_display = models.TextField(blank=True)
    def publish(self):
        new_textblock = PublishedTextBlock(text_code = self.text_code,text_display="",parent_textblock = self)
        new_textblock.save()
        new_textblock.text_display = newtexcode(new_textblock.text_code, 'publishedtextblock_'+str(new_textblock.pk), "")
        new_textblock.save()
        compileasy(new_textblock.text_code,'publishedtextblock_'+str(new_textblock.pk))
        return new_textblock
    def sync_to_parent(self):
        self.text_code = self.parent_textblock.text_code
        self.save()
        self.text_display = newtexcode(self.text_code, 'textblock_'+str(self.pk), "")
        self.save()
        compileasy(self.text_code,'textblock_'+str(self.pk))

class PublishedTextBlock(models.Model):
    parent_textblock = models.ForeignKey(TextBlock,null=True,on_delete=models.SET_NULL)
    text_code = models.TextField(blank=True)
    text_display = models.TextField(blank=True)
    def sync_to_parent(self):
        self.text_code = self.parent_textblock.text_code
        self.save()
        self.text_display = newtexcode(self.text_code, 'publishedtextblock_'+str(self.pk), "")
        self.save()
        compileasy(self.text_code,'publishedtextblock_'+str(self.pk))

class Proof(models.Model):
    prefix = models.CharField(max_length=20)#Proof, Solution
    proof_code = models.TextField(blank=True)
    proof_display = models.TextField(blank=True)
    isSolution = models.BooleanField(default=0)
    solution = models.ForeignKey(Solution,blank=True,null=True)
    def publish(self):
        new_proof = PublishedProof(prefix=self.prefix,proof_code = self.proof_code,proof_display="",parent_proof=self)
        new_proof.save()
        new_proof.proof_display = newtexcode(new_proof.proof_code, 'publishedproofblock_'+str(new_proof.pk), "")
        new_proof.save()
        compileasy(new_proof.proof_code,'publishedproofblock_'+str(new_proof.pk))
        return new_proof
    def sync_to_parent(self):
        self.proof_code = self.parent_proof.proof_code
        self.prefix = self.parent_proof.prefix
        self.save()
        self.proof_display = newtexcode(self.proof_code, 'proofblock_'+str(self.pk), "")
        self.save()
        compileasy(self.proof_code,'proofblock_'+str(self.pk))

class PublishedProof(models.Model):
    parent_proof = models.ForeignKey(Proof,null=True,on_delete=models.SET_NULL)
    prefix = models.CharField(max_length=20)#Proof, Solution
    proof_code = models.TextField(blank=True)
    proof_display = models.TextField(blank=True)
    isSolution = models.BooleanField(default=0)
    solution = models.ForeignKey(Solution,blank=True,null=True)
    def sync_to_parent(self):
        self.proof_code = self.parent_proof.proof_code
        self.prefix = self.parent_proof.prefix
        self.save()
        self.proof_display = newtexcode(self.proof_code, 'publishedproofblock_'+str(self.pk), "")
        self.save()
        compileasy(self.proof_code,'publishedproofblock_'+str(self.pk))

class Theorem(models.Model):
    name=models.CharField(max_length=150, default="")
    prefix = models.CharField(max_length=20)#Theorem, Proposition, Lemma, Corollary
    theorem_code = models.TextField(blank=True)
    theorem_display = models.TextField(blank=True)
    def __str__(self):
        return self.name
    def publish(self):
        new_theorem = PublishedTheorem(name=self.name,prefix=self.prefix,theorem_code = self.theorem_code,theorem_display="",parent_theorem = self)
        new_theorem.save()
        new_theorem.theorem_display = newtexcode(new_theorem.theorem_code, 'publishedtheoremblock_'+str(new_theorem.pk), "")
        new_theorem.save()
        compileasy(new_theorem.theorem_code,'publishedtheoremblock_'+str(new_theorem.pk))
        return new_theorem
    def sync_to_parent(self):
        self.theorem_code = self.parent_theorem.theorem_code
        self.name = self.parent_theorem.name
        self.prefix = self.parent_theorem.prefix
        self.save()
        self.theorem_display = newtexcode(self.theorem_code, 'theoremblock_'+str(self.pk), "")
        self.save()
        compileasy(self.theorem_code,'theoremblock_'+str(self.pk))


class PublishedTheorem(models.Model):
    parent_theorem = models.ForeignKey(Theorem,null=True,on_delete=models.SET_NULL)
    name=models.CharField(max_length=150, default="")
    prefix = models.CharField(max_length=20)#Theorem, Proposition, Lemma, Corollary
    theorem_code = models.TextField(blank=True)
    theorem_display = models.TextField(blank=True)
    def __str__(self):
        return self.name
    def sync_to_parent(self):
        self.theorem_code = self.parent_theorem.theorem_code
        self.name = self.parent_theorem.name
        self.prefix = self.parent_theorem.prefix
        self.save()
        self.theorem_display = newtexcode(self.theorem_code, 'publishedtheoremblock_'+str(self.pk), "")
        self.save()
        compileasy(self.theorem_code,'publishedtheoremblock_'+str(self.pk))

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
    def publish(self):
        new_example = PublishedExampleProblem(name=self.name,prefix=self.prefix,problem_code = self.problem_code,problem_display="",isProblem=self.isProblem, problem=self.problem,question_type=self.question_type,mc_answer = self.mc_answer,sa_answer = self.sa_answer,answer_A = self.answer_A,answer_B = self.answer_B,answer_C = self.answer_C,answer_D = self.answer_D,answer_E = self.answer_E,author=self.author,parent_exampleproblem = self)
        new_example.save()
        new_example.problem_display = newtexcode(new_example.problem_code, 'publishedexampleproblem_'+str(new_example.pk), "")
        new_example.save()
        compileasy(new_example.problem_code,'publishedexampleproblem_'+str(new_example.pk))
        return new_example
    def sync_to_parent(self):
        self.name = self.parent_exampleproblem.name
        self.prefix = self.parent_exampleproblem.prefix
        self.problem_code = self.parent_exampleproblem.problem_code
        self.isProblem = self.parent_exampleproblem.isProblem
        self.problem = self.parent_exampleproblem.problem
        self.question_type = self.parent_exampleproblem.question_type
        self.mc_answer = self.parent_exampleproblem.mc_answer
        self.sa_answer = self.parent_exampleproblem.sa_answer
        self.answer_A = self.parent_exampleproblem.answer_A
        self.answer_B = self.parent_exampleproblem.answer_B
        self.answer_C = self.parent_exampleproblem.answer_C
        self.answer_D = self.parent_exampleproblem.answer_D
        self.answer_E = self.parent_exampleproblem.answer_E
        self.author = self.parent_exampleproblem.author
        self.save()
        self.problem_display = newtexcode(self.problem_code, 'exampleproblem_'+str(self.pk), "")
        self.save()
        compileasy(self.problem_code,'exampleproblem_'+str(self.pk))


class PublishedExampleProblem(models.Model):
    parent_exampleproblem = models.ForeignKey(ExampleProblem,null=True,on_delete=models.SET_NULL)
    name = models.CharField(max_length=150, default="")
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
    author = models.ForeignKey(User,related_name='published_example_problem',blank=True,null=True)
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
    def sync_to_parent(self):
        self.name = self.parent_exampleproblem.name
        self.prefix = self.parent_exampleproblem.prefix
        self.problem_code = self.parent_exampleproblem.problem_code
        self.isProblem = self.parent_exampleproblem.isProblem
        self.problem = self.parent_exampleproblem.problem
        self.question_type = self.parent_exampleproblem.question_type
        self.mc_answer = self.parent_exampleproblem.mc_answer
        self.sa_answer = self.parent_exampleproblem.sa_answer
        self.answer_A = self.parent_exampleproblem.answer_A
        self.answer_B = self.parent_exampleproblem.answer_B
        self.answer_C = self.parent_exampleproblem.answer_C
        self.answer_D = self.parent_exampleproblem.answer_D
        self.answer_E = self.parent_exampleproblem.answer_E
        self.author = self.parent_exampleproblem.author
        self.save()
        self.problem_display = newtexcode(self.problem_code, 'publishedexampleproblem_'+str(self.pk), "")
        self.save()
        compileasy(self.problem_code,'publishedexampleproblem_'+str(self.pk))

class ImageModel(models.Model):
    image = models.ImageField(upload_to='images')
    def publish(self):
        new_image = PublishedImageModel(image = self.image,parent_image = self)
        new_image.save()
        return new_image
    def sync_to_parent(self):
        self.image = self.parent_image.image
        self.save()

class PublishedImageModel(models.Model):
    parent_image = models.ForeignKey(ImageModel,null=True,on_delete=models.SET_NULL)
    image = models.ImageField(upload_to='images')
    def sync_to_parent(self):
        self.image = self.parent_image.image
        self.save()

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
    total_points = models.IntegerField(default=0)
    num_problems = models.IntegerField(default=0)
    due_date = models.DateTimeField(null = True)
    def __str__(self):
        return self.name
    def publish(self,published_unit_object):
        new_problemset = PublishedProblemSet(name = self.name,default_point_value = self.default_point_value,unit_object = published_unit_object, parent_problemset = self, due_date = self.due_date)
        new_problemset.save()
        total_points=0
        for po in self.problem_objects.all():
            new_po = po.publish(new_problemset)
            new_problemset.problem_objects.add(new_po)
            total_points += po.point_value
        new_problemset.total_points = total_points
        new_problemset.num_problems = new_problemset.problem_objects.count()
        new_problemset.save()
    def sync_to_parent(self):
        self.name = self.parent_problemset.name
        self.default_point_value = self.parent_problemset.default_point_value
        self.save()
        parent_po_pks=[]
        for po in self.problem_objects.all():
            if po.parent_problemobject not in self.parent_problemset.problem_objects().all():
                po.response_set.delete()
                po.delete()
            else:
                po.sync_to_parent(self)
                parent_po_pks.append(po.parent_problem_object.pk)
        for po in self.parent_problemset.problem_objects.exclude(pk__in=parent_po_pks):
            new_po=po.publish(self)
            for ups in self.userproblemset_set.all():
                r=Response(problem_object = new_po,user_problemset = ups,order = new_po.order,point_value = new_po.point_value)
                r.save()

class PublishedProblemSet(models.Model):#like NewTest
    parent_problemset = models.ForeignKey(ProblemSet,null=True,on_delete=models.SET_NULL)
    unit_object = models.OneToOneField(
        PublishedUnitObject,
        on_delete=models.CASCADE,
        null = True,
    )
    name = models.CharField(max_length = 100)
    created_date = models.DateTimeField(default = timezone.now)
    problem_objects = models.ManyToManyField('PublishedProblemObject',blank=True)
    default_point_value = models.IntegerField(default = 1)
#    unit_objects = GenericRelation(UnitObject)#??????
    total_points = models.IntegerField(default=0)
    num_problems = models.IntegerField(default=0)
    due_date = models.DateTimeField(null = True)
    def __str__(self):
        return self.name
    def sync_to_parent(self):
        self.name = self.parent_problemset.name
        self.default_point_value = self.parent_problemset.default_point_value
        self.save()
        parent_po_pks=[]
        for po in self.problem_objects.all():
            if po.parent_problemobject not in self.parent_problemset.problem_objects().all():
                po.response_set.delete()
                po.delete()
            else:
                po.sync_to_parent(self)
                parent_po_pks.append(po.parent_problem_object.pk)
        for po in self.parent_problemset.problem_objects.exclude(pk__in=parent_po_pks):
            new_po=po.publish(self)
            for ups in self.userproblemset_set.all():
                r=Response(problem_object = new_po,user_problemset = ups,order = new_po.order,point_value = new_po.point_value)
                r.save()

class Test(models.Model):#like NewTest
    unit_object = models.OneToOneField(
        UnitObject,
        on_delete=models.CASCADE,
        null = True,
    )
    name = models.CharField(max_length = 100)
    created_date = models.DateTimeField(default = timezone.now)
    default_point_value = models.IntegerField(default = 1)
    default_blank_value = models.FloatField(default = 0)
    total_points = models.IntegerField(default=0)
    num_problems = models.IntegerField(default=0)
    start_date = models.DateTimeField(null = True)
    due_date = models.DateTimeField(null = True)
    time_limit = models.TimeField(null = True)
    def __str__(self):
        return self.name
    def publish(self,published_unit_object):
        new_test = PublishedTest(name = self.name,default_point_value = self.default_point_value,default_blank_value = self.default_blank_value,unit_object = published_unit_object, parent_test = self, due_date = self.due_date,time_limit = self.time_limit, start_date = self.start_date)
        new_test.save()
        total_points=0
        for po in self.test_problem_objects.all():
            new_po = po.publish(new_test)
            new_test.test_problem_objects.add(new_po)
            total_points += po.point_value
        new_test.total_points = total_points
        new_test.num_problems = new_test.test_problem_objects.count()
        new_test.save()

class PublishedTest(models.Model):#like NewTest
    parent_test = models.ForeignKey(Test,null=True,on_delete=models.SET_NULL)
    unit_object = models.OneToOneField(
        PublishedUnitObject,
        on_delete=models.CASCADE,
        null = True,
    )
    name = models.CharField(max_length = 100)
    created_date = models.DateTimeField(default = timezone.now)
#    test_problem_objects = models.ManyToManyField('PublishedProblemObject',blank=True)
    default_point_value = models.IntegerField(default = 1)
    default_blank_value = models.FloatField(default = 0)
    total_points = models.IntegerField(default=0)
    num_problems = models.IntegerField(default=0)
    due_date = models.DateTimeField(null = True)
    start_date = models.DateTimeField(null = True)
    time_limit = models.TimeField(null = True)
    def __str__(self):
        return self.name
    def sync_to_parent(self):
        self.name = self.parent_test.name
        self.default_point_value = self.parent_test.default_point_value
        self.default_blank_value = self.parent_test.default_blank_value
        self.due_date = self.parent_test.due_date
        self.start_date = self.parent_test.start_date
        self.save()
        parent_po_pks=[]
        for po in self.test_problem_objects.all():
            if po.parent_testproblemobject not in self.parent_test.test_problem_objects().all():
                po.testresponse_set.delete()
                po.delete()
            else:
                po.sync_to_parent(self)
                parent_po_pks.append(po.parent_test_problem_object.pk)
        for po in self.parent_test.test_problem_objects.exclude(pk__in=parent_po_pks):
            new_po=po.publish(self)
            for ut in self.usertest_set.all():
                r=TestResponse(test_problem_object = new_po,user_test = ut,order = new_po.order,point_value = new_po.point_value)
                r.save()

class ProblemObject(models.Model):
    a_problemset = models.ForeignKey(ProblemSet,null = True)
    test = models.ForeignKey(Test,null = True)
    order = models.IntegerField(default = 0)
    point_value = models.IntegerField(default = 1)
    blank_point_value = models.FloatField(default = 0)
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
    def publish(self,published_pset):
        new_po = PublishedProblemObject(order = self.order,point_value=self.point_value,problem_code = self.problem_code,problem_display="",isProblem=self.isProblem, problem=self.problem,question_type=self.question_type,mc_answer = self.mc_answer,sa_answer = self.sa_answer,answer_A = self.answer_A,answer_B = self.answer_B,answer_C = self.answer_C,answer_D = self.answer_D,answer_E = self.answer_E,author=self.author,parent_problemobject = self)
        new_po.save()
        if new_po.isProblem == 0:
            if new_po.question_type.question_type =='multiple choice':
                new_po.problem_display = newtexcode(new_po.problem_code, 'publishedoriginalproblem_'+str(new_po.pk), new_po.answers())
            else:
                new_po.problem_display = newtexcode(new_po.problem_code, 'publishedoriginalproblem_'+str(new_po.pk), "")
            new_po.save()
            compileasy(new_po.problem_code,'publishedoriginalproblem_'+str(new_po.pk))
        return new_po
    def sync_to_parent(self):
        self.order = self.parent_problemobject.order
        self.point_value = self.parent_problemobject.point_value
        self.problem_code = self.parent_problemobject.problem_code
        self.isProblem = self.parent_problemobject.isProblem
        self.problem = self.parent_problemobject.problem
        self.question_type = self.parent_problemobject.question_type
        self.mc_answer = self.parent_problemobject.mc_answer
        self.sa_answer = self.parent_problemobject.sa_answer
        self.answer_A = self.parent_problemobject.answer_A
        self.answer_B = self.parent_problemobject.answer_B
        self.answer_C = self.parent_problemobject.answer_C
        self.answer_D = self.parent_problemobject.answer_D
        self.answer_E = self.parent_problemobject.answer_E
        self.author = self.parent_problemobject.author
        self.save()
        self.problem_display = newtexcode(self.problem_code, 'originalproblem_'+str(self.pk), "")
        self.save()
        compileasy(self.problem_code,'originalproblem_'+str(self.pk))


class PublishedProblemObject(models.Model):
    problemset = models.ForeignKey(PublishedProblemSet,null=True)
    test = models.ForeignKey(PublishedTest,null=True)
    parent_problemobject = models.ForeignKey(ProblemObject,null=True,on_delete=models.SET_NULL)
    order = models.IntegerField(default = 0)
    point_value = models.IntegerField(default = 1)
    blank_point_value = models.FloatField(default = 0)
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
    author = models.ForeignKey(User,related_name='published_problem_object',blank=True,null=True)
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
    def sync_to_parent(self):
        self.order = self.parent_problemobject.order
        self.point_value = self.parent_problemobject.point_value
        self.problem_code = self.parent_problemobject.problem_code
        self.isProblem = self.parent_problemobject.isProblem
        self.problem = self.parent_problemobject.problem
        self.question_type = self.parent_problemobject.question_type
        self.mc_answer = self.parent_problemobject.mc_answer
        self.sa_answer = self.parent_problemobject.sa_answer
        self.answer_A = self.parent_problemobject.answer_A
        self.answer_B = self.parent_problemobject.answer_B
        self.answer_C = self.parent_problemobject.answer_C
        self.answer_D = self.parent_problemobject.answer_D
        self.answer_E = self.parent_problemobject.answer_E
        self.author = self.parent_problemobject.author
        self.save()
        self.problem_display = newtexcode(self.problem_code, 'publishedoriginalproblem_'+str(self.pk), "")
        self.save()
        compileasy(self.problem_code,'publishedoriginalproblem_'+str(self.pk))



##delete this model....but this also means that i want to make a foreignkey to Test; ProblemSet in problemobject (instead of manytomany)
#1: add foreign key
#2: Perform migrations and links
#3: delete manytomany field



#perhaps newresponse should have a generic reference....
#units....manytomany or foreign key?
#standalone units? or just allow copying from another Class?
#standalone slides?
