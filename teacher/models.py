from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType

from randomtest.models import Problem,Solution,QuestionType
from randomtest.utils import newtexcode, compileasy,newsoltexcode
from student.models import UserClass,UserUnit,UserUnitObject,UserProblemSet,UserSlides,UserTest
# Create your models here.

class Class(models.Model):#This should be reserved for drafts of classes; also, curated (i.e., professionally done) classes will appear here, which can be copied directly (or used as a template)/starting point
    name = models.CharField(max_length = 100)
    created_date = models.DateTimeField(default = timezone.now)
    units = models.ManyToManyField('Unit',blank = True)# or foreignkey
    version_number = models.IntegerField(default = 0)
    def __str__(self):
        return self.name
#Should I include a Version number?
    def publish(self,userprofile):
        p = PublishedClass(name=self.name,parent_class = self,version_number = self.version_number)
        p.save()
        class_points = 0
        class_prob_num = 0
        for u in self.unit_set.all():
            new_unit = u.publish(p)
            class_points += new_unit.total_points
            class_prob_num += new_unit.num_problems
        p.total_points = class_points
        p.num_problems = class_prob_num
        p.save()
        userprofile.my_published_classes.add(p)
        userprofile.save()
        return p
    def increment_version(self):
        self.version_number = self.version_number + 1
        self.save()

class PublishedClass(models.Model):#class?
    parent_class = models.ForeignKey(Class, null=True,on_delete=models.SET_NULL)
    name = models.CharField(max_length = 100)
    enrolled_students = models.ManyToManyField(User, blank = True)# or userprofile?
    created_date = models.DateTimeField(default = timezone.now)
    units = models.ManyToManyField('Unit',blank=True)
    pub_units = models.ManyToManyField('PublishedUnit',blank=True)
    total_points = models.IntegerField(default = 0)
    num_problems = models.IntegerField(default = 0)
    version_number = models.IntegerField(default = 0)
    def __str__(self):
        return self.name
    def sync_to_parent(self):
        parent_units_pk = []
        for u in self.publishedunit_set.all():
            if u.parent_unit not in self.parent_class.unit_set.all():
                u.delete()
            else:
                if u.version_number != u.parent_unit.version_number:####
                    u.sync_to_parent()
                parent_units_pk.append(u.parent_unit.pk)
        for u in self.parent_class.unit_set.exclude(pk__in=parent_units_pk):
            new_unit = u.publish(self)
        self.update_stats()
        for uc in self.userclass_set.all():
            uc.update_stats()
        self.name = self.parent_class.name
        self.version_number = self.parent_class.version_number
        self.save()
    def update_stats(self):
        total_points = 0
        num_problems = 0
        for u in self.publishedunit_set.all():
            u.update_stats()
            total_points += u.total_points
            num_problems += u.num_problems
        self.total_points = total_points
        self.num_problems = num_problems
        self.save()
    def add_student(self,student):
        self.enrolled_students.add(student)
        self.save()
        new_user_class = UserClass(published_class = self,userprofile = student.userprofile,total_points = self.total_points,points_earned = 0,num_problems = self.num_problems)
        new_user_class.save()
        for unit in self.publishedunit_set.all():
            unit.add_student(student,new_user_class)
        return new_user_class

class Unit(models.Model):#with order
    name = models.CharField(max_length = 100)
    order = models.IntegerField(default = 0)
    total_points = models.IntegerField(default=0)
    num_problems = models.IntegerField(default=0)
    num_problemsets = models.IntegerField(default=0)
    the_class = models.ForeignKey(Class,null = True,blank = True,on_delete=models.CASCADE)
    version_number = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']
    def publish(self,published_class):
        new_unit = PublishedUnit(name=self.name,order=self.order,parent_unit = self,the_class = published_class,version_number = self.version_number)
        new_unit.save()
        for user_class in published_class.userclass_set.all():
            new_user_unit = UserUnit(published_unit = new_unit,user_class = user_class,total_points = new_unit.total_points, points_earned=0,order = new_unit.order,num_problems = new_unit.num_problems,num_problemsets = new_unit.num_problemsets)
            new_user_unit.save()
#        published_class.pub_units.add(new_unit)
#        published_class.save()
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
    def increment_version(self):
        self.version_number = self.version_number + 1
        self.the_class.increment_version()
        self.save()

