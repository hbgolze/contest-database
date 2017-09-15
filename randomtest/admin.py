from django.contrib import admin

# Register your models here.
from .models import Problem,UserProfile,Test,Tag,Type,Solution,Response,Responses,QuestionType,ProblemGroup,NewTag

admin.site.register(Problem)
admin.site.register(UserProfile)
admin.site.register(Test)
admin.site.register(Tag)
admin.site.register(NewTag)
admin.site.register(Type)
admin.site.register(QuestionType)
admin.site.register(Solution)
admin.site.register(Response)
admin.site.register(Responses)
admin.site.register(ProblemGroup)
