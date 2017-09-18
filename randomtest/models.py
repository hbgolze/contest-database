from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry


# Create your models here.

class Dropboxurl(models.Model):
    url=models.CharField(max_length=100)
    def __str__(self):
        return self.url

class Tag(models.Model):
    tag = models.CharField(max_length=50)
    def __str__(self):
        return self.tag

class NewTag(models.Model):
    tag = models.CharField(max_length=50)
    label = models.CharField(max_length=50)
    level = models.IntegerField(default=0)
    parent = models.ForeignKey("self",null=True,related_name="children")
    def __str__(self):
        if self.level > 1:
            return str(self.parent)+'>'+self.label
        return self.label

    class Meta:
        ordering = ['tag']

class Type(models.Model):
    type = models.CharField(max_length=20)
    label = models.CharField(max_length=20,blank=True)
    top_index = models.IntegerField(default=0)
    is_contest = models.BooleanField(default=1)
    default_question_type = models.CharField(max_length=4,default = 'pf')
    readable_label_pre_form = models.CharField(max_length=20,default = '')
    readable_label_post_form = models.CharField(max_length=20,default = '')
    def __str__(self):
        return self.label
    class Meta:
        ordering = ['label']
class ProblemApproval(models.Model):
    approval_user = models.ForeignKey(User,blank=True,null=True)
    APPROVAL_CHOICES = (
        ('AP', 'Approved'),
        ('MN', 'Approved Subject to Minor Revision'),
        ('MJ', 'Needs Major Revision'),
        ('DE', 'Propose For Deletion'),
        )
    approval_status = models.CharField(max_length = 2,choices=APPROVAL_CHOICES,blank=False,default='MJ')
    author_name = models.CharField(max_length=50,blank=True)

class QuestionType(models.Model):#multiple choice; short answer; proof
    question_type = models.CharField(max_length=20)
    def __str__(self):
        return self.question_type

class Solution(models.Model):
    solution_text = models.TextField()
    display_solution_text = models.TextField(blank=True)
    solution_number = models.IntegerField(default=1)
    problem_label = models.CharField(max_length=20,blank=True)
    tags = models.ManyToManyField(Tag,blank=True)
    authors = models.ManyToManyField(User,blank=True)
    created_date = models.DateTimeField(default = timezone.now)
    modified_date = models.DateTimeField(default = timezone.now)
    def __str__(self):
        return self.problem_label+' sol '+str(self.solution_number)+str(self.authors.all())


class Sticky(models.Model):
    problem_label = models.CharField(max_length=20)
    sticky_date = models.DateTimeField(default = timezone.now)
    test_pk = models.CharField(max_length = 15)
    test_label = models.CharField(max_length=50,blank=True)
    def __str__(self):
        return self.problem_label

class Comment(models.Model):
    comment_text = models.TextField()
    problem_label = models.CharField(max_length=20,blank=True)
    comment_number = models.IntegerField(default=1)
    author = models.ForeignKey(User,blank=True)
    author_name = models.CharField(max_length=50,blank=True)
    created_date = models.DateTimeField(default = timezone.now)
    def __str__(self):
        return self.problem_label+' comment '+str(self.created_date)+', '+str(self.author)

class Problem(models.Model):
    problem_number = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag,related_name='problems',blank=True)#related name is used correctly here...
    newtags = models.ManyToManyField(NewTag,related_name='problems',blank=True)