class PublishedUnit(models.Model):
    parent_unit = models.ForeignKey(Unit,null=True,on_delete=models.SET_NULL)
    name = models.CharField(max_length = 100)
    order = models.IntegerField(default = 0)
    total_points = models.IntegerField(default=0)
    num_problems = models.IntegerField(default=0)
    num_problemsets = models.IntegerField(default=0)
    the_class = models.ForeignKey(PublishedClass,null = True,blank = True,on_delete=models.CASCADE)
    version_number = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']
    def sync_to_parent(self):
        print('start unit',self.name)
        parent_uos_pk=[]
        for uo in self.unit_objects.all():
            if uo.parent_unitobject not in self.parent_unit.unit_objects.all():
                uo.delete()
            else:
                if uo.version_number != uo.parent_unitobject.version_number:
                    uo.sync_to_parent()
                parent_uos_pk.append(uo.parent_unitobject.pk)
        print('mid_unit')
        for uo in self.parent_unit.unit_objects.exclude(pk__in=parent_uos_pk):
            new_uo = uo.publish(self)
        print('mid_unit 2')
        for uu in self.userunit_set.all():
            uu.update_stats()
        self.name = self.parent_unit.name
        self.order = self.parent_unit.order
        self.version_number = self.parent_unit.version_number
        self.save()
        print('end unit')
    def update_stats(self):
        print('update unit start')
        total_points = 0
        num_problems = 0
        num_problemsets = 0
        for uo in self.unit_objects.all():
            try:
                print('pset try start')
                pset = uo.publishedproblemset
                pset.update_stats()
                num_problemsets += 1
                num_problems += pset.num_problems
                total_points += pset.total_points
                print('pset try end')
            except PublishedProblemSet.DoesNotExist:
                try:
                    print('test try start')
                    test = uo.publishedtest
                    test.update_stats()
                    print('pset try end')
                except PublishedTest.DoesNotExist:
                    try:
                        slidegroup = uo.publishedslidegroup
                        slidegroup.update_stats()
                    except PublishedSlideGroup.DoesNotExist:
                        a=0
        self.total_points = total_points
        self.num_problems = num_problems
        self.num_problemsets = num_problemsets
        self.save()
        print('update unit end')
    def add_student(self,student,user_class):
        new_user_unit = UserUnit(published_unit = self,user_class = user_class,total_points=self.total_points, points_earned=0,order = self.order,num_problems = self.num_problems)
        new_user_unit.save()
        num_psets = 0
        for unit_object in self.unit_objects.all():
            new_user_unitobject = UserUnitObject(order = unit_object.order, user_unit = new_user_unit,unit_object = unit_object)
################CHECK The ABOvE line by adding a student.
            new_user_unitobject.save()
            try:
                slidegroup = unit_object.publishedslidegroup
                user_slides = UserSlides(published_slides = slidegroup,userunitobject = new_user_unitobject,num_slides = slidegroup.slides.count())
                user_slides.save()
            except PublishedSlideGroup.DoesNotExist:
                try:
                    pset = unit_object.publishedproblemset
                    user_problemset = UserProblemSet(published_problemset = pset, total_points = pset.total_points,points_earned = 0,num_problems = pset.num_problems,userunitobject = new_user_unitobject)
                    user_problemset.save()
                    num_psets +=1
                except PublishedProblemSet.DoesNotExist:
                    test = unit_object.publishedtest
                    user_test = UserTest(published_test = test, total_points = test.total_points, points_earned = 0,num_problems = test.num_problems,userunitobject = new_user_unitobject)
                    user_test.save()
        new_user_unit.num_problemsets = num_psets
        new_user_unit.save()

class UnitObject(models.Model):
    order = models.IntegerField(default = 0)
    unit = models.ForeignKey(Unit,null=True,related_name='unit_objects',on_delete=models.CASCADE)
    version_number = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']
    def publish(self,published_unit):
        print('start unitobject publish')
        new_unit_object = PublishedUnitObject(unit = published_unit,order = self.order,parent_unitobject = self,version_number = self.version_number)
        new_unit_object.save()
        for user_unit in published_unit.userunit_set.all():
            new_user_unitobject = UserUnitObject(order = new_unit_object.order, user_unit = user_unit,unit_object = new_unit_object)
            new_user_unitobject.save()

        print('mid unitobject publish')
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
        print('end unitobject publish')
        return new_unit_object
    def increment_version(self):
        self.version_number = self.version_number + 1
        self.unit.increment_version()
        self.save()

class PublishedUnitObject(models.Model):
    parent_unitobject = models.ForeignKey(UnitObject,null=True,on_delete=models.SET_NULL)
    order = models.IntegerField(default = 0)
    unit = models.ForeignKey(PublishedUnit,null=True,related_name='unit_objects',on_delete=models.CASCADE)
    version_number = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']
    def sync_to_parent(self):
        try:
            sg = self.publishedslidegroup
            if sg.version_number != sg.parent_slidegroup.version_number:
                sg.sync_to_parent()
        except PublishedSlideGroup.DoesNotExist:####Check these...
            try: 
                pset = self.publishedproblemset
                if pset.version_number != pset.parent_problemset.version_number:
                    pset.sync_to_parent()
            except PublishedProblemSet.DoesNotExist:
                try:
                    test = self.publishedtest
                    if test.version_number != test.parent_test.version_number:
                        test.sync_to_parent()
                except PublishedTest.DoesNotExist:
                    a = 0
##new:
        for uuo in self.userunitobject_set.all():
            uuo.order = self.parent_unitobject.order
            uuo.save()
        self.order = self.parent_unitobject.order
        self.version_number = self.parent_unitobject.version_number
        self.save()


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
    version_number = models.IntegerField(default = 0)
    def __str__(self):
        return self.name
    def publish(self,published_unit_object):
        new_slide_group = PublishedSlideGroup(name = self.name,num_slides = self.slides.count(),unit_object = published_unit_object,parent_slidegroup = self,version_number = self.version_number)
        new_slide_group.save()
        for user_unit_object in published_unit_object.userunitobject_set.all():
            user_slides = UserSlides(published_slides = new_slide_group,userunitobject = user_unit_object,num_slides = self.slides.count())
            user_slides.save()
        for s in self.slides.all():
            s.publish(new_slide_group)
    def increment_version(self):
        self.version_number = self.version_number + 1
        self.unit_object.increment_version()
        self.save()

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
    version_number = models.IntegerField(default = 0)
    def __str__(self):
        return self.name
    def sync_to_parent(self):
        parent_slide_pks=[]
        for s in self.slides.all():
            if s.parent_slide not in self.parent_slidegroup.slides.all():
                s.delete()
            else:
                if s.version_number != s.parent_slide.version_number:
                    s.sync_to_parent()
                parent_slide_pks.append(s.parent_slide.pk)
        for s in self.parent_slidegroup.slides.exclude(pk__in=parent_slide_pks):
            s.publish(self)
        self.name = self.parent_slidegroup.name
        self.version_number = self.parent_slidegroup.version_number
        self.save()
    def update_stats(self):
        self.num_slides = self.slides.count()
        self.save()

