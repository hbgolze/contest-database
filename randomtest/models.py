from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.db.models import Max,Min

# Create your models here.
TIMEZONES=(
    ("US/Alaska","US/Alaska"),
    ("US/Aleutian","US/Aleutian"),
    ("US/Arizona","US/Arizona"),
    ("US/Central","US/Central"),
    ("US/East-Indiana","US/East-Indiana"),
    ("US/Eastern","US/Eastern"),
    ("US/Hawaii","US/Hawaii"),
    ("US/Indiana-Starke","US/Indiana-Starke"),
    ("US/Michigan","US/Michigan"),
    ("US/Mountain","US/Mountain"),
    ("US/Pacific","US/Pacific"),
    ("US/Samoa","US/Samoa")
)
class Dropboxurl(models.Model):
    url=models.CharField(max_length = 100)
    def __str__(self):
        return self.url

class Tag(models.Model):
    tag = models.CharField(max_length = 50)
    def __str__(self):
        return self.tag

class NewTag(models.Model):
    tag = models.CharField(max_length = 50)
    label = models.CharField(max_length = 50)
    level = models.IntegerField(default = 0)
    parent = models.ForeignKey("self",null = True,related_name = "children",on_delete=models.CASCADE)
    description = models.TextField(blank = True)
    def __str__(self):
        if self.level > 1:
            return str(self.parent) + '>' + self.label
        return self.label

    class Meta:
        ordering = ['tag']

class Type(models.Model):
    type = models.CharField(max_length = 50)
    label = models.CharField(max_length = 50,blank = True)
    top_index = models.IntegerField(default = 0)
    is_contest = models.BooleanField(default = 1)
    default_question_type = models.CharField(max_length = 4,default = 'pf')
    readable_label_pre_form = models.CharField(max_length = 50,default = '')
    readable_label_post_form = models.CharField(max_length = 50,default = '')
    allow_form_letter = models.BooleanField(default = 0)
    is_sourced = models.BooleanField(default = 0)
    min_year = models.IntegerField(blank = True,null = True)
    max_year = models.IntegerField(blank = True,null = True)
    def __str__(self):
        return self.label
    class Meta:
        ordering = ['label']
    def update_years(self):
        P = self.problems.all()
        min_year = P.aggregate(Min('year'))
        max_year = P.aggregate(Max('year'))
        self.min_year = min_year['year__min']
        self.max_year = max_year['year__max']
        self.save()
    def accumulate_sa_answers(self):
        D={}
        for p in self.problems.all():
            if p.sa_answer in D:
                D[sa_answer] += 1
            else:
                D[sa_answer] = 1
        return {k: v for k,v in sorted(D.items(),key = lambda item: -item[1])}

class Round(models.Model):
    name = models.CharField(max_length = 50)
    type = models.ForeignKey(Type,blank = True,null = True, related_name = "rounds",on_delete=models.CASCADE)
    default_question_type = models.CharField(max_length = 4,default = 'pf')
    readable_label_pre_form = models.CharField(max_length = 50,default = '')
    readable_label_post_form = models.CharField(max_length = 50,default = '')
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class ContestTest(models.Model):
    contest_label = models.CharField(max_length = 100,blank = True)
    contest_type = models.ForeignKey(Type,related_name='contests',blank = True,null = True, on_delete=models.CASCADE)
    round =  models.ForeignKey(Round,related_name = 'contests',blank = True,null = True,on_delete=models.CASCADE)
    year = models.IntegerField(default = 2019)
    form_letter = models.CharField(max_length = 2,blank=True)
    short_label = models.CharField(max_length = 100,blank = True)
    def __str__(self):
        return self.contest_label
    class Meta:
        ordering = ['year','form_letter','contest_label']
    def modify_info(self,year= 0,short_label='',contest_label = ''):
        if year != 0:
            self.year = year
        if short_label != '':
            self.short_label = short_label
        if contest_label != '':
            self.contest_label = contest_label
        self.save()
        for p in self.problems.all():
            p.modify_info(year = year,test_label = short_label,readable_prefix = contest_label)
            
                
class SourceType(models.Model):
    name = models.CharField(max_length = 15)
    def __str__(self):
        return self.name