#    tags = models.ManyToManyField(Tag,blank=True)
    type_new = models.ForeignKey(Type,related_name='problems',blank=True,null=True)#new(should replace)
    question_type_new = models.ForeignKey(QuestionType,related_name='question_type_new',blank=True,null=True)#new(should replace), then replace again.
    year = models.IntegerField(default=2016)
    difficulty = models.IntegerField(blank=True,null=True)
    types = models.ManyToManyField(Type)#allows for  multiple types, should be replaced
    answer = models.CharField(max_length=20,blank=True)#should be replaced
    latexanswer = models.CharField(max_length=100,blank=True)#should be replaced
    label = models.CharField(max_length=20)
    readable_label = models.CharField(max_length=20,blank=True)
    latex_label = models.CharField(max_length=20,blank=True)
    problem_text = models.TextField(blank=True)
    mc_problem_text = models.TextField(blank=True)
    display_problem_text = models.TextField(blank=True)
    display_mc_problem_text = models.TextField(blank=True)
    answer_choices = models.TextField(blank=True)#should be replaced
    answer_A = models.CharField(max_length=500,blank=True)
    answer_B = models.CharField(max_length=500,blank=True)
    answer_C = models.CharField(max_length=500,blank=True)
    answer_D = models.CharField(max_length=500,blank=True)
    answer_E = models.CharField(max_length=500,blank=True)
    mc_answer = models.CharField(max_length=1,blank=True)
    sa_answer = models.CharField(max_length=20,blank=True)
    form_letter = models.CharField(max_length=2,blank=True)
    test_label = models.CharField(max_length=20,blank=True)
    question_type = models.ManyToManyField(QuestionType)
    solutions = models.ManyToManyField(Solution,blank=True)
    top_solution_number = models.IntegerField(blank=True,null=True)
    author = models.ForeignKey(User,related_name='author',blank=True,null=True)
    author_name = models.CharField(max_length=50,blank=True)
    created_date = models.DateTimeField(default = timezone.now)
    approval_status = models.BooleanField(default=0)#deprecated
    approval_user = models.ForeignKey(User,related_name='approval_user',blank=True,null=True)#deprecated
    comments = models.ManyToManyField(Comment,blank=True)
    approvals = models.ManyToManyField(ProblemApproval,blank=True)
    duplicate_problems = models.ManyToManyField("self",blank=True)
    problem_number_prefix = models.CharField(max_length=5,default="")
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

class ProofResponse(models.Model):
    problem = models.ForeignKey(Problem)
    proof = models.TextField(blank = True)
    problem_label = models.CharField(max_length=20)
    modified_date = models.DateTimeField(default = timezone.now)
    points_awarded = models.IntegerField(default = 0)
    attempted = models.BooleanField(default = 0)
    is_graded = models.BooleanField(default = 0)
    def __str__(self):
        return self.problem_label
    
class Response(models.Model):
    problem = models.ForeignKey(Problem,blank=True, null=True)
    response = models.CharField(max_length=10,blank=True)
    problem_label = models.CharField(max_length=20)
    modified_date = models.DateTimeField(default = timezone.now)
    attempted = models.BooleanField(default = 0)
    stickied = models.BooleanField(default = 0)
    def __str__(self):
        return self.response



class Test(models.Model):
    name = models.CharField(max_length=50)#Perhaps use a default naming scheme
    problems = models.ManyToManyField(Problem)
    types = models.ManyToManyField(Type,blank=True)
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
    def refresh_types(self):
        t=list(self.types.all())
        for i in t:
            self.types.remove(i)
        P=list(self.problems.all())
        for i in P:
            typs=list(i.types.all())
            for j in typs:
                if self.types.filter(type=j).count()==0:
                    self.types.add(j)
        self.save()
        
class TestCollection(models.Model):
    name=models.CharField(max_length=50)
    tests=models.ManyToManyField(Test)
    def __str__(self):
        return self.name

class ProblemGroup(models.Model):
    name = models.CharField(max_length=50)#Perhaps use a default naming scheme
    problems = models.ManyToManyField(Problem)
    created_date = models.DateTimeField(default = timezone.now)
    is_shared = models.BooleanField(default = 0)
    def __str__(self):
        return self.name

class Folder(models.Model):
    name=models.CharField(max_length=50)
    tests=models.ManyToManyField(Test)
    def __str__(self):
        return self.name

class TestTimeStamp(models.Model):
    date_added=models.DateTimeField(default = timezone.now)
    test_pk=models.CharField(max_length=15)

