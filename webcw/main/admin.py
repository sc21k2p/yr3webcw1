from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Professor, Module, ModuleInstance, StudentProfessorRating

# Register your models here.
# This is for user admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Professor)
admin.site.register(Module)
admin.site.register(ModuleInstance)
admin.site.register(StudentProfessorRating)