class Source(models.Model):
    source_type = models.ForeignKey(SourceType,null = True,on_delete=models.CASCADE)#book; contest; person
    title = models.CharField(max_length = 200,default = '')#book
    author = models.CharField(max_length = 200,default = '')#for book; person...
    year = models.CharField(max_length = 4,default = '',blank = True)#all? optional though (except contest)
    contest_name = models.CharField(max_length = 30,default = '')
    contest_short_name = models.CharField(max_length = 30,default = '')
    def __str__(self):
        if self.source_type.name == "book":
            return self.title
        elif self.source_type.name == "contest":
            return self.year+' '+self.contest_name
        elif self.source_type.name == "person":
            return self.author

class BookChapter(models.Model):
    source = models.ForeignKey(Source,null = True,on_delete=models.CASCADE)
    name = models.CharField(max_length = 200,default = '')
    chapter_number = models.IntegerField()
    class Meta:
        ordering = ['chapter_number']
    def __str__(self):
        return self.name

class ProblemApproval(models.Model):
    approval_user = models.ForeignKey(User,blank = True,null = True,on_delete=models.SET_NULL)
    APPROVAL_CHOICES = (
        ('AP', 'Approved'),
        ('MN', 'Approved Subject to Minor Revision'),
        ('MJ', 'Needs Major Revision'),
        ('DE', 'Propose For Deletion'),
        )
    approval_status = models.CharField(max_length = 2,choices = APPROVAL_CHOICES,blank = False,default = 'MJ')
    author_name = models.CharField(max_length = 50,blank = True)

class QuestionType(models.Model):#multiple choice; short answer; proof
    question_type = models.CharField(max_length = 20)
    def __str__(self):
        return self.question_type

class Solution(models.Model):
    solution_text = models.TextField()
    display_solution_text = models.TextField(blank = True)
    solution_number = models.IntegerField(default = 1)
    problem_label = models.CharField(max_length = 20,blank = True)
    tags = models.ManyToManyField(Tag,blank = True)
    authors = models.ManyToManyField(User,blank = True)
    created_date = models.DateTimeField(default = timezone.now)
    modified_date = models.DateTimeField(default = timezone.now)
    parent_problem = models.ForeignKey('Problem',null = True,on_delete=models.CASCADE)
    def __str__(self):
        return self.problem_label+' sol '+str(self.solution_number)+str(self.authors.all())


class Sticky(models.Model):
    problem_label = models.CharField(max_length = 20)
    sticky_date = models.DateTimeField(default = timezone.now)
    usertest = models.ForeignKey('UserTest',null = True,blank = True,on_delete=models.CASCADE)
    test_label = models.CharField(max_length = 50,blank = True)
    def __str__(self):
        return self.problem_label

class Comment(models.Model):
    comment_text = models.TextField()
    problem_label = models.CharField(max_length = 20,blank = True)
    comment_number = models.IntegerField(default = 1)
    author = models.ForeignKey(User,null = True,on_delete = models.SET_NULL)
    author_name = models.CharField(max_length = 50,blank = True)
    created_date = models.DateTimeField(default = timezone.now)
    def __str__(self):
        return self.problem_label+' comment '+str(self.created_date)+', '+str(self.author)

class Problem(models.Model):
    problem_number = models.IntegerField(default = 0)
    tags = models.ManyToManyField(Tag,related_name = 'problems',blank = True)#related name is used correctly here...
    newtags = models.ManyToManyField(NewTag,related_name = 'problems',blank = True)