class Slide(models.Model):#(i.e., slide 1...etc)
    title = models.CharField(max_length = 100)
    order = models.IntegerField(default = 0)
    slidegroup = models.ForeignKey(SlideGroup,null=True,related_name='slides',on_delete=models.CASCADE)
    top_order_number = models.IntegerField(default = 0)
    version_number = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']
    def __str__(self):
        return self.title
    def publish(self,published_slidegroup):
        new_slide = PublishedSlide(title = self.title, order = self.order,  parent_slide = self, slidegroup = published_slidegroup,top_order_number = self.top_order_number,version_number = self.version_number)
        new_slide.save()
        for so in self.slide_objects.all():
            so.publish(new_slide)
    def increment_version(self):
        self.version_number = self.version_number + 1
        self.slidegroup.increment_version()
        self.save()

class PublishedSlide(models.Model):#(i.e., slide 1...etc)
    title = models.CharField(max_length = 100)
    order = models.IntegerField(default = 0)
    parent_slide = models.ForeignKey(Slide,null=True,on_delete=models.SET_NULL)
    slidegroup = models.ForeignKey(PublishedSlideGroup,null=True,related_name='slides',on_delete=models.CASCADE)
    top_order_number = models.IntegerField(default = 0)
    version_number = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']
    def __str__(self):
        return self.title
    def sync_to_parent(self):
        parent_slideobject_pks = []
        for so in self.slide_objects.all():
            if so.parent_slideobject not in self.parent_slide.slide_objects.all():
                so.delete()
            else:
                if so.version_number != so.parent_slideobject.version_number:
                    so.sync_to_parent()
                parent_slideobject_pks.append(so.parent_slideobject.pk)
        for so in self.parent_slide.slide_objects.exclude(pk__in=parent_slideobject_pks):
            so.publish(self)
        self.title = self.parent_slide.title
        self.order = self.parent_slide.order
        self.top_order_number = self.parent_slide.top_order_number
        self.version_number = self.parent_slide.version_number
        self.save()


class SlideObject(models.Model):#placeholder for components
    order = models.IntegerField(default = 0)
    slide = models.ForeignKey(Slide,null=True,related_name='slide_objects',on_delete=models.CASCADE)
    version_number = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']
    def publish(self,published_slide):
        new_so = PublishedSlideObject(slide = published_slide, order = self.order, parent_slideobject = self,version_number = self.version_number)
        new_so.save()
        try:
            obj = self.textblock
        except TextBlock.DoesNotExist:
            try:
                obj = self.theorem
            except Theorem.DoesNotExist:
                try:
                    obj = self.proof
                except Proof.DoesNotExist:
                    try:
                        obj = self.exampleproblem
                    except ExampleProblem.DoesNotExist:
                        obj = self.imagemodel
        obj.publish(new_so)
        return new_so
    def increment_version(self):
        self.version_number = self.version_number + 1
        self.slide.increment_version()
        self.save()

class PublishedSlideObject(models.Model):#placeholder for components
    order = models.IntegerField(default = 0)
    parent_slideobject = models.ForeignKey(SlideObject,null=True,on_delete=models.SET_NULL)
    slide = models.ForeignKey(PublishedSlide,null=True,related_name='slide_objects',on_delete=models.CASCADE)
    version_number = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']
    def sync_to_parent(self):
        try:
            obj = self.publishedtextblock
            if obj.version_number != obj.parent_textblock.version_number:
                obj.sync_to_parent()
        except PublishedTextBlock.DoesNotExist:
            try:
                obj = self.publishedtheorem
                if obj.version_number != obj.parent_theorem.version_number:
                    obj.sync_to_parent()
            except PublishedTheorem.DoesNotExist:
                try:
                    obj = self.publishedproof
                    if obj.version_number != obj.parent_proof.version_number:
                        obj.sync_to_parent()
                except PublishedProof.DoesNotExist:
                    try:
                        obj = self.publishedexampleproblem
                        if obj.version_number != obj.parent_exampleproblem.version_number:
                            obj.sync_to_parent()
                    except PublishedExampleProblem.DoesNotExist:
                        obj = self.publishedimagemodel
                        if obj.version_number != obj.parent_imagemodel.version_number:
                            obj.sync_to_parent()
        self.order = self.parent_slideobject.order
        self.version_number = self.parent_slideobject.version_number
        self.save()


#theorem, problem, image, textblock,proof,solution (are these dependent?)

