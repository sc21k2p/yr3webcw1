from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Professor(models.Model):
    professor_id = models.AutoField(primary_key=True)
    prof_code = models.CharField(max_length=200, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.first_name} {self.last_name} | Code: {self.prof_code}"
    
class Module(models.Model):
    module_id = models.AutoField(primary_key=True)
    module_name = models.CharField(max_length=200)
    module_code = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f"{self.module_name} | Module Code: {self.module_code}"

class ModuleInstance(models.Model):
    module_instance_id = models.AutoField(primary_key=True)
    module = models.ForeignKey(Module, on_delete=models.PROTECT)
    professors = models.ManyToManyField('Professor')
    academic_year = models.IntegerField()
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)])

    def __str__(self):
        return f"Module: {self.module} | Professor: {self.professors} | Academic Year: {self.academic_year} | Semester: {self.semester}"
    
    class Meta:
        unique_together = ('module', 'academic_year', 'semester')

class StudentProfessorRating(models.Model):
    student_prof_rating_id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(User, on_delete=models.PROTECT)
    professor_id = models.ForeignKey(Professor, on_delete=models.PROTECT)
    module_instance_id = models.ForeignKey(ModuleInstance, on_delete=models.PROTECT)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return f"{self.student_id} | Professor: {self.professor_id} | Module Details: {self.module_instance_id} | Rating: {self.rating}"
    
    class Meta:
        unique_together = ('student_id', 'professor_id', 'module_instance_id')
