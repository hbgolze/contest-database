from django.contrib import admin

# Register your models here.
from .models import Drill,Category,YearFolder,DrillTask, DrillProblemSolution, DrillProblem, DrillProfile,DrillRecord, DrillRecordProblem, DrillAssignment

admin.site.register(Drill)
admin.site.register(Category)
admin.site.register(YearFolder)
admin.site.register(DrillTask)
admin.site.register(DrillProblem)
admin.site.register(DrillProblemSolution)
admin.site.register(DrillProfile)
admin.site.register(DrillRecord)
admin.site.register(DrillRecordProblem)
admin.site.register(DrillAssignment)
