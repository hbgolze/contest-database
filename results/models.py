from django.db import models

# Create your models here.

class Contest(models.Model):
    name = models.CharField(max_length = 100)
    def __str__(self):
        return self.name

class ContestYear(models.Model):
    year = models.CharField(max_length = 4)
    contest = models.ForeignKey(Contest,related_name="years")
    num_teams = models.IntegerField(default=0)
    max_team_score = models.IntegerField(default = 50)
    max_power_score = models.IntegerField(default = 50)
    max_relay_score = models.IntegerField(default = 25)
    def __str__(self):
        return self.year + str(self.contest)

#top score; averages; need total number of participants

class Team_format1(models.Model):
    year = models.ForeignKey(ContestYear,related_name="teams")
    name = models.CharField(max_length = 100)
    team_score = models.IntegerField(default = 0)
    power_score = models.IntegerField(default = 0)
#    relay1_score = models.IntegerField(default = 0)
#    relay2_score = models.IntegerField(default = 0)
    total_relay_score = models.IntegerField(default = 0)
    site = models.CharField(max_length = 1)
    division = models.CharField(max_length = 1)
    def __str__(self):
        return str(self.year) + ': ' + self.name

class IndivProb_format1(models.Model):
    year = models.ForeignKey(ContestYear,related_name="indiv_problems")
    problem_number = models.IntegerField(default=0)
    total_num_correct = models.IntegerField(default = 0)
    def percent_correct(self):
        return self.total_num_correct*1./self.year.num_teams/15
    def __str__(self):
        return str(self.year) + '-I'+str(self.problem_number)
    
class IndivProb_forteam_format1(models.Model):
    problem = models.ForeignKey(IndivProb_format1,related_name="team_results")
    team = models.ForeignKey(Team_format1,related_name="indiv_problems")
    num_correct = models.IntegerField(default = 0)
    def __str__(self):
        return str(self.problem) + ' (' + self.team.name + ')'

class RelayProb_format1(models.Model):
    year = models.ForeignKey(ContestYear,related_name="relay_problems")
    total_num_points = models.IntegerField(default = 0)
    problem_number = models.IntegerField(default=0)
    def percent_points(self):
        return self.total_num_points*1./self.year.num_teams/self.year.max_relay_score
    def __str__(self):
        return str(self.year)+'-R'+str(self.problem_number)

class RelayProb_forteam_format1(models.Model):
    problem = models.ForeignKey(RelayProb_format1,related_name="team_results",null = True)
    team = models.ForeignKey(Team_format1,related_name="relay_problems")
    num_points = models.IntegerField(default = 0)
    def __str__(self):
        return str(self.problem) + ' (' + self.team.name + ')'

