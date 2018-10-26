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
    class Meta:
        ordering = ['year']
    def __str__(self):
        return self.year + str(self.contest)
    def update_ranks(self):
        teams = self.teams.all()
        results = sorted(teams,key = lambda x:(-x.total_score,-x.total_team_score,-x.total_relay_score,-x.total_indiv_score))
        if len(results) > 0:
            r = results[0]
            r.overall_rank = 1
            r.save()
            current_leader = (-r.total_score,-r.total_team_score,-r.total_relay_score,-r.total_indiv_score)
            rank = 1
            for i in range(1,len(results)):
                r = results[i]
                r_tuple = (-r.total_score,-r.total_team_score,-r.total_relay_score,-r.total_indiv_score)
                if r_tuple > current_leader:
                    r.overall_rank = i+1
                    r.save()
                    rank = i+1
                    current_leader = r_tuple
                else:
                    r.overall_rank = rank
                    r.save()
        divs = []
        for t in teams:
            divs.append(t.division)
        divs = list(set(divs))
        for D in divs:
            div_teams = teams.filter(division = D)
            div_results = sorted(div_teams,key = lambda x:(-x.total_score,-x.total_team_score,-x.total_relay_score,-x.total_indiv_score))
            if len(div_results) > 0:
                r = div_results[0]
                r.divisional_rank = 1
                r.save()
                current_leader = (-r.total_score,-r.total_team_score,-r.total_relay_score,-r.total_indiv_score)
                rank = 1
                for i in range(1,len(div_results)):
                    r = div_results[i]
                    r_tuple = (-r.total_score,-r.total_team_score,-r.total_relay_score,-r.total_indiv_score)
                    if r_tuple > current_leader:
                        r.divisional_rank = i+1
                        r.save()
                        rank = i+1
                        current_leader = r_tuple
                    else:
                        r.divisional_rank = rank
                        r.save()

class Site(models.Model):
    letter = models.CharField(max_length = 1)
    label = models.CharField(max_length = 100)
    class Meta:
        ordering = ['letter']
    def __str__(self):
        return self.label
#top score; averages; need total number of participants

class Organization(models.Model):
    name = models.CharField(max_length = 100)
    contest = models.ForeignKey(Contest,related_name = "organizations",null=True)
    num_years = models.IntegerField(default = 0)
    last_year = models.CharField(max_length = 4,default = "")
    def __str__(self):
        return self.name
    def update(self):
        Y=[]
        for t in self.teams.all():
            Y.append(t.year.year)
        Y = list(set(Y))
        Y.sort()
        self.num_years = len(Y)
        self.last_year = Y[-1]
        self.save()

class Team_format1(models.Model):
    year = models.ForeignKey(ContestYear,related_name="teams")
    name = models.CharField(max_length = 100)
    total_team_score = models.IntegerField(default = 0)
    team_score = models.IntegerField(default = 0)
    power_score = models.IntegerField(default = 0)
    total_indiv_score = models.IntegerField(default = 0)
    total_relay_score = models.IntegerField(default = 0)
    total_score = models.IntegerField(default = 0)
    site = models.CharField(max_length = 1)
    new_site = models.ForeignKey(Site,related_name="teams",null=True)
    division = models.CharField(max_length = 1)
    organization = models.ForeignKey(Organization,related_name="teams",null=True)
    overall_rank = models.IntegerField(default = 0)
    divisional_rank = models.IntegerField(default = 0)
    award = models.CharField(max_length = 5,default = '')
    class Meta:
        ordering = ['overall_rank']
    def __str__(self):
        return str(self.year) + ': ' + self.name
    def update(self):
        self.total_team_score = self.team_score + self.power_score
        t = 0
        for i in self.indiv_problems.all():
            t += i.num_correct
        self.total_indiv_score = t
        t=0
        for r in self.relay_problems.all():
            t += r.num_points
        self.total_relay_score = t
        self.total_score = self.total_team_score + self.total_indiv_score + self.total_relay_score
        self.save()
class IndivProb_format1(models.Model):
    prefix = models.CharField(max_length = 16,default ="I")
    year = models.ForeignKey(ContestYear,related_name="indiv_problems")
    problem_number = models.IntegerField(default=0)
    total_num_correct = models.IntegerField(default = 0)
    class Meta:
        ordering = ['problem_number']
    def percent_correct(self):
        return self.total_num_correct*1./self.year.num_teams/15
    def __str__(self):
        return str(self.year) + '-'+self.prefix+str(self.problem_number)
    
class IndivProb_forteam_format1(models.Model):
    problem = models.ForeignKey(IndivProb_format1,related_name="team_results")
    team = models.ForeignKey(Team_format1,related_name="indiv_problems")
    num_correct = models.IntegerField(default = 0)
    problem_number = models.IntegerField(default=0)
    class Meta:
        ordering = ['problem_number']
    def __str__(self):
        return str(self.problem) + ' (' + self.team.name + ')'

class RelayProb_format1(models.Model):
    year = models.ForeignKey(ContestYear,related_name="relay_problems")
    total_num_points = models.IntegerField(default = 0)
    problem_number = models.IntegerField(default=0)
    class Meta:
        ordering = ['problem_number']
    def percent_points(self):
        return self.total_num_points*1./self.year.num_teams/self.year.max_relay_score
    def __str__(self):
        return str(self.year)+'-R'+str(self.problem_number)

class RelayProb_forteam_format1(models.Model):
    problem = models.ForeignKey(RelayProb_format1,related_name="team_results",null = True)
    team = models.ForeignKey(Team_format1,related_name="relay_problems")
    num_points = models.IntegerField(default = 0)
    problem_number = models.IntegerField(default=0)
    class Meta:
        ordering = ['problem_number']
    def __str__(self):
        return str(self.problem) + ' (' + self.team.name + ')'