class TextBlock(models.Model):
    text_code = models.TextField(blank=True)
    text_display = models.TextField(blank=True)
    up_slide_object = models.OneToOneField(
        SlideObject,
        on_delete=models.CASCADE,
        null = True,
    )
    version_number = models.IntegerField(default = 0)
    def publish(self,so):
        new_textblock = PublishedTextBlock(text_code = self.text_code,text_display="",parent_textblock = self,slide_object = so, version_number = self.version_number)
        new_textblock.save()
        new_textblock.text_display = newtexcode(new_textblock.text_code, 'publishedtextblock_'+str(new_textblock.pk), "")
        new_textblock.save()
        compileasy(new_textblock.text_code,'publishedtextblock_'+str(new_textblock.pk))
        return new_textblock
    def increment_version(self):
        self.version_number = self.version_number + 1
        self.up_slide_object.increment_version()
        self.save()

class PublishedTextBlock(models.Model):
    parent_textblock = models.ForeignKey(TextBlock,null=True,on_delete=models.SET_NULL)
    text_code = models.TextField(blank=True)
    text_display = models.TextField(blank=True)
    slide_object = models.OneToOneField(
        PublishedSlideObject,
        on_delete=models.CASCADE,
        null = True,
    )
    version_number = models.IntegerField(default = 0)
    def sync_to_parent(self):
        tc = self.parent_textblock.text_code
        self.text_code = tc
        self.text_display = newtexcode(tc, 'publishedtextblock_'+str(self.pk), "")
        self.version_number = self.parent_textblock.version_number
        self.save()
        compileasy(tc,'publishedtextblock_'+str(self.pk))

class Proof(models.Model):
    prefix = models.CharField(max_length=20)#Proof, Solution
    proof_code = models.TextField(blank=True)
    proof_display = models.TextField(blank=True)
    isSolution = models.BooleanField(default=0)
    solution = models.ForeignKey(Solution,blank=True,null=True,on_delete=models.CASCADE)
    up_slide_object = models.OneToOneField(
        SlideObject,
        on_delete=models.CASCADE,
        null = True,
    )
    version_number = models.IntegerField(default = 0)
    def publish(self,so):
        new_proof = PublishedProof(prefix=self.prefix,proof_code = self.proof_code,proof_display="",parent_proof=self,slide_object = so,version_number = self.version_number)
        new_proof.save()
        new_proof.proof_display = newtexcode(new_proof.proof_code, 'publishedproofblock_'+str(new_proof.pk), "")
        new_proof.save()
        compileasy(new_proof.proof_code,'publishedproofblock_'+str(new_proof.pk))
        return new_proof
    def increment_version(self):
        self.version_number = self.version_number + 1
        self.up_slide_object.increment_version()
        self.save()


class PublishedProof(models.Model):
    parent_proof = models.ForeignKey(Proof,null=True,on_delete=models.SET_NULL)
    prefix = models.CharField(max_length=20)#Proof, Solution
    proof_code = models.TextField(blank=True)
    proof_display = models.TextField(blank=True)
    isSolution = models.BooleanField(default=0)
    solution = models.ForeignKey(Solution,blank=True,null=True,on_delete=models.CASCADE)
    slide_object = models.OneToOneField(
        PublishedSlideObject,
        on_delete=models.CASCADE,
        null = True,
    )
    version_number = models.IntegerField(default = 0)
    def sync_to_parent(self):
        pc = self.parent_proof.proof_code
        self.proof_code = pc
        self.prefix = self.parent_proof.prefix
        self.proof_display = newtexcode(pc, 'publishedproofblock_'+str(self.pk), "")
        self.version_number = self.parent_proof.version_number
        self.save()
        compileasy(self.proof_code,'publishedproofblock_'+str(self.pk))

class Theorem(models.Model):
    name=models.CharField(max_length=150, default="")
    prefix = models.CharField(max_length=20)#Theorem, Proposition, Lemma, Corollary
    theorem_code = models.TextField(blank=True)
    theorem_display = models.TextField(blank=True)
    up_slide_object = models.OneToOneField(
        SlideObject,
        on_delete=models.CASCADE,
        null = True,
    )
    version_number = models.IntegerField(default = 0)
    def __str__(self):
        return self.name
    def publish(self,so):
        new_theorem = PublishedTheorem(name=self.name,prefix=self.prefix,theorem_code = self.theorem_code,theorem_display="",parent_theorem = self,slide_object = so,version_number = self.version_number)
        new_theorem.save()
        new_theorem.theorem_display = newtexcode(new_theorem.theorem_code, 'publishedtheoremblock_'+str(new_theorem.pk), "")
        new_theorem.save()
        compileasy(new_theorem.theorem_code,'publishedtheoremblock_'+str(new_theorem.pk))
        return new_theorem
    def increment_version(self):
        self.version_number = self.version_number + 1
        self.up_slide_object.increment_version()
        self.save()



class PublishedTheorem(models.Model):
    parent_theorem = models.ForeignKey(Theorem,null=True,on_delete=models.SET_NULL)
    name=models.CharField(max_length=150, default="")
    prefix = models.CharField(max_length=20)#Theorem, Proposition, Lemma, Corollary
    theorem_code = models.TextField(blank=True)
    theorem_display = models.TextField(blank=True)
    slide_object = models.OneToOneField(
        PublishedSlideObject,
        on_delete=models.CASCADE,
        null = True,
    )
    version_number = models.IntegerField(default = 0)
    def __str__(self):
        return self.name
    def sync_to_parent(self):
        tc = self.parent_theorem.theorem_code
        self.theorem_code = tc
        self.name = self.parent_theorem.name
        self.prefix = self.parent_theorem.prefix
        self.theorem_display = newtexcode(tc, 'publishedtheoremblock_'+str(self.pk), "")
        self.version_number = self.parent_theorem.version_number
        self.save()
        compileasy(self.theorem_code,'publishedtheoremblock_'+str(self.pk))

