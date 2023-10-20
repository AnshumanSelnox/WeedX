from django.urls import path
from .views import *
    
urlpatterns = [  
    path('Add-Employee/', AddEmployee.as_view()),
    path('Get-Employee/', GetEmployee.as_view()),
    path('update-Employee/<int:id>', UpdateEmployee.as_view()),
    path('delete-Employee/<int:id>', DeleteEmployee.as_view()),
]
