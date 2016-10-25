from django.contrib import admin

# Register your models here.
from .models import Problem,UserProfile,Test,Tag,Type

admin.site.register(Problem)
admin.site.register(UserProfile)
admin.site.register(Test)
admin.site.register(Tag)
admin.site.register(Type)
