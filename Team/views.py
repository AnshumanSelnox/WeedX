from rest_framework.views import APIView
from AdminPanel.tokens import create_jwt_pair_for_user
from AdminPanel.models import *
from AdminPanel.serializer import * 
from rest_framework import status,generics,permissions
from rest_framework.response import Response
from .serializer import *
# Create your views here.
class RegisterAPI(generics.GenericAPIView):
    serializer_class =RegisterSerializer

    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get("username")
            email = request.data.get("email")
            password = request.data.get("password")
            if username:
                if email:
                    if password:
                        serializer = RegisterUserSerializer(data=request.data)
                        user = User.objects.filter(email=email)
                        username = User.objects.filter(username=username)
                        if user.exists():
                            if username.exists():
                                return Response({"username": "Username is already Registered"},status=status.HTTP_400_BAD_REQUEST)
                            else :
                                return Response({"email": "Email is already Registered"},status=status.HTTP_400_BAD_REQUEST)
                        else:
                            if serializer.is_valid():
                                user = serializer.save()
                                return Response({"message": "User add Successfully"},status=status.HTTP_200_OK)
                            else:
                                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response("Enter the Valid password",status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response("Enter the Valid email",status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Enter the Valid User-name",status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