class Responses(models.Model):
    test = models.ForeignKey(Test,on_delete=models.CASCADE)
    responses = models.ManyToManyField(Response,blank=True)
    num_problems_correct = models.IntegerField(blank=True,null=True)
    show_answer_marks=models.BooleanField(default=0)
    modified_date = models.DateTimeField(default = timezone.now)
    def __str__(self):
        return self.test.name

#Equivalent to Response, except it is used to hold items for the User Response queue (also point value added)
class UserResponse(models.Model):
    test_label = models.CharField(max_length=50,blank=True)
    response = models.CharField(max_length=10,blank=True)
    problem_label = models.CharField(max_length=30)
    modified_date = models.DateTimeField(default = timezone.now)
    correct = models.BooleanField(default = 0)
    test_pk = models.CharField(max_length = 15,blank = True)
    point_value = models.IntegerField(default=0)


class SortableProblem(models.Model):
    newtest_pk = models.CharField(max_length = 15)
    order = models.IntegerField(default = 0)
    problem = models.ForeignKey(Problem, blank=True,null=True)
    point_value =models.IntegerField(default = 1)#add ability to use this
#    def __str__(self):
#        return 
#in general, we would want this to be deleted if Problem is deleted, but not the other way around.
    class Meta:
        ordering = ['order']

class NewTest(models.Model):
    name = models.CharField(max_length=50)
    problems = models.ManyToManyField(SortableProblem,blank=True)
    types = models.ManyToManyField(Type,blank=True, related_name='types')
    created_date = models.DateTimeField(default = timezone.now)
    num_problems = models.IntegerField(default=0)
    def __str__(self):
        return self.name

class UserType(models.Model):
    name = models.CharField(max_length=20)
    allowed_types = models.ManyToManyField(Type,blank=True)
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)
    tests = models.ManyToManyField(Test, blank=True)
    usertests = models.ManyToManyField('UserTest', blank=True)
    timestamps = models.ManyToManyField(TestTimeStamp,blank=True)
    archived_tests = models.ManyToManyField(Test,blank = True,related_name='archived_tests')
    folders = models.ManyToManyField(Folder,blank = True,related_name='folders')
    students = models.ManyToManyField(User,blank = True,related_name='students')
    allresponses = models.ManyToManyField(Responses,blank=True,related_name='user_profile')
    responselog = models.ManyToManyField(UserResponse,blank=True)
    stickies = models.ManyToManyField(Sticky,blank=True)
    user_type = models.CharField(max_length=15,default='member')
    user_type_new = models.ForeignKey(UserType,null=True, blank=True,on_delete=models.SET_NULL)
    problem_groups = models.ManyToManyField(ProblemGroup,blank = True,related_name = 'problem_groups')
    handouts = models.ManyToManyField('handouts.Handout',blank = True,related_name = 'handouts')
    newtests = models.ManyToManyField(NewTest,blank=True,related_name='newtests')
    def __str__(self):
        return self.user.username


class UserTest(models.Model):
    userprof = models.ForeignKey(UserProfile,related_name='user_tests',null=True)
    test = models.ForeignKey(Test)
    responses = models.ForeignKey(Responses,related_name='usertest',null = True)
    num_probs = models.IntegerField()
    num_correct = models.IntegerField(default=0)
    show_answer_marks=models.BooleanField(default=0)
    def __str__(self):
        return self.test.name

class NewResponse(models.Model):
    problem = models.ForeignKey(Problem,blank=True, null=True)
    usertest = models.ForeignKey(UserTest,related_name = "newresponses")
    response = models.CharField(max_length=10,blank=True)
    problem_label = models.CharField(max_length=20)
    modified_date = models.DateTimeField(default = timezone.now)
    attempted = models.BooleanField(default = 0)
    stickied = models.BooleanField(default = 0)
    def __str__(self):
        return self.problem_label+': '+self.response

def get_or_create_up(user):
    userprofile,boolcreated=UserProfile.objects.get_or_create(user=user)
    if boolcreated==False:
        userprofile.save()
    return userprofile
