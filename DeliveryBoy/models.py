from django.db import models
from AdminPanel.models import *

class Employee(models.Model):
    FirstName=models.CharField(max_length=5000)
    LastName=models.CharField(max_length=5000)
    DOB=models.DateField()
    Study=models.CharField(max_length=20)
    StartDate=models.DateField()
    EndDate=models.DateField()
    CurrentSalary=models.IntegerField()
    Description=RichTextField()