#    tags = models.ManyToManyField(Tag,blank=True)
    type_new = models.ForeignKey(Type,related_name='problems',blank = True,null = True,on_delete=models.CASCADE)#new(should replace)
    round = models.ForeignKey(Round,related_name = 'problems',blank = True,null = True,on_delete=models.SET_NULL)
    question_type_new = models.ForeignKey(QuestionType,related_name = 'question_type_new',blank = True,null = True,on_delete=models.SET_NULL)#new(should replace), then replace again.
    year = models.IntegerField(default = 2018)
    difficulty = models.IntegerField(blank = True,null = True)
    types = models.ManyToManyField(Type)#allows for  multiple types, should be replaced
    answer = models.CharField(max_length = 20,blank = True)#should be replaced
    latexanswer = models.CharField(max_length = 100,blank = True)#should be replaced
    label = models.CharField(max_length = 20)
    readable_label = models.CharField(max_length = 20,blank = True)
    latex_label = models.CharField(max_length = 20,blank = True)
    problem_text = models.TextField(blank = True)
    mc_problem_text = models.TextField(blank = True)
    display_problem_text = models.TextField(blank = True)
    display_mc_problem_text = models.TextField(blank = True)
    needs_answers = models.BooleanField(default = 0)
    answer_choices = models.TextField(blank = True)#should be replaced
    answer_A = models.CharField(max_length = 500,blank = True)
    answer_B = models.CharField(max_length = 500,blank = True)
    answer_C = models.CharField(max_length = 500,blank = True)
    answer_D = models.CharField(max_length = 500,blank = True)
    answer_E = models.CharField(max_length = 500,blank = True)
    mc_answer = models.CharField(max_length = 1,blank = True)
    sa_answer = models.CharField(max_length = 150,blank = True)
    form_letter = models.CharField(max_length = 2,blank = True)
    test_label = models.CharField(max_length = 50,blank = True)
    contest_test = models.ForeignKey(ContestTest,related_name='problems',blank = True,null = True,on_delete = models.SET_NULL)
    question_type = models.ManyToManyField(QuestionType)#deprecated?
    solutions = models.ManyToManyField(Solution,blank = True)
    top_solution_number = models.IntegerField(blank = True,null = True)
    author = models.ForeignKey(User,related_name = 'author',blank = True,null = True,on_delete=models.SET_NULL)
    author_name = models.CharField(max_length = 50,blank = True)
    created_date = models.DateTimeField(default = timezone.now)
    approval_status = models.BooleanField(default = 0)#deprecated
    approval_user = models.ForeignKey(User,related_name = 'approval_user',blank = True,null = True,on_delete=models.SET_NULL)#deprecated
    comments = models.ManyToManyField(Comment,blank = True)
    approvals = models.ManyToManyField(ProblemApproval,blank = True)
    duplicate_problems = models.ManyToManyField("self",blank = True)
    problem_number_prefix = models.CharField(max_length = 5,default = "")
    notes = models.TextField(blank = True)
    source = models.ForeignKey(Source,blank = True,null = True,on_delete=models.CASCADE)
    book_chapter = models.ForeignKey(BookChapter,blank = True,null = True,on_delete=models.CASCADE)
    order = models.IntegerField(default = 0)
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
    def answers(self):
        s = '\n\n$\\textbf{(A) }{'+self.answer_A
        k = len(self.answer_A)
        if len(self.answer_A) > 0 and self.answer_A[k-2:k] == '\\\\':
            s = s[0:-2]+ '}\\\\\n\\textbf{(B) }{'+self.answer_B
        else:
            s += '}\\qquad\\textbf{(B) }{'+self.answer_B
        k = len(self.answer_B)
        if len(self.answer_B) > 0 and self.answer_B[k-2:k] == '\\\\':
            s = s[0:-2]+ '}\\\\\n\\textbf{(C) }{'+self.answer_C
#            s += '}\\\n\\textbf{(C) }{'+self.answer_C
        else:
            s += '}\\qquad\\textbf{(C) }{'+self.answer_C
        k = len(self.answer_C)
        if len(self.answer_C) > 0 and self.answer_C[k-2:k] == '\\\\':
            s = s[0:-2]+ '}\\\\\n\\textbf{(D) }{'+self.answer_D
#            s += '}\\\n\\textbf{(D) }{'+self.answer_D
        else:
            s += '}\\qquad\\textbf{(D) }{'+self.answer_D
        k = len(self.answer_D)
        if len(self.answer_D) > 0 and self.answer_D[k-2:k] == '\\\\':
            s = s[0:-2]+ '}\\\\\n\\textbf{(E) }{'+self.answer_E
 #           s += '}\\\n\\textbf{(E) }{'+self.answer_E
        else:
            s += '}\\qquad\\textbf{(E) }{'+self.answer_E
        return s + '}$\n\n'
    def correct_answer(self):
        if self.mc_answer == 'A':
            return self.answer_A
        if self.mc_answer == 'B':
            return self.answer_B
        if self.mc_answer == 'C':
            return self.answer_C
        if self.mc_answer == 'D':
            return self.answer_D
        if self.mc_answer == 'E':
            return self.answer_E
        return ''
    def modify_info(self,year=0,test_label='',readable_prefix=''):
        if year != 0:
            self.year = year
        if test_label != '':
            self.test_label = test_label
            self.label = test_label + str(self.problem_number)
        if readable_prefix != '':
            self.readable_label = readable_prefix+' #' + str(self.problem_number)
        self.save()

    
