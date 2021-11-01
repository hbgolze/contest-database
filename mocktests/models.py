from django.db import models

from randomtest.models import Problem,UserProfile
# Create your models here.

class MockTestFolder(models.Model):
    name = models.CharField(max_length = 100)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']
        
class MockTest(models.Model):
    name = models.CharField(max_length = 100)
    folder = models.ForeignKey(MockTestFolder,blank=True,null=True,related_name = "mock_tests", on_delete = models.CASCADE)
    points = models.FloatField(default = 0)
    def __str__(self):
        return self.name
    def add_to_user(self,userprofile):
        user_mock_test = UserMockTest(userprofile=userprofile,mock_test =self)
        user_mock_test.save()
        for mt_seg in self.mock_test_segments.all():
            user_mock_test_segment = UserMockTestSegment(user_mock_test = user_mock_test,mock_test_segment = mt_seg,order = mt_seg.order)
            user_mock_test_segment.save()
            for mt_prob in mt_seg.problems.all():
                user_mock_problem = UserMockProblem(user_mocktest_segment = user_mock_test_segment,mocktest_problem=mt_prob,order = mt_prob.order)
                user_mock_problem.save()
        return user_mock_test
    class Meta:
        ordering = ['name']
    
class MockTestSegment(models.Model):
    name = models.CharField(max_length = 100)
    mock_test = models.ForeignKey(MockTest,blank=True,null=True,related_name = 'mock_test_segments',on_delete = models.CASCADE)
    segment_type = models.CharField(max_length = 2)#PR for problems or BR for break
    instructions = models.CharField(max_length = 1000)
    time_limit = models.DurationField(null=True)
    order = models.IntegerField(default = 0)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['order']

class MockTestProblem(models.Model):
    problem = models.ForeignKey(Problem,blank = True, null = True, on_delete = models.CASCADE)
    order = models.IntegerField(default = 0)
    mocktest_segment = models.ForeignKey(MockTestSegment,blank = True, null = True, related_name="problems", on_delete = models.CASCADE)
    point_value = models.FloatField(default = 1)
    blank_point_value = models.FloatField(default = 0)
    answer_type = models.CharField(max_length = 3)#?
    units = models.CharField(max_length = 50)#?
    class Meta:
        ordering = ['order']
    def __str__(self):
        return self.problem.label

class UserMockTest(models.Model):
    userprofile = models.ForeignKey(UserProfile,blank=True,null=True,related_name='mock_tests',on_delete=models.CASCADE)
    mock_test = models.ForeignKey(MockTest,blank = True, null = True, on_delete = models.CASCADE)
    points = models.FloatField(default = 0)
    status = models.IntegerField(default = 0)#0 = not taken, 1 = in progress, 2 = finished
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    current_segment = models.IntegerField(default = 0)
    allow_solutions = models.BooleanField(default = 0)
    class Meta:
        ordering = ['end_time']
    def __str__(self):
        return self.mock_test.name
    def grade(self):
        points = 0
        for s in self.segments.all():
            points +=s.grade()
        self.points = points
        self.save()

class UserMockTestSegment(models.Model):
    user_mock_test = models.ForeignKey(UserMockTest,blank = True, null = True, related_name='segments',on_delete = models.CASCADE)
    mock_test_segment = models.ForeignKey(MockTestSegment,blank = True, null = True, on_delete = models.CASCADE)
    points = models.FloatField(default = 0)
    status = models.IntegerField(default = 0)#0 = not taken, 1 = in progress, 2 = finished
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null = True)
    order = models.IntegerField(default=0)
    class Meta:
        ordering = ['order']
    def __str__(self):
        return self.mock_test_segment.name
    def grade(self):
        points = 0
        for p in self.problems.all():
            points += p.grade()
        self.points = points
        self.save()
        return self.points
        
class UserMockProblem(models.Model):
    user_mocktest_segment = models.ForeignKey(UserMockTestSegment,blank = True, null = True, related_name = 'problems',on_delete = models.CASCADE)
    mocktest_problem = models.ForeignKey(MockTestProblem,blank = True,null=True,on_delete = models.CASCADE)
    answer_a = models.CharField(default="",max_length=50)
    answer_b = models.CharField(default="",max_length=50)
    answer_c = models.CharField(default="",max_length=50)
    correct = models.IntegerField(default=1)#0=incorrect,1=blank,2=correct
    points = models.FloatField(default=0)
    order = models.IntegerField(default=0)
    def __str__(self):
        return self.mocktest_problem.problem.label
    class Meta:
        ordering = ['order']
    def grade(self):
        self.correct = 0
        if self.answer_a == '' and self.answer_b == '' and self.answer_c == '':
            self.correct = 1
            self.points = self.mocktest_problem.blank_point_value
        else:
            if self.mocktest_problem.problem.question_type_new.question_type == 'multiple choice':
                if self.answer_a == self.mocktest_problem.problem.mc_answer:
                    self.correct = 2
                    self.points = self.mocktest_problem.point_value
            else:
                for acc_ans in self.mocktest_problem.problem.accepted_answers.all():
                    if self.answer_a == acc_ans.answer_a and self.answer_b == acc_ans.answer_b and self.answer_c == acc_ans.answer_c:
                        self.correct = 2
                        self.points = self.mocktest_problem.point_value
        self.save()
        return self.points