class ExampleProblem(models.Model):
    name = models.CharField(max_length=150, default="")
    prefix = models.CharField(max_length=20,default="")#Example, Exercise
    problem_code = models.TextField(blank=True)
    problem_display = models.TextField(blank=True)
    isProblem = models.BooleanField(default=0)
    problem = models.ForeignKey(Problem,blank=True,null=True,on_delete=models.CASCADE)
    question_type = models.ForeignKey(QuestionType,blank=True,null=True,on_delete=models.CASCADE)
    mc_answer = models.CharField(max_length=1,default = "")
    sa_answer = models.CharField(max_length = 20, default = "")
    answer_A = models.CharField(max_length=500,blank=True)
    answer_B = models.CharField(max_length=500,blank=True)
    answer_C = models.CharField(max_length=500,blank=True)
    answer_D = models.CharField(max_length=500,blank=True)
    answer_E = models.CharField(max_length=500,blank=True)
    author = models.ForeignKey(User,related_name='example_problem',blank=True,null=True,on_delete=models.SET_NULL)
    created_date = models.DateTimeField(default = timezone.now)
    up_slide_object = models.OneToOneField(
        SlideObject,
        on_delete=models.CASCADE,
        null = True,
    )
    version_number = models.IntegerField(default = 0)
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
    def publish(self,so):
        new_example = PublishedExampleProblem(name=self.name,prefix=self.prefix,problem_code = self.problem_code,problem_display="",isProblem=self.isProblem, problem=self.problem,question_type=self.question_type,mc_answer = self.mc_answer,sa_answer = self.sa_answer,answer_A = self.answer_A,answer_B = self.answer_B,answer_C = self.answer_C,answer_D = self.answer_D,answer_E = self.answer_E,author=self.author,parent_exampleproblem = self,slide_object = so,version_number = self.version_number)
        new_example.save()
        new_example.problem_display = newtexcode(new_example.problem_code, 'publishedexampleproblem_'+str(new_example.pk), "")
        new_example.save()
        compileasy(new_example.problem_code,'publishedexampleproblem_'+str(new_example.pk))
        return new_example
    def increment_version(self):
        self.version_number = self.version_number + 1
        self.up_slide_object.increment_version()
        self.save()


class PublishedExampleProblem(models.Model):
    parent_exampleproblem = models.ForeignKey(ExampleProblem,null=True,on_delete=models.SET_NULL)
    name = models.CharField(max_length=150, default="")
    prefix = models.CharField(max_length=20,default="")#Example, Exercise
    problem_code = models.TextField(blank=True)
    problem_display = models.TextField(blank=True)
    isProblem = models.BooleanField(default=0)
    problem = models.ForeignKey(Problem,blank=True,null=True,on_delete=models.CASCADE)
    question_type = models.ForeignKey(QuestionType,blank=True,null=True,on_delete=models.CASCADE)
    mc_answer = models.CharField(max_length=1,default = "")
    sa_answer = models.CharField(max_length = 20, default = "")
    answer_A = models.CharField(max_length=500,blank=True)
    answer_B = models.CharField(max_length=500,blank=True)
    answer_C = models.CharField(max_length=500,blank=True)
    answer_D = models.CharField(max_length=500,blank=True)
    answer_E = models.CharField(max_length=500,blank=True)
    author = models.ForeignKey(User,related_name='published_example_problem',blank=True,null=True,on_delete=models.SET_NULL)
    created_date = models.DateTimeField(default = timezone.now)
    slide_object = models.OneToOneField(
        PublishedSlideObject,
        on_delete=models.CASCADE,
        null = True,
    )
    version_number = models.IntegerField(default = 0)
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
        pc = self.parent_exampleproblem.problem_code
        self.name = self.parent_exampleproblem.name
        self.prefix = self.parent_exampleproblem.prefix
        self.problem_code = pc
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
        self.problem_display = newtexcode(pc, 'publishedexampleproblem_'+str(self.pk), "")
        self.version_number = self.parent_exampleproblem.version_number
        self.save()
        compileasy(self.problem_code,'publishedexampleproblem_'+str(self.pk))

class ImageModel(models.Model):
    image = models.ImageField(upload_to='images')
    up_slide_object = models.OneToOneField(
        SlideObject,
        on_delete=models.CASCADE,
        null = True,
    )
    version_number = models.IntegerField(default = 0)
    def publish(self,so):
        new_image = PublishedImageModel(image = self.image,parent_image = self,slide_object = so,version_number = self.version_number)
        new_image.save()
        return new_image
    def increment_version(self):
        self.version_number = self.version_number + 1
        self.up_slide_object.increment_version()
        self.save()

