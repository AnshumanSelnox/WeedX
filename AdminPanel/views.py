import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import *
from django.shortcuts import get_object_or_404
import pandas as pd
import uuid
from .serializer import *
from rest_framework import generics, permissions
from rest_framework.response import Response
from .tokens import create_jwt_pair_for_user
from rest_framework import  status
from Ecommerce.settings import EMAIL_HOST,EMAIL_HOST_USER,EMAIL_HOST_PASSWORD,EMAIL_PORT
import smtplib
import random
from UserPanel.serializer import *
# Class based view to Get User Details using Token Authentication
def send_OneToOneMail(from_email='',to_emails=''):
    Otp=random.randint(1000, 9999)
    server=smtplib.SMTP(EMAIL_HOST,EMAIL_PORT)
    server.ehlo()
    server.starttls()
    server.login(EMAIL_HOST_USER,EMAIL_HOST_PASSWORD)
    Subject="Selnox"
    Text="Your One Time Password is "  + str(Otp)
    
    msg='Subject: {}\n\n{}'.format(Subject, Text)
    server.sendmail(from_email,to_emails,msg)
    user=User.objects.get(email=to_emails)
    user.otp=Otp
    user.save()
    server.quit()

class VerifyOtpLogin(APIView):
    permission_classes=(permissions.AllowAny,)
    def post(self,request):
        try:
            data=request.data

            email=request.data.get("email")
            
            otp=request.data.get("OTP")
            
            
            user= User.objects.filter(email=email).first()
            if user.user_type=="Admin" or "Co-Owner" or "Content Manager Editor" or "vendor managent" or "store managment":
                if user.otp != int(otp):
                    return Response({
                        'message':'Something goes wrong',
                        'data':'invalid Otp'
                    },status=status.HTTP_400_BAD_REQUEST)
                user= User.objects.get(email=email)  
                if user is not None:

                    tokens = create_jwt_pair_for_user(user)

                    response = {"message": "Login Successfull", "tokens": tokens,"UserType":user.user_type}
                    return Response(data=response, status=status.HTTP_200_OK)

                else:
                    return Response(data={"message": "Invalid email or password"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response ("Not Authorised")
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    def get(self, request):
        try:
            content = {"user": str(request.user), "auth": str(request.auth)}

            return Response(data=content, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
class ResetPasswordAPI(APIView):
    serializer_class = ChangePasswordSerializer
    model = User

    def get_object(self, queryset=None):
        try:
            obj = self.request.user
            return obj
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            serializer = ChangePasswordSerializer(data=request.data)
            if serializer.is_valid():
                email=serializer.validated_data['email']
                send_OneToOneMail(from_email='smtpselnox@gmail.com',to_emails=email)
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'mail sent successfully',
                    'data': {"Otp_Sent_To":email}
                }

                return Response(response)
            else:
                return Response({"message":"Something Goes Wrong"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
class VerifyOtpResetPassword(APIView):
    def get_object(self, queryset=None):
        
        obj = self.request.user
        return obj


    def post(self,request):
        try:
            self.object = self.get_object()
            data=request.data
            serializer=PasswordReseetSerializer(data=data)
            if serializer.is_valid():
                email=serializer.validated_data['email']
                new_password=serializer.validated_data['new_password']
                otp=serializer.validated_data['OTP']
            
                user=User.objects.filter(email=email)
                if not user.exists():
                    return Response({
                        'message':'Something goes wrong',
                        'data':'invalid Email'
                    },status=status.HTTP_400_BAD_REQUEST)
                if user[0].otp != otp:
                    return Response({
                        'message':'Something goes wrong',
                        'data':'invalid Otp'
                    },status=status.HTTP_400_BAD_REQUEST)
                if len(new_password)>5 :
                    self.object.set_password(serializer.data.get("new_password"))
                    self.object.save()

                    return Response({
                            'message':'Password is Update',
                        },status=status.HTTP_200_OK)
                else:
                    return Response({
                                'message':'Password must be Strong',
                            },status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginAPI(APIView):
    permission_classes=(permissions.AllowAny,)
    def post(self,request,format=None):
        try:
            username=request.data.get("username")
            email=request.data.get("email")
            password=request.data.get("password")
            if username:
                if email:
                    if password:
                        serializer=LoginSerializer(data=request.data)
                        if serializer.is_valid():
                            # self.object.check_password(Admin.data.get("password"))
                            
                            email=serializer.validated_data['email']
                            send_OneToOneMail(from_email='smtpselnox@gmail.com',to_emails=email)
                            return Response({
                                        'message':'Email sent',
                                        'data':{"Otp_Sent_to":email}
                                    },status=status.HTTP_200_OK)
                        else:
                            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"error":"Enter the valid Password"},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error":"Enter the valid Email"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error":"Enter the valid Username"},status=status.HTTP_400_BAD_REQUEST)
                        
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Get User API
class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = UserSerializer

    def get_object(self):
        try:
            return self.request.user
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class RegisterAPI(generics.GenericAPIView):
    serializer_class =RegisterSerializer

    def post(self,request,*args,**kwargs):
        try:
            serializer=self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user=serializer.save()
            
        
            return Response({
            "user":UserSerializer(user,context=self.get_serializer_context()).data,
            # "token":AuthToken.objects.create(user)[1]
            })
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Category Api
class GetCategories(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner':
                category = Category.objects.select_related().all()
                serialize = Serializer_Category(category, many=True)
                return Response(serialize.data)
            
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
    
class AddCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner':
           
                serializer = Serializer_Category(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data},status=status.HTTP_200_OK)
                else:
                    return Response({ "error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner':
            
            
                User = Category.objects.get(id=id)
                serializer = Serializer_Category(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteCategory(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = get_object_or_404(Category, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

#Sub Category Api
class GetSubCategories(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner':
                User = SubCategory.objects.select_related().all()
                serialize = Serializer_SubCategory(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddSubCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner':

                serializer = Serializer_SubCategory(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
              
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateSubCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner':
                User = SubCategory.objects.get(id=id)
                serializer = Serializer_SubCategory(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteSubCategory(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' :
                User = get_object_or_404(SubCategory, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

#Country
class GetCountry(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = Countries.objects.select_related().all()
                serialize = Serializer_Country(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddCountry(APIView):
    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                serializer = Serializer_Country(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateCountry(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a== 'Content Manager Editor':

                User = Countries.objects.get(id=id)
                serializer = Serializer_Country(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteCountry(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = get_object_or_404(Countries, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

#States
class GetStates(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = States.objects.select_related().all()
                serialize = Serializer_States(User, many=True)
                
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddStates(APIView):

    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a== 'Content Manager Editor':
                serializer = Serializer_States(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"status": "error", "data": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateStates(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
            
                User = States.objects.get(id=id)
                serializer = Serializer_States(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"status": "error", "data": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteStates(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' :
                User = get_object_or_404(States, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

#Cities 
class GetCities(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = Cities.objects.select_related().all()
                serialize = Serializer_Cities(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddCities(APIView):

    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                serializer = Serializer_Cities(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateCities(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = Cities.objects.get(id=id)
                serializer = Serializer_Cities(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({ "error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteCities(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
            
                User = get_object_or_404(Cities, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
#Brand
class GetBrand(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner':
                User = Brand.objects.select_related().all()
                serialize = Serializer_Brand(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddBrand(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner':
                serializer = Serializer_Brand(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        
                        
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateBrand(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner':

                User = Brand.objects.get(id=id)
                serializer = Serializer_Brand(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
                    
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteBrand(APIView): 
    permission_classes = [IsAuthenticated]
    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = get_object_or_404(Brand, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

#Salestax
class GetSalesTax(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = Salestaxes.objects.select_related().all()
            serialize = Serializer_Salestax(User, many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddSalesTax(APIView): 
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:

            serializer = Serializer_Salestax(data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
                    
                
                    
                    
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateSalesTax(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            
            User = Salestaxes.objects.get(id=id)
            serializer = Serializer_Salestax(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.username)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
                    
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteSalesTax(APIView): 
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, id=None):
        try:
            User = get_object_or_404(Salestaxes, id=id)
            User.delete()
            return Response({"status": "success", "data": "Deleted"})
        except Exception as e:
            return Response({'error' : str(e)},status=500)

#Esteemedtax
class GetEsteemedTax(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = Estemeedtaxes.objects.select_related().all()
            serialize = Serializer_Esteemedtax(User, many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddEsteemedTax(APIView): 
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = Serializer_Esteemedtax(data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateEsteemedTax(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            
            User = Estemeedtaxes.objects.get(id=id)
            serializer = Serializer_Esteemedtax(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.username)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
                    
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteEsteemedTax(APIView): 
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, id=None):
        try:
            User = get_object_or_404(Estemeedtaxes, id=id)
            User.delete()
            return Response({"status": "success", "data": "Deleted"})
        except Exception as e:
            return Response({'error' : str(e)},status=500)    

#Replicate or Duplicate Data
#Replicate or Duplicate Data
class Replicate_data(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id=None):
        try:
            User = Product.objects.get(id=id)
            serializer = Serializer_Product(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)          
        
#Stores 
class GetStores(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='store managment':
                User = Stores.objects.select_related().all()
                serialize = Serializer_Store(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddStores(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='store managment':

                serializer = Serializer_Store(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
                            
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateStores(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='store managment':

                User = Stores.objects.get(id=id)
                serializer = Serializer_Store(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
                               
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteStores(APIView): 
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = get_object_or_404(Stores, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

#News
class GetNews(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = News.objects.select_related().all()
                serialize = Serializer_News(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddNews(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user=request.user
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                serializer = Serializer_News(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(created_by=user)
                    blog=News.objects.all().last()
                    lastblog=blog.id
                    Blog={"Blog":lastblog}
                
                    serializer1=Serializer_UserNotification(data=Blog,partial=True)
                    if serializer1.is_valid():
                        noti=serializer1.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
                                        
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateNews(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':

                User = News.objects.get(id=id)
                serializer = Serializer_News(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
                                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteNews(APIView): 
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = get_object_or_404(News, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)    

import pandas as pd
import uuid

class ExportImportExcel(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            a=[]
            # User = Product.objects.filter(created_by=request.user)
            User = Product.objects.all()
            serialize=Serializer_Product(User,many=True).data
            for i in serialize:
                for j in i["Prices"]:
                    for k in j["Price"]:
                        response={"Product_Name":i["Product_Name"],"SubcategoryName":i["SubcategoryName"],"category_name":i["category_name"],"StoreAddress":i["StoreAddress"],"StoreName":i["StoreName"],"Product_Description":i["Product_Description"],"strain":i["strain"],"Status":i["Status"],"Store_Country":i["Store_Country"],"Store_State":i["Store_State"],"Store_City":i["Store_City"],"Store_Type":i["Store_Type"],"Price":k}
                        a.append(response)
            df=pd.DataFrame(a)
            df.to_csv(f'/home/selnoxinfotech/Anshuman/BackwoodAroma/{uuid.uuid4()}.csv',encoding="UTF-8",index=False)
            return Response(a)
        except Exception as e:
            return Response({'error' : str(e)},status=500)


class TotalCount(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,format=None):
        try:
            category=Category.objects.all().count()
            subCategory=SubCategory.objects.all().count()
            product=Product.objects.all().count()
            brand=Brand.objects.all().count()
            store=Stores.objects.all().count()
            news=News.objects.all().count()
            return Response({'Data':[{"title":"Total Category","total":category},
                                    {"title":"Total Product","total":product},
                                    {"title":"Total subCategory","total":subCategory},
                                    {"title":"Total brand","total":brand},
                                    {"title":"Total store","total":store},
                                    {"title":"Total News","total":news}]})
        except Exception as e:
            return Response({'error' : str(e)},status=500)    

class TotalProductGraph(APIView):   
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            TotalProduct=Product.objects.filter(created__range=["2022-01-01", "2050-01-31"])
            if TotalProduct is not None:
                User = Product.objects.all()
                for i in User:
                    CreatedMonths=i.created.strftime('%B')
                    if CreatedMonths=='January':
                        TotalProductCount=Product.objects.count()
                    elif CreatedMonths=='February':
                        TotalProductCount=Product.objects.count()
                    elif CreatedMonths=='March':
                        TotalProductCount=Product.objects.count()
                    elif CreatedMonths=='April':
                        TotalProductCount=Product.objects.count()
                    elif CreatedMonths=='May':
                        TotalProductCount=Product.objects.count()
                    elif CreatedMonths=='June':
                        TotalProductCount=Product.objects.count()
                    elif CreatedMonths=='July':
                        TotalProductCount=Product.objects.count()
                    elif CreatedMonths=='August':
                        TotalProductCount=Product.objects.count()
                    elif CreatedMonths=='September':
                        TotalProductCount=Product.objects.count()
                    elif CreatedMonths=='October':
                        TotalProductCount=Product.objects.count()
                    elif CreatedMonths=='November':
                        TotalProductCount=Product.objects.count()
                    elif CreatedMonths=='December':
                        TotalProductCount=Product.objects.count()
                        
            return Response({'data':{"Month":CreatedMonths,"count":TotalProductCount}})
        except Exception as e:
            return Response({'error' : str(e)},status=500)


#Category Api
class GetNewsCategories(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = NewsCategory.objects.select_related().all()
                serialize = Serializer_NewsCategory(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
    
class AddNewsCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            a=request.user
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                serializer = Serializer_NewsCategory(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(created_by=request.user)
                    return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateNewsCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = NewsCategory.objects.get(id=id)
                serializer = Serializer_NewsCategory(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteNewsCategory(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = get_object_or_404(NewsCategory, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

#Sub Category Api
class GetNewsSubCategories(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = NewsSubCategory.objects.select_related().all()
                serialize = Serializer_NewsSubCategory(User, many=True)
                return Response({"data":serialize.data},status=200)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddNewsSubCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                serializer = Serializer_NewsSubCategory(data=request.data, partial=True)
                if serializer.is_valid(): 
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateNewsSubCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = NewsSubCategory.objects.get(id=id)
                serializer = Serializer_NewsSubCategory(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteNewsSubCategory(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = get_object_or_404(NewsSubCategory, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class FilterbyNewsSubCategory(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            subcategory=request.data.get(id)
            User = News.objects.filter(SubCategory=subcategory)
            serializer = Serializer_News(User,many=True)
            return Response({"status": "success", "data": serializer.data}, status=200)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class FilterbyCategory(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,id=None):
        try:
            User = SubCategory.objects.filter(category_id=id)
            serializer = Serializer_SubCategory(User,many=True)
            
            return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class FilterStatesByCountry(APIView):
    def get(self,request,id=None):
        try:
            User = States.objects.filter(Country_id=id)
            active=States.objects.filter(Status="Active")
            if User and active:
                serializer = Serializer_States(User,many=True)
                return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FilterCitiesByStates(APIView):
    def get(self,request,id=None):
        try:
            User = Cities.objects.filter(States_id=id)
            
            active=User.filter(Status="Active")
            
            serializer = Serializer_Cities(active,many=True)
            return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
 
class ActiveCategory(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            User=Category.objects.filter(Status="Active")
            serializer = Serializer_Category(User,many=True)
            return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
class ActiveSubCategory(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            User=SubCategory.objects.filter(Status="Active")
            serializer = Serializer_SubCategory(User,many=True)
            return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActiveCountry(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            User=Countries.objects.filter(Status="Active")
            serializer = Serializer_Country(User,many=True)
            return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActiveStates(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            User=States.objects.filter(Status="Active")
            serializer = Serializer_States(User,many=True)
            return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ActiveCities(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            User=Cities.objects.filter(Status="Active")
            serializer = Serializer_Cities(User,many=True)
            return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActiveStores(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            User=Stores.objects.filter(Status="Active")
            serializer = Serializer_Store(User,many=True)
            return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ActiveBrand(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            User=Brand.objects.filter(Status="Active")
            serializer = Serializer_Brand(User,many=True)
            return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
class ActiveNetWeight(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            User=Net_Weight.objects.filter(Status="Active")
            serializer = Serializer_Net_Weight(User,many=True)
            return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class  DeleteVendor(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='vendor managent':
                user = get_object_or_404(User, id=id)
                user.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetAllUsers(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner':
                alluser=User.objects.all()
                serializer = UserSerializer(alluser,many=True)
                return Response({"status": "success", "data":serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetAllVendor(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            z=[]
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='vendor managent':
                allvendor=User.objects.filter(user_type='Vendor')
                for i in allvendor:
                    l=Stores.objects.filter(created_by=i.id)
                    for m in l:
                        response={"email":i.email,"Name":i.username,"MobileNo.":i.MobilePhone,"Status":i.status,"Register Date":m.created,"StoreName":m.Store_Name,"StoreType":m.Store_Type,"id":i.id}
                        z.append(response)
                return Response({"status":"success","data":z},status=status.HTTP_200_OK)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class GetActiveVendor(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='vendor managent':
                user=User.objects.filter(status='Active')
                allvendor=user.filter(user_type="Vendor")
                serializer=UserSerializer(allvendor,many=True)
                return Response({"status":"success","data":serializer.data},status=status.HTTP_200_OK)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetHideVendor(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='vendor managent':
                user=User.objects.filter(status='Hide')
                allvendor=user.filter(user_type="Vendor")
                serializer=UserSerializer(allvendor,many=True)
                return Response({"status":"success","data":serializer.data},status=status.HTTP_200_OK)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Home_Page_Banner  
class Get_Home_Page_Banner(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User =HomePageBanner.objects.select_related().all()
                serialize = Serializer_HomePageBanner(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
            
        except Exception as e:
            return Response({'error' : str(e)},status=500)
 
class Add_Home_Page_Banner(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                serializer = Serializer_HomePageBanner(data=request.data, partial=True)
                if serializer.is_valid():
                        serializer.save()
                        return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Update_Home_Page_Banner(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = HomePageBanner.objects.get(id=id)
                serializer = Serializer_HomePageBanner(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Delete_Home_Page_Banner(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = get_object_or_404(HomePageBanner, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

import io, csv, pandas as pd
class FileUploadAPIView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        decoded_file = file.read().decode()
        reader = csv.DictReader(io.StringIO(decoded_file))
        data = list(reader)
        for row in data:
            objs = [
                USACountry(
                        zip= row["zip"],
                        lat= row['lat'],
                        lng= row["lng"],
                        city= row["city"],
                        state_id= row["state_id"],
                        state_name= row["state_name"],
                        zcta= row["zcta"],
                        parent_zcta= row["parent_zcta"],
                        population= row["population"],
                        density= row["density"],
                        county_fips= row["county_fips"],
                        county_name= row["county_name"],
                        county_weights= row["county_weights"],
                        county_names_all= row["county_names_all"],
                        county_fips_all= row["county_fips_all"],
                        imprecise= row["imprecise"],
                        military= row["military"],
                        timezone= row["timezone"],
                        
                        )

        ]
            a=USACountry.objects.bulk_create(objs)
        return Response("Sucess")

class GetLaw(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User =Law.objects.select_related().all()
                serialize = Serializer_Law(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddLaw(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                serializer = Serializer_Law(data=request.data, partial=True)
                if serializer.is_valid():
                        serializer.save()
                        return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateLaw(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = Law.objects.get(id=id)
                serializer = Serializer_Law(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
            
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteLaw(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = get_object_or_404(Law, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class GetAboutUs(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User =AboutUs.objects.select_related().all()
                serialize = Serializer_AboutUs(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddAboutUs(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                serializer = Serializer_AboutUs(data=request.data, partial=True)
                if serializer.is_valid():
                        serializer.save()
                        return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateAboutUs(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = AboutUs.objects.get(id=id)
                serializer = Serializer_AboutUs(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteAboutUs(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = get_object_or_404(AboutUs, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
     
class GetTermsandCondition(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User =TermsandCondition.objects.select_related().all()
                serialize = Serializer_TermsAndCondition(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddTermsandCondition(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                serializer = Serializer_TermsAndCondition(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateTermsandCondition(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = TermsandCondition.objects.get(id=id)
                serializer = Serializer_TermsAndCondition(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteTermsandCondition(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = get_object_or_404(TermsandCondition, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
class GetPrivacyandPolicies(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User =PrivacyandPolicies.objects.select_related().all()
                serialize = Serializer_PrivacyAndPolicies(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddPrivacyandPolicies(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                serializer = Serializer_PrivacyAndPolicies(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdatePrivacyandPolicies(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = PrivacyandPolicies.objects.get(id=id)
                serializer = Serializer_PrivacyAndPolicies(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeletePrivacyandPolicies(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = get_object_or_404(PrivacyandPolicies, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class GetPromotionalBanners(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        try:
            a=request.user.user_type.Name
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User =PromotionalBanners.objects.select_related().all()
                serialize = Serializer_PromotionalBanners(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddPromotionalBanners(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            # a=request.user.user_type.Name
            # if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                serializer = Serializer_PromotionalBanners(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            # else:
            #     return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdatePromotionalBanners(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = PromotionalBanners.objects.get(id=id)
                serializer = Serializer_PromotionalBanners(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeletePromotionalBanners(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            a=request.user.user_type.Name
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = get_object_or_404(PromotionalBanners, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class GetNet_Weight(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = Net_Weight.objects.select_related().all()
                serialize = Serializer_Net_Weight(User, many=True)
                return Response({"data":serialize.data},status=200)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddNet_Weight(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                serializer = Serializer_Net_Weight(data=request.data, partial=True)
                if serializer.is_valid(): 
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateNet_Weight(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = Net_Weight.objects.get(id=id)
                serializer = Serializer_Net_Weight(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteNet_Weight(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = get_object_or_404(Net_Weight, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class GetSubscribe(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = Subscribe.objects.select_related().all()
            serialize = Serializer_Subscribe(User, many=True)
            return Response({"data":serialize.data},status=200)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class GetStaticImages(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = StaticImages.objects.select_related().all()
                serialize = Serializer_StaticImages(User, many=True)
                return Response({"data":serialize.data},status=200)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddStaticImages(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                serializer = Serializer_StaticImages(data=request.data, partial=True)
                if serializer.is_valid(): 
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateStaticImages(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = StaticImages.objects.get(id=id)
                serializer = Serializer_StaticImages(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteStaticImages(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                User = get_object_or_404(StaticImages, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)


class UpdateProfileForVendor(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='Co-Owner' or a=='Content Manager Editor':
                user = User.objects.get(id=id)
                serializer = UserSerializer(user, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         