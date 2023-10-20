from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .serializer import *
from .models import *


class GetEmployee(APIView):
    def get(self, request, format=None):
        
        try:
            User= Employee.objects.select_related().all()
            serialize = Serializer_Employee(User, many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddEmployee(APIView):
    def post(self, request):
        try:
            serializer = Serializer_Employee(data=request.data, partial=True)
            if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateEmployee(APIView):
    def post(self, request, id=None):
        try:
            User = Employee.objects.get(id=id)
            serializer = Serializer_Employee(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.username)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteEmployee(APIView):

    def delete(self, request, id=None):
        try:
            User = get_object_or_404(Employee, id=id)
            User.delete()
            return Response({"status": "success", "data": "Deleted"})
        except Exception as e:
            return Response({'error' : str(e)},status=500)