class PublishedImageModel(models.Model):
    parent_image = models.ForeignKey(ImageModel,null=True,on_delete=models.SET_NULL)
    image = models.ImageField(upload_to='images')
    slide_object = models.OneToOneField(
        PublishedSlideObject,
        on_delete=models.CASCADE,
        null = True,
    )
    version_number = models.IntegerField(default = 0)
    def sync_to_parent(self):
        self.image = self.parent_image.image
        self.version_number = self.parent_image.version_number
        self.save()

class ProblemSet(models.Model):#like NewTest
    unit_object = models.OneToOneField(
        UnitObject,
        on_delete=models.CASCADE,
        null = True,
    )
    name = models.CharField(max_length = 100)
    created_date = models.DateTimeField(default = timezone.now)
#    problem_objects = models.ManyToManyField('ProblemObject',blank=True)
    default_point_value = models.IntegerField(default = 1)
    total_points = models.IntegerField(default=0)
    num_problems = models.IntegerField(default=0)
    due_date = models.DateTimeField(null = True)
    start_date = models.DateTimeField(null = True)
    version_number = models.IntegerField(default = 0)
    def __str__(self):
        return self.name
    def publish(self,published_unit_object):
        new_problemset = PublishedProblemSet(name = self.name,default_point_value = self.default_point_value,unit_object = published_unit_object, parent_problemset = self, due_date = self.due_date, start_date = self.start_date,version_number = self.version_number)
        new_problemset.save()
        for user_unit_object in published_unit_object.userunitobject_set.all():
            user_pset = UserProblemSet(published_problemset = new_problemset, total_points = self.total_points,points_earned = 0,num_problems = self.num_problems,userunitobject = user_unit_object)
            user_pset.save()

        total_points=0
        for po in self.problem_objects.all():
            po.publish(published_pset=new_problemset)
#            new_problemset.problem_objects.add(new_po)
            total_points += po.point_value
        new_problemset.total_points = total_points
        new_problemset.num_problems = new_problemset.problem_objects.count()
        new_problemset.save()
    def increment_version(self):
        self.version_number = self.version_number + 1
        self.unit_object.increment_version()
        self.save()

    def add_to_end(self,prob):
        if self.problem_objects.filter(problem = prob).exists() == False:
            po = ProblemObject(order = self.problem_objects.count()+1,point_value = self.default_point_value,isProblem = 1,problem = prob,question_type = prob.question_type_new)
            po.problemset = self
            po.save()
            self.increment_version()
            return 1
        return 0
    def problem_list(self):
        P = []
        for i in self.problem_objects.all():
            if i.isProblem:
                P.append(i.problem)
        return P

####sync_to_parent needs work beyond here.

class PublishedProblemSet(models.Model):#like NewTest
    parent_problemset = models.ForeignKey(ProblemSet,null=True,on_delete=models.SET_NULL)
    unit_object = models.OneToOneField(
        PublishedUnitObject,
        on_delete=models.CASCADE,
        null = True,
    )
    name = models.CharField(max_length = 100)
    created_date = models.DateTimeField(default = timezone.now)
#    problem_objects = models.ManyToManyField('PublishedProblemObject',blank=True)
    default_point_value = models.IntegerField(default = 1)
    total_points = models.IntegerField(default=0)
    num_problems = models.IntegerField(default=0)
    due_date = models.DateTimeField(null = True)
    start_date = models.DateTimeField(null = True)
    version_number = models.IntegerField(default = 0)
    def __str__(self):
        return self.name
    def sync_to_parent(self):
        print('problemset sync start',self.pk)
        parent_po_pks=[]
        print('middle 1')
        for po in self.problem_objects.all():
            if po.parent_problemobject not in self.parent_problemset.problem_objects.all():
                print('if')
                po.response_set.all().delete()
                po.delete()
            else:
                print('else')
                if po.version_number != po.parent_problemobject.version_number:
                    print('be else')
                    po.sync_to_parent()
                    print('af else')
                parent_po_pks.append(po.parent_problemobject.pk)
        print('middle 2')
        for po in self.parent_problemset.problem_objects.exclude(pk__in = parent_po_pks):
            print('gey')
            new_po = po.publish(published_pset=self)
        print('middle 3')
        for ups in self.userproblemset_set.all():
            ups.update_stats()
            ups.is_initialized = 0
            ups.save()
        print('middle 4')
        self.name = self.parent_problemset.name
        self.default_point_value = self.parent_problemset.default_point_value
        self.version_number = self.parent_problemset.version_number
        self.due_date = self.parent_problemset.due_date
        self.start_date = self.parent_problemset.start_date
        self.save()
        print('problemset sync end',self.pk)
    def update_stats(self):
        total_points = 0
        self.num_problems = self.problem_objects.count()
        for po in self.problem_objects.all():
            total_points += po.point_value
        self.total_points = total_points
        self.save()

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
    student_gradeable = models.BooleanField(default = True)
    version_number = models.IntegerField(default = 0)
    def __str__(self):
        return self.name
    def publish(self,published_unit_object):
        new_test = PublishedTest(name = self.name,default_point_value = self.default_point_value,default_blank_value = self.default_blank_value,unit_object = published_unit_object, parent_test = self, due_date = self.due_date,time_limit = self.time_limit, start_date = self.start_date,student_gradeable = self.student_gradeable,version_number = self.version_number)
        new_test.save()
        num_problems = self.problem_objects.count()
        total_points=0
        for po in self.problem_objects.all():
            total_points += po.point_value
            po.publish(published_test = new_test)
        for user_unit_object in published_unit_object.userunitobject_set.all():
            user_test = UserTest(published_test = new_test,total_points = total_points, points_earned = 0,num_problems = num_problems,userunitobject = user_unit_object)
            user_test.save()

        new_test.total_points = total_points
        new_test.num_problems = num_problems#new_test.problem_objects.count()
        new_test.save()
    def increment_version(self):
        self.version_number = self.version_number + 1
        self.unit_object.increment_version()
        self.save()

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
    student_gradeable = models.BooleanField(default = True)
    version_number = models.IntegerField(default = 0)
    def __str__(self):
        return self.name
    def sync_to_parent(self):
        print('test start')
        parent_po_pks = []
        for po in self.problem_objects.all():
            if po.parent_problemobject not in self.parent_test.problem_objects.all():
                po.response_set.all().delete()
                po.delete()
            else:
                if po.version_number != po.parent_problemobject.version_number:
                    po.sync_to_parent()
                parent_po_pks.append(po.parent_problemobject.pk)
        for po in self.parent_test.problem_objects.exclude(pk__in = parent_po_pks):
            new_po = po.publish(published_test = self)
        for ut in self.usertest_set.all():
            ut.is_initialized = 0
            ut.update_stats()
            ut.save()
        self.name = self.parent_test.name
        self.default_point_value = self.parent_test.default_point_value
        self.default_blank_value = self.parent_test.default_blank_value
        self.total_points = self.parent_test.total_points
        self.num_problems = self.parent_test.num_problems
        self.due_date = self.parent_test.due_date
        self.start_date = self.parent_test.start_date
        self.time_limit = self.parent_test.time_limit
        self.student_gradeable = self.parent_test.student_gradeable
        self.version_number = self.parent_test.version_number
        self.save()
        print('test end')
    def update_stats(self):
        print('test update start')
        total_points = 0
        self.num_problems = self.problem_objects.count()
        for po in self.problem_objects.all():
            total_points += po.point_value
        self.total_points = total_points
        self.save()
        print('test update end')


