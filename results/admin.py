from django.contrib import admin

# Register your models here.
from .models import Contest,ContestYear,Team_format1,IndivProb_format1,IndivProb_forteam_format1,RelayProb_format1,RelayProb_forteam_format1

admin.site.register(Contest)
admin.site.register(ContestYear)
admin.site.register(Team_format1)
admin.site.register(IndivProb_format1)
admin.site.register(IndivProb_forteam_format1)
admin.site.register(RelayProb_format1)
admin.site.register(RelayProb_forteam_format1)