class ProofResponse(models.Model):
    problem = models.ForeignKey(Problem,null=True,on_delete=models.CASCADE)
    proof = models.TextField(blank = True)
    problem_label = models.CharField(max_length = 20)
    modified_date = models.DateTimeField(default = timezone.now)
    points_awarded = models.IntegerField(default = 0)
    attempted = models.BooleanField(default = 0)
    is_graded = models.BooleanField(default = 0)
    def __str__(self):
        return self.problem_label
    
class Response(models.Model):
    problem = models.ForeignKey(Problem,blank = True, null = True,on_delete=models.CASCADE)
    response = models.CharField(max_length = 10,blank = True)
    problem_label = models.CharField(max_length = 20)
    modified_date = models.DateTimeField(default = timezone.now)
    attempted = models.BooleanField(default = 0)
    stickied = models.BooleanField(default = 0)
    def __str__(self):
        return self.response



class Test(models.Model):
    name = models.CharField(max_length = 50)#Perhaps use a default naming scheme
    problems = models.ManyToManyField(Problem)
    types = models.ManyToManyField(Type,blank = True)
    created_date = models.DateTimeField(default = timezone.now)
    last_attempted_date = models.DateTimeField(default = timezone.now)
    def __str__(self):
        return self.name
    def print_types(self):
        s = ''
        L = list(self.types.all())
        if len(L) > 0:
            s = L[0].type
        for i in range(1,len(L)):
            s += ', '+L[i].type
        return s
    def refresh_types(self):
        t = list(self.types.all())
        for i in t:
            self.types.remove(i)
        P = list(self.problems.all())
        for i in P:
            typs = list(i.types.all())
            for j in typs:
                if self.types.filter(type = j).count()==0:
                    self.types.add(j)
        self.save()
        
class TestCollection(models.Model):
    name = models.CharField(max_length = 50)
    tests = models.ManyToManyField(Test)
    def __str__(self):
        return self.name

class ProblemGroup(models.Model):
    name = models.CharField(max_length=50)#Perhaps use a default naming scheme
    problems = models.ManyToManyField(Problem)
    created_date = models.DateTimeField(default = timezone.now)
    is_shared = models.BooleanField(default = 0)
    def __str__(self):
        return self.name
    def add_to_end(self,prob):
        if self.problem_objects.filter(problem = prob).exists() == False:
            pg_object = ProblemGroupObject(problemgroup = self,problem=prob,order=self.problem_objects.count()+1)
            pg_object.save()
            return 1
        return 0
    def problem_list(self):
        P = []
        for i in self.problem_objects.all():
            P.append(i.problem)
        return P
    def order_by_num(self):
        L=list(self.problem_objects.order_by('problem__problem_number'))
        for i in range(0,len(L)):
            L[i].order = i+1
            L[i].save()

class ProblemGroupObject(models.Model):
    problemgroup = models.ForeignKey(ProblemGroup,null = True, related_name = "problem_objects",on_delete=models.CASCADE)
    order = models.IntegerField(default = 0)
    problem = models.ForeignKey(Problem,blank=True,null=True,on_delete=models.CASCADE)
    created_date = models.DateTimeField(default = timezone.now)
    class Meta:
        ordering = ['order']

class Folder(models.Model):
    name = models.CharField(max_length = 50)
    tests = models.ManyToManyField(Test)
    def __str__(self):
        return self.name


class Responses(models.Model):
    test = models.ForeignKey(Test,null=True,on_delete = models.CASCADE)
    responses = models.ManyToManyField(Response,blank = True)
    num_problems_correct = models.IntegerField(blank = True,null = True)
    show_answer_marks = models.BooleanField(default = 0)
    modified_date = models.DateTimeField(default = timezone.now)
    def __str__(self):
        return self.test.name