class ProblemObject(models.Model):
    problemset = models.ForeignKey(ProblemSet,null = True, related_name = "problem_objects",on_delete=models.CASCADE)
    test = models.ForeignKey(Test,null = True,related_name = "problem_objects",on_delete=models.CASCADE)
    order = models.IntegerField(default = 0)
    point_value = models.IntegerField(default = 1)
    blank_point_value = models.FloatField(default = 0)
    problem_code = models.TextField(blank=True)
    problem_display = models.TextField(blank=True)
    isProblem = models.BooleanField(default=0)
    problem = models.ForeignKey(Problem,blank=True,null=True,on_delete=models.CASCADE)
    question_type = models.ForeignKey(QuestionType,null=True,on_delete=models.CASCADE)
    mc_answer = models.CharField(max_length=1,blank=True)
    sa_answer = models.CharField(max_length = 20,blank=True)
    answer_A = models.CharField(max_length=500,blank=True)
    answer_B = models.CharField(max_length=500,blank=True)
    answer_C = models.CharField(max_length=500,blank=True)
    answer_D = models.CharField(max_length=500,blank=True)
    answer_E = models.CharField(max_length=500,blank=True)
    author = models.ForeignKey(User,related_name='problem_object',blank=True,null=True,on_delete=models.SET_NULL)
    created_date = models.DateTimeField(default = timezone.now)
    version_number = models.IntegerField(default = 0)
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
    def publish(self,published_test=None,published_pset=None):
        new_po = PublishedProblemObject(order = self.order,point_value=self.point_value,problem_code = self.problem_code,problem_display="",isProblem=self.isProblem, problem=self.problem,question_type=self.question_type,mc_answer = self.mc_answer,sa_answer = self.sa_answer,answer_A = self.answer_A,answer_B = self.answer_B,answer_C = self.answer_C,answer_D = self.answer_D,answer_E = self.answer_E,author=self.author,parent_problemobject = self,problemset = published_pset, test = published_test,blank_point_value = self.blank_point_value,version_number = self.version_number)
        new_po.save()
        if new_po.isProblem == 0:
            if new_po.question_type.question_type =='multiple choice':
                new_po.problem_display = newtexcode(new_po.problem_code, 'publishedoriginalproblem_'+str(new_po.pk), new_po.answers())
            else:
                new_po.problem_display = newtexcode(new_po.problem_code, 'publishedoriginalproblem_'+str(new_po.pk), "")
            new_po.save()
            compileasy(new_po.problem_code,'publishedoriginalproblem_'+str(new_po.pk))
##check this after allowing solution viewing in new format.
        for so in self.solution_objects.all():
            so.publish(published_problemobject = new_po)
##
        return new_po
    def increment_version(self):
        self.version_number = self.version_number + 1
        try:
            self.problemset.increment_version()
        except:
            self.test.increment_version()
        self.save()
    def get_pset(self):
        pset = self.problemset
        if pset is not None:
            return ('p',pset)
        test = self.test
        if test is not None:
            return ('t',test)
        return ('n',None)
#        except ProblemSet.DoesNotExist:
#try:
#                pset = self.test
#                return ('t',pset)
#            except Test.DoesNotExist:
#                return ('n',None)


class PublishedProblemObject(models.Model):
    problemset = models.ForeignKey(PublishedProblemSet,null=True,related_name="problem_objects",on_delete=models.CASCADE)
    test = models.ForeignKey(PublishedTest,null=True,related_name = "problem_objects",on_delete=models.CASCADE)
    parent_problemobject = models.ForeignKey(ProblemObject,null=True,on_delete=models.SET_NULL)
    order = models.IntegerField(default = 0)
    point_value = models.IntegerField(default = 1)
    blank_point_value = models.FloatField(default = 0)
    problem_code = models.TextField(blank=True)
    problem_display = models.TextField(blank=True)
    isProblem = models.BooleanField(default=0)
    problem = models.ForeignKey(Problem,blank=True,null=True,on_delete=models.CASCADE)
    question_type = models.ForeignKey(QuestionType,null=True,on_delete=models.CASCADE)
    mc_answer = models.CharField(max_length=1,blank=True)
    sa_answer = models.CharField(max_length = 20,blank=True)
    answer_A = models.CharField(max_length=500,blank=True)
    answer_B = models.CharField(max_length=500,blank=True)
    answer_C = models.CharField(max_length=500,blank=True)
    answer_D = models.CharField(max_length=500,blank=True)
    answer_E = models.CharField(max_length=500,blank=True)
    author = models.ForeignKey(User,related_name='published_problem_object',blank=True,null=True,on_delete=models.SET_NULL)
    created_date = models.DateTimeField(default = timezone.now)
    version_number = models.IntegerField(default = 0)
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
        self.version_number = self.parent_problemobject.version_number
        self.save()
        compileasy(self.problem_code,'publishedoriginalproblem_'+str(self.pk))
        for r in self.response_set.all():
            r.order = self.parent_problemobject.order
            if self.parent_problemobject.question_type.question_type == "multiple choice" or self.parent_problemobject.question_type.question_type == "short answer":
                if r.response == "":
                    r.attempted = 0
                else:
                    r.attempted = 1
            r.save()
        parent_so_pks = []
        for so in self.solution_objects.all():
            if so.parent_solutionobject not in self.parent_problemobject.solution_objects.all():
                so.delete()
            else:
                if so.version_number != so.parent_solutionobject.version_number:
                    so.sync_to_parent()
                parent_so_pks.append(so.parent_solutionobject.pk)
        for so in self.parent_problemobject.solution_objects.exclude(pk__in = parent_so_pks):
            new_so = so.publish(published_problemobject = self)
            new_so.save()



class SolutionObject(models.Model):
    problem_object = models.ForeignKey(ProblemObject,null = True, related_name = "solution_objects",on_delete=models.CASCADE)
    order = models.IntegerField(default = 0)
    solution_code = models.TextField(blank=True)
    solution_display = models.TextField(blank=True)
    isSolution = models.BooleanField(default=0)
    solution = models.ForeignKey(Solution,blank=True,null=True,on_delete=models.CASCADE)
    author = models.ForeignKey(User,related_name='solution_object',blank=True,null=True,on_delete=models.SET_NULL)
    created_date = models.DateTimeField(default = timezone.now)
    version_number = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']
    def publish(self,published_problemobject=None):
        new_so = PublishedSolutionObject(order = self.order,solution_code = self.solution_code,solution_display="",isSolution=self.isSolution, solution=self.solution,author=self.author,parent_solutionobject = self,problem_object = published_problemobject,version_number = self.version_number)
        new_so.save()
        if new_so.isSolution == 0:
            new_so.solution_display = newsoltexcode(new_so.solution_code, 'publishedoriginalsolution_'+str(new_so.pk))###
            new_so.save()
            compileasy(new_so.solution_code,'publishedoriginalsolution_'+str(new_so.pk))
        return new_so
    def increment_version(self):
        self.version_number = self.version_number + 1
        self.problem_object.increment_version()
        self.save()


class PublishedSolutionObject(models.Model):
    problem_object = models.ForeignKey(PublishedProblemObject,null=True,related_name="solution_objects",on_delete=models.CASCADE)
    parent_solutionobject = models.ForeignKey(SolutionObject,null=True,on_delete=models.SET_NULL)
    order = models.IntegerField(default = 0)
    solution_code = models.TextField(blank=True)
    solution_display = models.TextField(blank=True)
    isSolution = models.BooleanField(default=0)
    solution = models.ForeignKey(Solution,blank=True,null=True,on_delete=models.CASCADE)
    author = models.ForeignKey(User,related_name='published_solution_object',blank=True,null=True,on_delete=models.SET_NULL)
    created_date = models.DateTimeField(default = timezone.now)
    version_number = models.IntegerField(default = 0)
    class Meta:
        ordering = ['order']
    def sync_to_parent(self):
        self.order = self.parent_solutionobject.order
        self.solution_code = self.parent_solutionobject.solution_code
        self.isSolution = self.parent_solutionobject.isSolution
        self.solution = self.parent_solutionobject.solution
        self.author = self.parent_solutionobject.author
        self.save()
        self.solution_display = newsoltexcode(self.solution_code, 'publishedoriginalsolution_'+str(self.pk))
        self.version_number = self.parent_solutionobject.version_number
        self.save()
        compileasy(self.solution_code,'publishedoriginalsolution_'+str(self.pk))






#perhaps newresponse should have a generic reference....
#units....manytomany or foreign key?
#standalone units? or just allow copying from another Class?
#standalone slides?