#Equivalent to Response, except it is used to hold items for the User Response queue (also point value added)
class UserResponse(models.Model):
    test_label = models.CharField(max_length = 50,blank = True)
    response = models.CharField(max_length = 10,blank = True)
    problem_label = models.CharField(max_length = 30)
    modified_date = models.DateTimeField(default = timezone.now)
    correct = models.BooleanField(default = 0)
    usertest = models.ForeignKey('UserTest',blank = True, null = True,on_delete = models.SET_NULL)
    point_value = models.IntegerField(default = 0)


class SortableProblem(models.Model):
    newtest_pk = models.CharField(max_length = 15)#unnecessary
    newtest = models.ForeignKey('NewTest', null = True,on_delete=models.CASCADE)
    order = models.IntegerField(default = 0)
    problem = models.ForeignKey(Problem, blank = True,null = True, on_delete=models.CASCADE)
    point_value =models.IntegerField(default = 1)#add ability to use this
#    def __str__(self):
#        return 
    class Meta:
        ordering = ['order']

class NewTest(models.Model):
    name = models.CharField(max_length = 50)
    problems = models.ManyToManyField(SortableProblem,blank = True, related_name = "new_test")
    types = models.ManyToManyField(Type,blank = True)
    created_date = models.DateTimeField(default = timezone.now)
    num_problems = models.IntegerField(default = 0)
    def __str__(self):
        return self.name

class UserType(models.Model):
    name = models.CharField(max_length = 20)
    allowed_types = models.ManyToManyField(Type,blank = True)
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    tests = models.ManyToManyField(Test, blank = True)
    usertests = models.ManyToManyField('UserTest', blank = True)
    archived_tests = models.ManyToManyField(Test,blank = True,related_name='userprofiles')
    folders = models.ManyToManyField(Folder,blank = True,related_name='userprofiles')
    students = models.ManyToManyField(User,blank = True,related_name='teacher_profiles')
    collaborators = models.ManyToManyField(User,blank = True, related_name = 'collaborators')
    allresponses = models.ManyToManyField(Responses,blank=True,related_name='userprofiles')
    responselog = models.ManyToManyField(UserResponse,blank = True)
    stickies = models.ManyToManyField(Sticky,blank = True)
    user_type = models.CharField(max_length=15,default = 'member')
    user_type_new = models.ForeignKey(UserType,null = True, blank = True,on_delete = models.SET_NULL)
    problem_groups = models.ManyToManyField(ProblemGroup,blank = True,related_name = 'userprofiles')
    owned_problem_groups = models.ManyToManyField(ProblemGroup,blank = True,related_name = 'owneruserprofiles')
    editable_problem_groups = models.ManyToManyField(ProblemGroup,blank = True,related_name = 'editoruserprofiles')
    readonly_problem_groups = models.ManyToManyField(ProblemGroup,blank = True,related_name = 'readeruserprofiles')
    archived_problem_groups = models.ManyToManyField(ProblemGroup,blank = True,related_name = 'a_userprofiles')
    archived_owned_problem_groups = models.ManyToManyField(ProblemGroup,blank = True,related_name = 'a_owneruserprofiles')
    archived_editable_problem_groups = models.ManyToManyField(ProblemGroup,blank = True,related_name = 'a_editoruserprofiles')
    archived_readonly_problem_groups = models.ManyToManyField(ProblemGroup,blank = True,related_name = 'a_readeruserprofiles')
#    handouts = models.ManyToManyField('handouts.Handout',blank = True,related_name = 'handouts')
    newtests = models.ManyToManyField(NewTest,blank=True,related_name = 'userprofiles')
    my_classes = models.ManyToManyField('teacher.Class',related_name = 'userprofiles')
    owned_my_classes = models.ManyToManyField('teacher.Class',related_name = 'owneruserprofiles')
    editable_my_classes = models.ManyToManyField('teacher.Class',related_name = 'editoruserprofiles')
    readonly_my_classes = models.ManyToManyField('teacher.Class',related_name = 'readeruserprofiles')
    my_published_classes = models.ManyToManyField('teacher.PublishedClass',related_name='userprofiles')
    my_TA_classes = models.ManyToManyField('teacher.PublishedClass',related_name = 'TA_userprofiles')
    time_zone = models.CharField(max_length = 100, blank = True, null=True, choices = TIMEZONES)
    def __str__(self):
        return self.user.username
    def add_problem_group(self,name=""):
        pg = ProblemGroup(name=name)
        pg.save()
        self.problem_groups.add(pg)
        self.save()
    def add_test(self,name,problems):
        t = Test(name=name)
        t.save()
        for p in problems:
            t.problems.add(p)
            t.types.add(p.type_new)
        t.save()
        self.tests.add(t)
        ut = UserTest(test =t,num_probs = t.problems.count(),num_correct = 0,userprof = self)
        ut.save()
        self.save()
        for p in t.problems.all(): 
            r = NewResponse(response = '', problem_label = p.label, problem = p, usertest =ut) 
            r.save() 

        
class UserTest(models.Model):
    userprof = models.ForeignKey(UserProfile,related_name = 'user_tests',null = True,on_delete=models.CASCADE)
    test = models.ForeignKey(Test, null = True, on_delete=models.CASCADE)
    newtest = models.ForeignKey(NewTest,null = True,on_delete=models.CASCADE)
    responses = models.ForeignKey(Responses,related_name = 'usertest',null = True, on_delete=models.SET_NULL)
    num_probs = models.IntegerField()
    num_correct = models.IntegerField(default = 0)
    show_answer_marks = models.BooleanField(default = 0)
    def __str__(self):
        return self.test.name

class NewResponse(models.Model):
    problem = models.ForeignKey(Problem,blank = True, null = True, on_delete=models.CASCADE)
    usertest = models.ForeignKey(UserTest,null=True,related_name = "newresponses", on_delete=models.CASCADE)
    response = models.CharField(max_length = 10,blank = True)
    problem_label = models.CharField(max_length = 20)
    modified_date = models.DateTimeField(default = timezone.now)
    attempted = models.BooleanField(default = 0)
    stickied = models.BooleanField(default = 0)
    order = models.IntegerField(default = 0)
    points = models.IntegerField(default = 0)
    point_value = models.IntegerField(default = 1)
    is_migrated = models.BooleanField(default = 0)
    correct = models.BooleanField(default = 0)
    def __str__(self):
        return self.problem_label+': '+self.response


class CollaboratorRequest(models.Model): 
    from_user = models.ForeignKey(UserProfile, null=True,related_name = "collab_invitations_from", on_delete=models.CASCADE)
    to_user = models.ForeignKey(UserProfile, null=True,related_name = "collab_invitations_to", on_delete=models.CASCADE)
#    message = models.CharField(max_length=200, blank=True) 
    created = models.DateTimeField(default = timezone.now, editable = False) 
    accepted = models.BooleanField(default = False) 

#    class Meta: 
#        verbose_name = _(u'friendship request') 
#        verbose_name_plural = _(u'friendship requests') 
#        unique_together = (('to_user', 'from_user'),) 

    def __str__(self): 
        return '{from_user} wants to collaborate with {to_user}'.format({'from_user': str(self.from_user), 'to_user': str(self.to_user)}) 

#    def accept(self): 
#        Friendship.objects.befriend(self.from_user, self.to_user) 
#        self.accepted = True 
#        self.save() 
#        signals.friendship_accepted.send(sender=self) 

#    def decline(self): 
#        signals.friendship_declined.send(sender=self, cancelled=False) 
#        self.delete() 

#    def cancel(self): 
#        signals.friendship_declined.send(sender=self, cancelled=True) 
#        self.delete() 

class AdvancedSearchPreset(models.Model):
    label = models.CharField(max_length=100,blank=True)
    types = models.ManyToManyField(Type,blank=True)
    rounds = models.ManyToManyField(Round,blank=True)
    def __str__(self):
        return self.label
    def actions(self):
        s = ''
        for t in self.types.all():
            s += 'T_'+str(t.pk)+'|'
        for r in self.rounds.all():
            s += 'R_'+str(r.pk)+'|'
        if len(s) > 0:
            return s[0:-1]
        return ''


def get_or_create_up(user):
    userprofile,boolcreated = UserProfile.objects.get_or_create(user = user)
    if boolcreated == False:
        userprofile.save()
    return userprofile
