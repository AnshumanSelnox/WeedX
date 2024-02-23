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
from Ecommerce.settings import EMAIL_HOST_USER,EMAIL_HOST_PASSWORD
import smtplib
import random
from UserPanel.serializer import *
from datetime import datetime,timedelta
from django.utils import timezone
from dateutil.relativedelta import relativedelta 
from operator import itemgetter  
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EmailBody='''    <div>
        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">Dear Administrator,</h4>

         <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">Thank you for choosing Cannabaze POS! Your trust in our services is highly appreciated. To access your admin panel, kindly use the provided One-Time Password (OTP):</h4>
             <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> OTP: <b style="color:#222222;font-size:14px;font-weight: 700; background-color: yellow;"> Your One Time Password is {otp}</b></h4>
             <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> This OTP is valid for a single login session and should be utilized within the next 10 minutes. If you have not initiated this request or harbor any concerns about the security of your account, please promptly contact our support team.</h4>
             <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">Contact Information: </h4>
             <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400; margin:4px;"> Phone:  <a  style="color:#0084ff;font-size:14px;font-weight: 500;"  href="tel:+1 (209) 655-0360">+1 1(209) 655-0360</a></h4>
             <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400; margin:4px;"> Email: <a  style="color:#0084ff;font-size:14px;font-weight: 500;"  href="mailto:info@weedx.io">info@weedx.io</a></h4>
             <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400; margin:4px;"> Website: <a  style="color:#0084ff;font-size:14px;font-weight: 500;"  href="https://cannabaze.com/"> cannabaze.com</a></h4>
             <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;  margin:4px; margin-top: 12px;"> Best regards,</h4>
             <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400; margin:4px;"> Cannabaze POS Team</h4>
     </div>'''

def send_OneToOneMail(to_emails='',from_email=''):
    Otp = random.randint(1000, 9999)
    user = User.objects.get(email=to_emails)
    user.otp = Otp
    user.save()
    email_from = EMAIL_HOST_USER
    password = EMAIL_HOST_PASSWORD
    email_message = MIMEMultipart()
    email_message['From'] = from_email
    email_message['To']=to_emails
    email_message['Subject'] = "One-Time Password (OTP) for Cannabaze Admin Panel Login"
    email_message.attach(MIMEText(EmailBody.format(username=user.username,otp=str(Otp)), "html"))
    email_string = email_message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_from, password)
        server.sendmail(email_from, to_emails, email_string)

class VerifyOtpLogin(APIView):
    permission_classes=(permissions.AllowAny,)
    def post(self,request):
        try:
            email=request.data.get("email")
            otp=request.data.get("OTP")
            user= User.objects.filter(email=email).filter(user_type="Admin").first()
            if user.user_type=="Admin" :
                if user.otp != int(otp):
                    return Response({
                        'message':'Something goes wrong',
                        'data':'invalid Otp'
                    },status=status.HTTP_400_BAD_REQUEST)
                user= User.objects.get(email=email)  
                if user is not None:
                    tokens = create_jwt_pair_for_user(user)
                    permission=user.Roles.all()
                    serialize=Serializer_RolesandPermission(permission,many=True).data
                    response = {"message": "Login Successfull", "tokens": tokens,"UserType":user.user_type,"permission":serialize,"is_superuser":user.is_superuser}
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
            
                user=User.objects.filter(email=email).filter(user_type ="Admin")
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
                        serializer=LoginSerializer1(data=request.data)
                        if serializer.is_valid():
                            email=serializer.validated_data['email']
                            user1=User.objects.filter(username=username).filter(email=email).filter(user_type ="Admin").first()
                            if user1:
                                if user1.user_type =="Admin":
                                    send_OneToOneMail(from_email='smtpselnox@gmail.com',to_emails=email)
                                    return Response({'message':'Email sent','data':{"Otp_Sent_to":email}},status=status.HTTP_200_OK)
                                else:
                                    return Response({"error":"Not Authorized"},status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response({"error":"Username and Email Mismatch"},status=status.HTTP_400_BAD_REQUEST)
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
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RegisterAPI(generics.GenericAPIView):
    serializer_class =RegisterSerializer

    def post(self,request,*args,**kwargs):
        try:
            roles=request.data.get("Roles")
            serializer=self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user=serializer.save()
            user.Roles.set(roles)
            return Response({
            "user":UserSerializer(user,context=self.get_serializer_context()).data,
            # "token":AuthToken.objects.create(user)[1]
            })
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteUser(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self, request, id=None):
        try:
            a=request.user.user_type    
            if a == 'Admin':
                user = get_object_or_404(User, id=id)
                user.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#Category Api
class GetCategories(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a=="Admin":
                category = Category.objects.select_related().all()
                serialize = Serializer_Category(category, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class AddCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin':
           
                serializer = Serializer_Category(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data},status=status.HTTP_200_OK)
                else:
                    return Response({ "error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = Category.objects.get(id=id)
                serializer = Serializer_Category(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
                
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
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Sub Category Api
class GetSubCategories(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = SubCategory.objects.select_related().all()
                serialize = Serializer_SubCategory(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddSubCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin':

                serializer = Serializer_SubCategory(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
              
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateSubCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = SubCategory.objects.get(id=id)
                serializer = Serializer_SubCategory(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
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
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Country
class GetCountry(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = Countries.objects.select_related().all()
                serialize = Serializer_Country(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddCountry(APIView):
    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin':
                serializer = Serializer_Country(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateCountry(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a== 'Content Manager Editor':

                User = Countries.objects.get(id=id)
                serializer = Serializer_Country(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
                
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
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#States
class GetStates(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = States.objects.select_related().all()
                serialize = Serializer_States(User, many=True)
                
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddStates(APIView):

    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a== 'Content Manager Editor':
                serializer = Serializer_States(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"status": "error", "data": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateStates(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
            
                User = States.objects.get(id=id)
                serializer = Serializer_States(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"status": "error", "data": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
                
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
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Cities 
class GetCities(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = Cities.objects.select_related().all()
                serialize = Serializer_Cities(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddCities(APIView):

    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin':
                serializer = Serializer_Cities(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateCities(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = Cities.objects.get(id=id)
                serializer = Serializer_Cities(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({ "error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
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
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#Brand
class GetBrand(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = Brand.objects.select_related().all()
                serialize = Serializer_Brand(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddBrand(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin':
                serializer = Serializer_Brand(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        
                        
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateBrand(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':

                User = Brand.objects.get(id=id)
                serializer = Serializer_Brand(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
                    
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
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Salestax
class GetSalesTax(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = Salestaxes.objects.select_related().all()
            serialize = Serializer_Salestax(User, many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Esteemedtax
class GetEsteemedTax(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = Estemeedtaxes.objects.select_related().all()
            serialize = Serializer_Esteemedtax(User, many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

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
            if a == 'Admin' or a=='store managment':
                User = Stores.objects.select_related().all()
                serialize = Serializer_Store(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddStores(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='store managment':

                serializer = Serializer_Store(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
                            
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateStores(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin' or a=='store managment':

                User = Stores.objects.get(id=id)
                serializer = Serializer_Store(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
                               
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
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#News
class GetNews(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = News.objects.select_related().all()
                serialize = Serializer_News(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddNews(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user=request.user
            a=request.user.user_type
            if a == 'Admin':
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
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
                                        
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateNews(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':

                User = News.objects.get(id=id)
                serializer = Serializer_News(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
                                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteNews(APIView): 
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = get_object_or_404(News, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

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
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

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
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Category Api
class GetNewsCategories(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = NewsCategory.objects.select_related().all()
                serialize = Serializer_NewsCategory(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class AddNewsCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            a=request.user
            if a == 'Admin':
                serializer = Serializer_NewsCategory(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(created_by=request.user)
                    return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateNewsCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = NewsCategory.objects.get(id=id)
                serializer = Serializer_NewsCategory(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteNewsCategory(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = get_object_or_404(NewsCategory, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Sub Category Api
class GetNewsSubCategories(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = NewsSubCategory.objects.select_related().all()
                serialize = Serializer_NewsSubCategory(User, many=True)
                return Response({"data":serialize.data},status=status.HTTP_200_OK)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddNewsSubCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin':
                serializer = Serializer_NewsSubCategory(data=request.data, partial=True)
                if serializer.is_valid(): 
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateNewsSubCategories(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = NewsSubCategory.objects.get(id=id)
                serializer = Serializer_NewsSubCategory(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteNewsSubCategory(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = get_object_or_404(NewsSubCategory, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FilterbyNewsSubCategory(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            subcategory=request.data.get(id)
            User = News.objects.filter(SubCategory=subcategory)
            serializer = Serializer_News(User,many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            a=request.user.user_type
            if a=="Admin":
                User=Stores.objects.filter(Status="Active")
                serializer = Serializer_Store(User,many=True)
                return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN) 
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ActiveBrand(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            a=request.user.user_type
            if a=="Admin":
                User=Brand.objects.filter(Status="Active")
                serializer = Serializer_Brand(User,many=True)
                return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN) 
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
            if a == 'Admin':
                user = get_object_or_404(User, id=id)
                user.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetAllUsers(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            a=request.user.user_type
            if a == 'Admin':
                alluser=User.objects.all()
                serializer = UserSerializer(alluser,many=True)
                return Response({"status": "success", "data":serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetAllVendor(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            z=[]
            a=request.user.user_type
            if a == 'Admin':
                allvendor=User.objects.filter(user_type='Vendor')
                for i in allvendor:
                    l=Stores.objects.filter(created_by=i.id)
                    for m in l:
                        response={"email":i.email,"Name":i.username,"MobileNo.":i.MobilePhone,"Status":i.status,"RegisterDate":m.created,"StoreName":m.Store_Name,"StoreType":m.Store_Type,"id":i.id,"Storeid":m.id}
                        z.append(response)
                return Response({"status":"success","data":z},status=status.HTTP_200_OK)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class GetActiveVendor(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            a=request.user.user_type
            if a == 'Admin':
                user=User.objects.filter(status='Active')
                allvendor=user.filter(user_type="Vendor")
                serializer=UserSerializer(allvendor,many=True)
                return Response({"status":"success","data":serializer.data},status=status.HTTP_200_OK)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetHideVendor(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            a=request.user.user_type
            if a == 'Admin':
                user=User.objects.filter(status='Hide')
                allvendor=user.filter(user_type="Vendor")
                serializer=UserSerializer(allvendor,many=True)
                return Response({"status":"success","data":serializer.data},status=status.HTTP_200_OK)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Home_Page_Banner  
class Get_Home_Page_Banner(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User =HomePageBanner.objects.select_related().all()
                serialize = Serializer_HomePageBanner(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
            
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
class Add_Home_Page_Banner(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin':
                serializer = Serializer_HomePageBanner(data=request.data, partial=True)
                if serializer.is_valid():
                        serializer.save()
                        return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Update_Home_Page_Banner(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = HomePageBanner.objects.get(id=id)
                serializer = Serializer_HomePageBanner(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Delete_Home_Page_Banner(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = get_object_or_404(HomePageBanner, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            if a == 'Admin':
                User =Law.objects.select_related().all()
                serialize = Serializer_Law(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddLaw(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin':
                serializer = Serializer_Law(data=request.data, partial=True)
                if serializer.is_valid():
                        serializer.save()
                        return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateLaw(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = Law.objects.get(id=id)
                serializer = Serializer_Law(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
            
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteLaw(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = get_object_or_404(Law, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetAboutUs(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User =AboutUs.objects.select_related().all()
                serialize = Serializer_AboutUs(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddAboutUs(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin':
                serializer = Serializer_AboutUs(data=request.data, partial=True)
                if serializer.is_valid():
                        serializer.save()
                        return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateAboutUs(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = AboutUs.objects.get(id=id)
                serializer = Serializer_AboutUs(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteAboutUs(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = get_object_or_404(AboutUs, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
class GetTermsandCondition(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User =TermsandCondition.objects.select_related().all()
                serialize = Serializer_TermsAndCondition(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddTermsandCondition(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin':
                serializer = Serializer_TermsAndCondition(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateTermsandCondition(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = TermsandCondition.objects.get(id=id)
                serializer = Serializer_TermsAndCondition(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteTermsandCondition(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = get_object_or_404(TermsandCondition, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetPrivacyandPolicies(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User =PrivacyandPolicies.objects.select_related().all()
                serialize = Serializer_PrivacyAndPolicies(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddPrivacyandPolicies(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin':
                serializer = Serializer_PrivacyAndPolicies(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdatePrivacyandPolicies(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = PrivacyandPolicies.objects.get(id=id)
                serializer = Serializer_PrivacyAndPolicies(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeletePrivacyandPolicies(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = get_object_or_404(PrivacyandPolicies, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetPromotionalBanners(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User =PromotionalBanners.objects.select_related().all()
                serialize = Serializer_PromotionalBanners(User, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddPromotionalBanners(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            a=request.user.user_type.Name
            if a == 'Admin':
                serializer = Serializer_PromotionalBanners(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdatePromotionalBanners(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = PromotionalBanners.objects.get(id=id)
                serializer = Serializer_PromotionalBanners(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeletePromotionalBanners(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id=None):
        try:
            a=request.user.user_type.Name
            if a == 'Admin':
                User = get_object_or_404(PromotionalBanners, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetNet_Weight(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = Net_Weight.objects.select_related().all()
                serialize = Serializer_Net_Weight(User, many=True)
                return Response({"data":serialize.data},status=status.HTTP_200_OK)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddNet_Weight(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin':
                serializer = Serializer_Net_Weight(data=request.data, partial=True)
                if serializer.is_valid(): 
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateNet_Weight(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = Net_Weight.objects.get(id=id)
                serializer = Serializer_Net_Weight(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteNet_Weight(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = get_object_or_404(Net_Weight, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetSubscribe(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = Subscribe.objects.select_related().all()
                serialize = Serializer_Subscribe(User, many=True)
                return Response({"data":serialize.data},status=status.HTTP_200_OK)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetStaticImages(APIView):
    def get(self, request, format=None):
        try:
            User = StaticImages.objects.select_related().all()
            serialize = Serializer_StaticImages(User, many=True)
            return Response({"data":serialize.data},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddStaticImages(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            a=request.user.user_type
            if a == 'Admin':
                serializer = Serializer_StaticImages(data=request.data, partial=True)
                if serializer.is_valid(): 
                    serializer.save()
                    return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateStaticImages(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = StaticImages.objects.get(id=id)
                serializer = Serializer_StaticImages(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteStaticImages(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                User = get_object_or_404(StaticImages, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateProfileForVendor(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a == 'Admin':
                user = User.objects.get(id=id)
                serializer = UserSerializer(user, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorised",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetRolesAndPermission(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        try:
            a=request.user.user_type
            if a=="Admin":
                category = CustomRole.objects.select_related().all()
                serialize = Serializer_RolesandPermission(category, many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class AddRolesAndPermission(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            a=request.user.user_type
            if a=="Admin":
                serializer = Serializer_RolesandPermission(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"status": "success","data": serializer.data},status=status.HTTP_200_OK)
                else:
                    return Response({ "error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateRolesAndPermission(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id=None):
        try:
            a=request.user.user_type
            if a=="Admin":
                User = CustomRole.objects.get(id=id)
                serializer = Serializer_RolesandPermission(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteRolesAndPermission(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id=None):
        try:
            a=request.user.user_type
            if a=="Admin":
                User = get_object_or_404(CustomRole, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserNameCheck(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            a=request.user.user_type
            if a=="Admin":
                username=request.data.get("username",None)
                email=request.data.get("email",None)
                UserName=User.objects.filter(username=username)
                Email=User.objects.filter(email=email)
                if UserName.exists():
                    return Response("This UserName is already Exist")
                elif Email.exists():
                    return Response("This Email Id is already registered with another account.")
                else:
                    return Response("False")
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
class AllStaff(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            qwe=request.user.user_type
            if qwe =="Admin":
                a=[]
                user=User.objects.all()
                for i in user:
                    if i.Roles!=[]:
                        z=i.Roles.all()
                        b=Serializer_RolesandPermission(z,many=True).data
                        if z:
                            response={"ID":i.id,"Name":i.username,"Email":i.email,"Status":i.status,"Roles": [x["RoleTitle"] for x in b ],"created_at": i.created_at,"MobileNo":i.MobilePhone}
                            a.append(response)
                return Response(a)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
class RolesAfterLogin(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            a=request.user.user_type
            if a == 'Admin':
                user=request.user
                z=user.Roles.all()
                serialize=Serializer_RolesandPermission(z,many=True).data
                return Response(serialize)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
class TotalStore(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                LastStartDate=request.data.get("LastStartDate",None)
                EndStartDate=request.data.get("EndStartDate",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    z=[]
                    store=Stores.objects.filter(created__icontains=StartDate).count()
                    lastdaystore=Stores.objects.filter(created__icontains=LastStartDate).count()
                    if lastdaystore !=0:
                        totalpercenttage=(store - lastdaystore )*100/lastdaystore
                        if store> lastdaystore:
                            result = {"TotalStore":store,"percentage":totalpercenttage,"Growth":True}
                            z.append(result)
                        else:
                            result={"TotalStore":store,"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"TotalStore":store,"percentage":0,"Growth":True}
                        z.append(result)
                    return Response(z)

                else:
                    z=[]
                    startDate=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    endDate=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    lastStartDate=timezone.make_aware(datetime.strptime(LastStartDate, '%Y-%m-%d'))
                    endStartDate=timezone.make_aware(datetime.strptime(EndStartDate, '%Y-%m-%d'))
                    currentstorecount=Stores.objects.filter(created__gte=startDate,created__lt=(endDate+timedelta(days=1))).count()
                    laststore=Stores.objects.filter(created__gte=lastStartDate,created__lt=endStartDate).count()
                    if laststore !=0:
                        totalpercenttage=(currentstorecount - laststore)  * 100/laststore
                        if currentstorecount >= laststore:
                            result = {"TotalStore":currentstorecount,"percentage":round(totalpercenttage,2),"Growth":True}
                            z.append(result)
                        else:
                            result={"TotalStore":currentstorecount,"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"TotalStore":currentstorecount,"percentage":0,"Growth":True}
                        z.append(result)

                    return Response(z)
                
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VendorCard(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                LastStartDate=request.data.get("LastStartDate",None)
                EndStartDate=request.data.get("EndStartDate",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    z=[]

                    store=Stores.objects.filter(created__icontains=StartDate).count()
                    lastdaystore=Stores.objects.filter(created__icontains=LastStartDate).count()
                    if lastdaystore != 0:
                        totalpercenttage=(store - lastdaystore)*100 /lastdaystore
                        if store >= lastdaystore:
                            result = {"TotalStore":store,"percentage":totalpercenttage,"Growth":True}
                            z.append(result)
                        else:
                            result={"TotalStore":store,"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"TotalStore":store,"percentage":0,"Growth":True}
                        z.append(result)
                    return Response(z)

                else:
                    z=[]
                    startDate=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    endDate=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    lastStartDate=timezone.make_aware(datetime.strptime(LastStartDate, '%Y-%m-%d'))
                    endStartDate=timezone.make_aware(datetime.strptime(EndStartDate, '%Y-%m-%d'))
                    currentstorecount=Stores.objects.filter(created__gte=startDate,created__lt=(endDate + timedelta(days=1))).count()
                    laststore=Stores.objects.filter(created__gte=lastStartDate,created__lt=endStartDate).count()
                    if laststore !=0:
                        totalpercenttage=(currentstorecount - laststore)*100/laststore
                        if currentstorecount >= laststore:
                            result = {"TotalStore":currentstorecount,"percentage":round(totalpercenttage,2),"Growth":True}
                            z.append(result)
                        else:
                            result={"TotalStore":currentstorecount,"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"TotalStore":currentstorecount,"percentage":0,"Growth":True}
                        z.append(result)
                    return Response(z)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
class AllRecentOrder(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            a=request.user.user_type
            if a=="Admin":
                order=Order.objects.all().order_by("-OrderId")
                serialize=Serializer_Order(order,many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ParticularOrder(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,id=None):
        try:
            a=request.user.user_type
            if a=="Admin":
                order=Order.objects.filter(OrderId=id)
                serialize=Serializer_Order(order,many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SearchRecentOrderDashboard(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            a=request.user.user_type
            if a=="Admin":
                search=request.data.get("search")
                order=Order.objects.filter(OrderId__icontains=search) or  Order.objects.filter(Store__Store_Name__icontains=search) or Order.objects.filter(created_by__username__icontains=search)
                serialize=Serializer_Order(order,many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AllPendingStores(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            a=request.user.user_type
            if a=="Admin":
                StartDate=request.data.get("StartDate")
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime")
                z=[]
                l=[]
                if SelectTime == "Today":
                    store=Stores.objects.filter(Status="Hide").filter(created__icontains=StartDate).order_by("-id")
                    for i in store:
                        user=User.objects.filter(id=i.created_by_id).first()
                        response={"UserName":user.username,"TimeOfCreation":user.created_at,"Email":user.email,"MobileNo":user.MobilePhone,"StoreName":i.Store_Name,"StoreType":i.Store_Type,"StoreStatus":i.Status,"image":user.image.url  }
                        z.append(response)
                    return Response(z)
                else:
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    while week <= today:
                        store=Stores.objects.filter(Status="Hide").filter(created__gte=week,created__lt=(today+timedelta(days=1))).order_by("-id")
                        for i in store:
                            user=User.objects.filter(id=i.created_by_id).first()
                            response={"UserName":user.username,"TimeOfCreation":user.created_at,"Email":user.email,"MobileNo":user.MobilePhone,"StoreName":i.Store_Name,"StoreType":i.Store_Type,"StoreStatus":i.Status,"image":user.image.url  }
                            z.append(response)
                        week=week + timedelta(days=1)
                    for m in z:
                        if m not in l:
                            l.append(m)
                    return Response(l)
            
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TotalSalesCard(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                LastStartDate=request.data.get("LastStartDate",None)
                EndStartDate=request.data.get("EndStartDate",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    z=[]
                    totalsale=0
                    lastdayordersale=0
                    order=Order.objects.filter(OrderDate__icontains=StartDate)
                    for j in order:
                        totalsale =totalsale + j.subtotal
                    if lastdayordersale !=0:

                        totalpercenttage=(totalsale - lastdayordersale) * 100 / lastdayordersale
                        if totalsale >=  lastdayordersale:
                            result = {"totalsale":totalsale,"percentage":totalpercenttage,"Growth":True}
                            z.append(result)
                        else:
                            result={"totalsale":totalsale,"percentage":totalpercenttage,"Growth":False}
                            z.append(result)
                    else:
                        result={"totalsale":totalsale,"percentage":0,"Growth":False}
                        z.append(result)
                    return Response(z)

                else:
                    z=[]
                    totalsale=0
                    lastdayordersale=0
                    startDate=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    endDate=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    lastStartDate=timezone.make_aware(datetime.strptime(LastStartDate, '%Y-%m-%d'))
                    endStartDate=timezone.make_aware(datetime.strptime(EndStartDate, '%Y-%m-%d'))
                    currentsales=Order.objects.filter(OrderDate__gte=startDate,OrderDate__lte=(endDate + timedelta(days=1)))
                    for i in currentsales:
                        totalsale =totalsale + i.subtotal
                    lastorder=Order.objects.filter(OrderDate__gte=lastStartDate,OrderDate__lte=endStartDate)
                    for j in lastorder:
                        lastdayordersale =lastdayordersale + i.subtotal
                    if lastdayordersale !=0:
                        totalpercenttage=(totalsale - lastdayordersale)*100 /lastdayordersale
                        if totalsale >= lastdayordersale:
                            result = {"totalsale":totalsale,"percentage":round(totalpercenttage,2),"Growth":True}
                            z.append(result)
                        else:
                            result={"totalsale":totalsale,"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"totalsale":totalsale,"percentage":0,"Growth":True}
                        z.append(result)
                    return Response(z)
                
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TotalOrderCard(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                LastStartDate=request.data.get("LastStartDate",None)
                EndStartDate=request.data.get("EndStartDate",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    z=[]
                    current=0
                    order=Order.objects.filter(OrderDate__icontains=StartDate).count()
                    lastdayorder=Order.objects.filter(OrderDate__icontains=LastStartDate).count()
                    if lastdayorder !=0:
                        current += order
                        totalpercenttage=(order - lastdayorder) *100 /lastdayorder
                        if order >= lastdayorder:
                            result = {"Totalorder":current,"percentage":round(totalpercenttage,2),"Growth":True}
                            z.append(result)
                        else:
                            result={"Totalorder":current,"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"Totalorder":order,"percentage":0,"Growth":True}
                        z.append(result)
                    return Response(z)

                else:
                    z=[]
                    current=0
                    startDate=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    endDate=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    lastStartDate=timezone.make_aware(datetime.strptime(LastStartDate, '%Y-%m-%d'))
                    endStartDate=timezone.make_aware(datetime.strptime(EndStartDate, '%Y-%m-%d'))
                    currentordercount=Order.objects.filter(OrderDate__gte=startDate,OrderDate__lt=(endDate + timedelta(days=1))).count()
                    lastcurrentordercount=Order.objects.filter(OrderDate__gte=lastStartDate,OrderDate__lt=endStartDate).count()
                    if lastcurrentordercount !=0:
                        totalpercenttage=(currentordercount - lastcurrentordercount) * 100 /lastcurrentordercount
                        current += currentordercount
                        if currentordercount >= lastcurrentordercount:
                            result = {"Totalorder":current,"percentage":round(totalpercenttage,2),"Growth":True}
                            z.append(result)
                        else:
                            result={"Totalorder":current,"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"Totalorder":current,"percentage":0,"Growth":True}
                        z.append(result)
                    return Response(z)
                
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductDashBoardCard(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                LastStartDate=request.data.get("LastStartDate",None)
                EndStartDate=request.data.get("EndStartDate",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    z=[]
                    product=Product.objects.filter(created__icontains=StartDate).count()
                    lastdayProduct=Product.objects.filter(created__icontains=LastStartDate).count()
                    if lastdayProduct !=0:
                        totalpercenttage=(product-lastdayProduct)*100 /lastdayProduct
                        if product >= lastdayProduct:
                            result = {"Totalproduct":product,"percentage":round(totalpercenttage,2),"Growth":True}
                            z.append(result)
                        else:
                            result={"Totalproduct":product,"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"Totalproduct":product,"percentage":0,"Growth":True}
                        z.append(result)
                    return Response(z)

                else:
                    z=[]
                    startDate=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d')).date()
                    endDate=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d')).date()
                    lastStartDate=timezone.make_aware(datetime.strptime(LastStartDate, '%Y-%m-%d')).date()
                    endStartDate=timezone.make_aware(datetime.strptime(EndStartDate, '%Y-%m-%d')).date()
                    currentproductcount=Product.objects.filter(created__gte=startDate,created__lt=(endDate + timedelta(days=1))).count()
                    lastcurrentproductcount=Product.objects.filter(created__gte=lastStartDate,created__lt=endStartDate).count()
                    if lastcurrentproductcount !=0:
                        totalpercenttage=(currentproductcount - lastcurrentproductcount)*100 /lastcurrentproductcount
                        if currentproductcount >= lastcurrentproductcount:
                            result = {"Totalproduct":currentproductcount,"percentage":round(totalpercenttage,2),"Growth":True}
                            z.append(result)
                        else:
                            result={"Totalproduct":currentproductcount,"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"Totalproduct":currentproductcount,"percentage":0,"Growth":True}
                        z.append(result)

                    return Response(z)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomerDashBoardCard(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                LastStartDate=request.data.get("LastStartDate",None)
                EndStartDate=request.data.get("EndStartDate",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    z=[]
                    currentcustomer=[]
                    lastcustomer=[]
                    customer=Order.objects.filter(OrderDate__icontains=StartDate)
                    for j in customer:
                        currentcustomer.append(j.created_by)
                    res = [currentcustomer[i] for i in range(len(currentcustomer)) if i == currentcustomer.index(currentcustomer[i]) ]
                    lastdayProduct=Order.objects.filter(OrderDate__icontains=LastStartDate)
                    for k in lastdayProduct:
                        lastcustomer.append(k.created_by)
                    res1 = [lastcustomer[i] for i in range(len(lastcustomer)) if i == lastcustomer.index(lastcustomer[i]) ]
                    if len(res1) != 0:

                        totalpercenttage= (len(res) - len(res1))*100 /len(res1)
                        if len(res)> len(res1):
                            result = {"TotalCustomer":len(res),"percentage":round(totalpercenttage,2),"Growth":True}
                            z.append(result)
                        else:
                            result={"TotalCustomer":len(res),"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"TotalCustomer":len(res),"percentage":0,"Growth":True}
                        z.append(result)
                    return Response(z)
                else:
                    z=[]
                    daybeforecustomer=[]
                    currentcustomer=[]
                    lastcustomer=[]
                    startDate=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    endDate=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    lastStartDate=timezone.make_aware(datetime.strptime(LastStartDate, '%Y-%m-%d'))
                    endStartDate=timezone.make_aware(datetime.strptime(EndStartDate, '%Y-%m-%d'))
                    customer=Order.objects.filter(OrderDate__gte=startDate,OrderDate__lt=endDate + timedelta(days=1))
                    for j in customer:
                        currentcustomer.append(j.created_by)
                    res = [currentcustomer[i] for i in range(len(currentcustomer)) if i == currentcustomer.index(currentcustomer[i]) ]
                    daybefore=Order.objects.filter(OrderDate__gte=lastStartDate,OrderDate__lt=endStartDate)
                    for i in daybefore:
                        daybeforecustomer.append(i.created_by)
                    res1 = [daybeforecustomer[i] for i in range(len(daybeforecustomer)) if i == daybeforecustomer.index(daybeforecustomer[i]) ]
                    if len(res1) !=0:
                        totalpercenttage=(len(res) - len(res1)) * 100/len(res1)
                        if len(res) >= len(res1):
                            result = {"TotalCustomer":len(res),"percentage":round(totalpercenttage,2),"Growth":True}
                            z.append(result)
                        else:
                            result={"TotalCustomer":len(res),"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"TotalCustomer":len(res),"percentage":0,"Growth":True}
                        z.append(result)
                    return Response(z)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class TotalSalesPieChart(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                LastStartDate=request.data.get("LastStartDate",None)
                EndStartDate=request.data.get("EndStartDate",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    order=Order.objects.filter(OrderDate__icontains=EndDate).filter(Order_Status="Delivered")
                    order1=Order.objects.filter(OrderDate__icontains=StartDate).filter(Order_Status="Delivered")
                    if order1.count()!=0:
                        percentage=(order.count()- order1.count())*100/order1.count()
                        result = {"Pickup": 0, "Delivery": 0,"Curbsibe":0,"TotalSales":0,"Percentage":round(percentage,2),"Growth": (order.count()) >= (order1.count())}
                        for i in order:
                            result["TotalSales"] +=i.subtotal
                            if i.Order_Type == "Pickup":
                                result["Pickup"] += i.subtotal
                            elif i.Order_Type == "Delivery":
                                result["Delivery"] += i.subtotal
                            elif i.Order_Type == "Delivery and Pickup":
                                result["Curbsibe"] += i.subtotal
                    
                        return Response(result)
                    else:
                        result = {"Pickup": 0, "Delivery": 0,"Curbsibe":0,"TotalSales":0,"Percentage":0,"Growth": True}
                        for i in order:
                            result["TotalSales"] +=i.subtotal
                            if i.Order_Type == "Pickup":
                                result["Pickup"] += i.subtotal
                            elif i.Order_Type == "Delivery":
                                result["Delivery"] += i.subtotal
                            elif i.Order_Type == "Delivery and Pickup":
                                result["Curbsibe"] += i.subtotal
                        return Response(result)
                else:
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    lastStartDate=timezone.make_aware(datetime.strptime(LastStartDate, '%Y-%m-%d'))
                    endStartDate=timezone.make_aware(datetime.strptime(EndStartDate, '%Y-%m-%d'))
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=(today + timedelta(days=1))).filter(Order_Status="Delivered")
                    order1=Order.objects.filter(OrderDate__gte=lastStartDate,OrderDate__lt=endStartDate).filter(Order_Status="Delivered")
                    if order1.count()!=0:
                        percentage=(order.count()- order1.count())*100/order1.count()
                        result = {"Pickup": 0, "Delivery": 0,"Curbsibe":0,"TotalSales":0,"Percentage":round(percentage,2),"Growth": (order.count()) >= (order1.count())}
                        for i in order:
                            result["TotalSales"] +=i.subtotal
                            if i.Order_Type == "Pickup":
                                result["Pickup"] += i.subtotal
                            elif i.Order_Type == "Delivery":
                                result["Delivery"] += i.subtotal
                            elif i.Order_Type == "Delivery and Pickup":
                                result["Curbsibe"] += i.subtotal
                    
                        return Response(result)
                    else:
                        result = {"Pickup": 0, "Delivery": 0,"Curbsibe":0,"TotalSales":0,"Percentage":0,"Growth": True}
                        for i in order:
                            result["TotalSales"] +=i.subtotal
                            if i.Order_Type == "Pickup":
                                result["Pickup"] += i.subtotal
                            elif i.Order_Type == "Delivery":
                                result["Delivery"] += i.subtotal
                            elif i.Order_Type == "Delivery and Pickup":
                                result["Curbsibe"] += i.subtotal
                        return Response(result)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TopProduct(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    z=[]
                    q=[]
                    y=[]
                    order=Order.objects.filter(OrderDate__icontains=StartDate).filter(Order_Status="Delivered")
                    for i in order:
                        for j in i.Product:
                            a=ProductImage.objects.filter(product=j["Product_id"]).first()
                            qwe=0
                            cart=0
                            qwe = qwe + j["TotalPrice"]
                            cart= cart +j["Cart_Quantity"]
                            response={"ProductName":j["ProductName"],"ProductSalesCount":cart,"Price":qwe,"Image":a.image.url,"category":j["category"],"Product_id":j["Product_id"],"ProductPrice":j["Price"]["SalePrice"],"Stock": j["Price"]["Stock"],"StoreName":j["StoreName"]}
                            z.append(response)
                    for l in z:
                        if l not in y:
                            y.append(l)
                    for w in y:
                        found = False
                        for l in q:
                            if l["Product_id"] == w["Product_id"]:
                                l["ProductSalesCount"] += w["ProductSalesCount"]
                                l["Price"] += w["Price"]
                                found = True 
                                break
                        if not found:
                            q.append(w.copy())
                    q.sort(key = itemgetter('ProductSalesCount'), reverse=True)
                    return Response(q)
                else:
                    z=[]
                    y=[]
                    q=[]
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lte=(today + timedelta(days=1))).filter(Order_Status="Delivered")
                    for i in order:
                        for j in i.Product:
                            a=ProductImage.objects.filter(product=j["Product_id"]).first()
                            qwe=0
                            cart=0
                            qwe = qwe + j["TotalPrice"]
                            cart= cart +j["Cart_Quantity"]
                            response={"ProductName":j["ProductName"],"ProductSalesCount":cart,"Price":qwe,"Image":a.image.url,"category":j["category"],"Product_id":j["Product_id"],"ProductPrice":j["Price"]["SalePrice"],"Stock": j["Price"]["Stock"],"StoreName":j["StoreName"]}
                            z.append(response)
                    for l in z:
                        if l not in y:
                            y.append(l)
                    for w in y:
                        found = False
                        for l in q:
                            if l["Product_id"] == w["Product_id"]:
                                l["ProductSalesCount"] += w["ProductSalesCount"]
                                l["Price"] += w["Price"]
                                found = True 
                                break

                        if not found:
                            q.append(w.copy())
                        q.sort(key = itemgetter('ProductSalesCount'), reverse=True)
                    return Response(q)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TopStore(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                LastStartDate=request.data.get("LastStartDate",None)
                EndStartDate=request.data.get("EndStartDate",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    saleprice=0
                    z=[]
                    order=Order.objects.filter(OrderDate__icontains=StartDate).filter(Order_Status="Delivered")
                    order1=Order.objects.filter(OrderDate__icontains=EndDate).filter(Order_Status="Delivered")
                    for i in order:
                        store = Stores.objects.filter(id=i.Store_id).first()
                        if store:
                            saleprice += i.subtotal
                            response = {
                                "VendorName":store.created_by.username,
                                "Email":store.created_by.email,
                                "MobileNo":store.created_by.MobilePhone,
                                "StoreName": store.Store_Name,
                                "StoreType":store.Store_Type,
                                "Image": store.Store_Image.url,
                                "SalesPrice": saleprice,
                                "StoreOrder":StoreOrder,
                                "Growth": (order.count()) >= (order1.count()),
                                "id":store.id
                            }
                            z.append(response)
                    result = list({dictionary['StoreName']: dictionary for dictionary in z}.values())
                    return Response(result)
                else:
                    saleprice=0
                    StoreOrder=0
                    z=[]
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    lastStartDate=timezone.make_aware(datetime.strptime(LastStartDate, '%Y-%m-%d'))
                    endStartDate=timezone.make_aware(datetime.strptime(EndStartDate, '%Y-%m-%d'))
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lte=(today + timedelta(days=1))).filter(Order_Status="Delivered")
                    order1=Order.objects.filter(OrderDate__gte=lastStartDate,OrderDate__lte=(endStartDate + timedelta(days=1))).filter(Order_Status="Delivered")
                    for i in order:
                        store = Stores.objects.filter(id=i.Store_id).first()
                        storeorder=Order.objects.filter(Store=store.id)
                        for j in storeorder:
                            for k in j.Product:
                                StoreOrder+=k["Cart_Quantity"]
                        if store:
                            saleprice += i.subtotal
                            response = {
                                "VendorName":store.created_by.username,
                                "Email":store.created_by.email,
                                "MobileNo":store.created_by.MobilePhone,
                                "StoreName": store.Store_Name,
                                "StoreType":store.Store_Type,
                                "Image": store.Store_Image.url,
                                "SalesPrice": saleprice,
                                "StoreOrder":StoreOrder,
                                "Growth": (order.count()) >= (order1.count()),
                                "id":store.id
                            }
                            z.append(response)
                    result = list({dictionary['StoreName']: dictionary for dictionary in z}.values())
                    return Response(result)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TotalUserGraph(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    user=User.objects.filter(created_at__icontains=StartDate).filter(user_type="Customer").count()
                    response={"StartDate":StartDate,"User":user}
                    return Response(response)
                if SelectTime=="ThisWeek":
                    z=[]
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    while week <= today:
                        user=User.objects.filter(created_at__gte=week,created_at__lte=today).filter(user_type="Customer").count()
                        result = {"Date":week.strftime("%A"),"User":user}
                        z.append(result)
                        week=week + timedelta(days=1)
                    return Response(z)
                if SelectTime=="ThisMonth":
                    z=[]
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    while week <= today:
                        user=User.objects.filter(created_at__gte=week,created_at__lte=today).filter(user_type="Customer").count()
                        result = {"Date":week.strftime("%x"),"User":user}
                        z.append(result)
                        week=week + timedelta(days=1)
                    return Response(z)
                if SelectTime=="ThisYear":
                    z=[]
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    while week <= today:
                        user=User.objects.filter(created_at__gte=week,created_at__lte=today).filter(user_type="Customer").count()
                        result = {"Date":week.strftime("%B"),"User":user}
                        z.append(result)
                        week=week + relativedelta(months=+1)
                    return Response(z)

                else:
                    z=[]
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    while week <= today:
                        user=User.objects.filter(created_at__gte=week,created_at__lte=today).filter(user_type="Customer").count()
                        result = {"Date":week.strftime("%x"),"User":user}
                        z.append(result)
                        week=week + timedelta(days=1)
                    return Response(z)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TotalStoreVendorProFileCard(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,id=None):
        try:
            user=request.user.user_type
            if user=='Admin':
                store=Stores.objects.filter(created_by=id).count()
                return Response({"StoreCount":store})
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TotalSalesVendorCard(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                id=request.data.get("id")
                LastStartDate=request.data.get("LastStartDate",None)
                EndStartDate=request.data.get("EndStartDate",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    z=[]
                    totalsale=0
                    lastdayordersale=0
                    store=Stores.objects.filter(created_by=id)
                    for i in store:
                        order=Order.objects.filter(OrderDate__icontains=StartDate).filter(Store=i.id)
                        for j in order:
                            totalsale =totalsale + j.subtotal
                        if lastdayordersale !=0:

                            totalpercenttage=(totalsale - lastdayordersale) * 100 / lastdayordersale
                            if totalsale >=  lastdayordersale:
                                result = {"totalsale":totalsale,"percentage":totalpercenttage,"Growth":True}
                                z.append(result)
                            else:
                                result={"totalsale":totalsale,"percentage":totalpercenttage,"Growth":False}
                                z.append(result)
                        else:
                            result={"totalsale":totalsale,"percentage":0,"Growth":False}
                            z.append(result)
                    return Response(z[-1])

                else:
                    z=[]
                    totalsale=0
                    lastdayordersale=0
                    startDate=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    endDate=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    lastStartDate=timezone.make_aware(datetime.strptime(LastStartDate, '%Y-%m-%d'))
                    endStartDate=timezone.make_aware(datetime.strptime(EndStartDate, '%Y-%m-%d'))
                    store=Stores.objects.filter(created_by=id)
                    for m in store:
                        currentsales=Order.objects.filter(OrderDate__gte=startDate,OrderDate__lte=(endDate + timedelta(days=1))).filter(Store=m.id)
                        for i in currentsales:
                            totalsale =totalsale + i.subtotal
                        lastorder=Order.objects.filter(OrderDate__gte=lastStartDate,OrderDate__lte=endStartDate).filter(Store=m.id)
                        for j in lastorder:
                            lastdayordersale =lastdayordersale + i.subtotal
                        if lastdayordersale !=0:
                            totalpercenttage=(totalsale - lastdayordersale)*100 /lastdayordersale
                            if totalsale >= lastdayordersale:
                                result = {"totalsale":totalsale,"percentage":round(totalpercenttage,2),"Growth":True}
                                z.append(result)
                            else:
                                result={"totalsale":totalsale,"percentage":round(totalpercenttage,2),"Growth":False}
                                z.append(result)
                        else:
                            result={"totalsale":totalsale,"percentage":0,"Growth":True}
                            z.append(result)
                    return Response(z[-1])
                
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
class TotalOrderVendorCard(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                id=request.data.get("id")
                LastStartDate=request.data.get("LastStartDate",None)
                EndStartDate=request.data.get("EndStartDate",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    z=[]
                    current=0
                    last=0
                    store=Stores.objects.filter(created_by=id)
                    for i in store:
                        order=Order.objects.filter(OrderDate__icontains=StartDate).filter(Store=i.id).count()
                        lastdayorder=Order.objects.filter(OrderDate__icontains=LastStartDate).filter(Store=i.id).count()
                        current += order
                        last += lastdayorder
                    if last !=0:
                        totalpercenttage=(current - last) *100 /last
                        if order >= lastdayorder:
                            result = {"Totalorder":current,"percentage":round(totalpercenttage,2),"Growth":True}
                            z.append(result)
                        else:
                            result={"Totalorder":current,"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"Totalorder":current,"percentage":0,"Growth":True}
                        z.append(result)
                    return Response(z)
                else:
                    z=[]
                    current=0
                    last=0
                    startDate=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    endDate=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    lastStartDate=timezone.make_aware(datetime.strptime(LastStartDate, '%Y-%m-%d'))
                    endStartDate=timezone.make_aware(datetime.strptime(EndStartDate, '%Y-%m-%d'))
                    store=Stores.objects.filter(created_by=id)
                    for i in store:
                        currentordercount=Order.objects.filter(OrderDate__gte=startDate,OrderDate__lt=(endDate + timedelta(days=1))).filter(Store=i.id).count()
                        lastcurrentordercount=Order.objects.filter(OrderDate__gte=lastStartDate,OrderDate__lt=endStartDate).filter(Store=i.id).count()
                        current += currentordercount
                        last += lastcurrentordercount
                    if last !=0:
                        totalpercenttage=(current - last) * 100 /last
                        if current >= last:
                            result = {"Totalorder":current,"percentage":round(totalpercenttage,2),"Growth":True}
                            z.append(result)
                        else:
                            result={"Totalorder":current,"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"Totalorder":current,"percentage":0,"Growth":True}
                        z.append(result)
                    return Response(z)
                
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TotalProductCard(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                id=request.data.get("id")
                LastStartDate=request.data.get("LastStartDate",None)
                EndStartDate=request.data.get("EndStartDate",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    z=[]
                    current=0
                    last=0
                    store=Stores.objects.filter(created_by=id)
                    for i in store:
                        order=Product.objects.filter(created__icontains=StartDate).filter(Store_id=i.id).count()
                        lastdayorder=Product.objects.filter(created__icontains=LastStartDate).filter(Store_id=i.id).count()
                        current += order
                        last += lastdayorder
                    if last !=0:
                        totalpercenttage=(current - last) *100 /last
                        if order >= lastdayorder:
                            result = {"TotalProduct":current,"percentage":round(totalpercenttage,2),"Growth":True}
                            z.append(result)
                        else:
                            result={"TotalProduct":current,"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"TotalProduct":current,"percentage":0,"Growth":True}
                        z.append(result)
                    return Response(z)
                else:
                    startDate=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    endDate=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    lastStartDate=timezone.make_aware(datetime.strptime(LastStartDate, '%Y-%m-%d'))
                    endStartDate=timezone.make_aware(datetime.strptime(EndStartDate, '%Y-%m-%d'))
                    z=[]
                    current=0
                    last=0
                    store=Stores.objects.filter(created_by=id)
                    for i in store:
                        order=Product.objects.filter(created__gte=startDate,created__lt=(endDate + timedelta(days=1))).filter(Store_id=i.id).count()
                        lastdayorder=Product.objects.filter(created__gte=lastStartDate,created__lt=endStartDate).filter(Store_id=i.id).count()
                        current += order
                        last += lastdayorder
                    if last !=0:
                        totalpercenttage=(current - last) *100 /last
                        if order >= lastdayorder:
                            result = {"TotalProduct":current,"percentage":round(totalpercenttage,2),"Growth":True}
                            z.append(result)
                        else:
                            result={"TotalProduct":current,"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"TotalProduct":current,"percentage":0,"Growth":True}
                        z.append(result)
                    return Response(z)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class TotalCustomerVendorCard(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                id=request.data.get("id")
                LastStartDate=request.data.get("LastStartDate",None)
                EndStartDate=request.data.get("EndStartDate",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    z=[]
                    currentcustomer=[]
                    lastcustomer=[]
                    store=Stores.objects.filter(created_by=id)
                    for qwe in store:
                        customer=Order.objects.filter(OrderDate__icontains=StartDate).filter(Store=qwe.id)
                        for j in customer:
                            currentcustomer.append(j.created_by)
                        lastdayProduct=Order.objects.filter(OrderDate__icontains=LastStartDate).filter(Store=qwe.id)
                        for k in lastdayProduct:
                            lastcustomer.append(k.created_by)
                    res = [currentcustomer[i] for i in range(len(currentcustomer)) if i == currentcustomer.index(currentcustomer[i]) ]
                    res1 = [lastcustomer[i] for i in range(len(lastcustomer)) if i == lastcustomer.index(lastcustomer[i]) ]
                    if len(res1) != 0:

                        totalpercenttage= (len(res) - len(res1))*100 /len(res1)
                        if len(res)> len(res1):
                            result = {"TotalCustomer":len(res),"percentage":round(totalpercenttage,2),"Growth":True}
                            z.append(result)
                        else:
                            result={"TotalCustomer":len(res),"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"TotalCustomer":len(res),"percentage":0,"Growth":False}
                        z.append(result)
                    return Response(z)
                else:
                    z=[]
                    daybeforecustomer=[]
                    currentcustomer=[]
                    lastcustomer=[]
                    startDate=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    endDate=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    lastStartDate=timezone.make_aware(datetime.strptime(LastStartDate, '%Y-%m-%d'))
                    endStartDate=timezone.make_aware(datetime.strptime(EndStartDate, '%Y-%m-%d'))
                    store=Stores.objects.filter(created_by=id)
                    for qwe in store:
                        customer=Order.objects.filter(OrderDate__gte=startDate,OrderDate__lt=endDate + timedelta(days=1)).filter(Store=qwe.id)
                        for j in customer:
                            currentcustomer.append(j.created_by)
                        daybefore=Order.objects.filter(OrderDate__gte=lastStartDate,OrderDate__lt=endStartDate).filter(Store=qwe.id)
                        for i in daybefore:
                            daybeforecustomer.append(i.created_by)
                    res = [currentcustomer[i] for i in range(len(currentcustomer)) if i == currentcustomer.index(currentcustomer[i]) ]
                    res1 = [daybeforecustomer[i] for i in range(len(daybeforecustomer)) if i == daybeforecustomer.index(daybeforecustomer[i]) ]
                    if len(res1) !=0:
                        totalpercenttage=(len(res) - len(res1)) * 100/len(res1)
                        if len(res) >= len(res1):
                            result = {"TotalCustomer":len(res),"percentage":round(totalpercenttage,2),"Growth":True}
                            z.append(result)
                        else:
                            result={"TotalCustomer":len(res),"percentage":round(totalpercenttage,2),"Growth":False}
                            z.append(result)
                    else:
                        result={"TotalCustomer":len(res),"percentage":0,"Growth":False}
                        z.append(result)
                    return Response(z)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class AllStoresVendor(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,id=None):
        try:
            user=request.user.user_type
            if user=='Admin':
                store=Stores.objects.filter(created_by=id)
                serializer=Serializer_Store(store,many=True)
                return Response(serializer.data)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class TopSaleProductVendor(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                Storeid=request.data.get("Storeid",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    z=[]
                    q=[]
                    y=[]
                    order=Order.objects.filter(OrderDate__icontains=StartDate).filter(Order_Status="Delivered").filter(Store=Storeid)
                    for i in order:
                        for j in i.Product:
                            a=ProductImage.objects.filter(product=j["Product_id"]).first()
                            qwe=0
                            cart=0
                            qwe = qwe + j["TotalPrice"]
                            cart= cart +j["Cart_Quantity"]
                            response={"ProductName":j["ProductName"],"ProductSalesCount":cart,"Price":qwe,"Image":a.image.url,"category":j["category"],"Product_id":j["Product_id"],"ProductPrice":j["Price"]["SalePrice"],"Stock": j["Price"]["Stock"],"StoreName":j["StoreName"]}
                            z.append(response)
                    for l in z:
                        if l not in y:
                            y.append(l)
                    for w in y:
                        found = False
                        for l in q:
                            if l["Product_id"] == w["Product_id"]:
                                l["ProductSalesCount"] += w["ProductSalesCount"]
                                l["Price"] += w["Price"]
                                found = True 
                                break
                        if not found:
                            q.append(w.copy())
                    q.sort(key = itemgetter('ProductSalesCount'), reverse=True)
                    return Response(q)
                else:
                    z=[]
                    y=[]
                    q=[]
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lte=(today + timedelta(days=1))).filter(Order_Status="Delivered").filter(Store=Storeid)
                    for i in order:
                        for j in i.Product:
                            a=ProductImage.objects.filter(product=j["Product_id"]).first()
                            qwe=0
                            cart=0
                            qwe = qwe + j["TotalPrice"]
                            cart= cart +j["Cart_Quantity"]
                            response={"ProductName":j["ProductName"],"ProductSalesCount":cart,"Price":qwe,"Image":a.image.url,"category":j["category"],"Product_id":j["Product_id"],"ProductPrice":j["Price"]["SalePrice"],"Stock": j["Price"]["Stock"],"StoreName":j["StoreName"]}
                            z.append(response)
                    for l in z:
                        if l not in y:
                            y.append(l)
                    for w in y:
                        found = False
                        for l in q:
                            if l["Product_id"] == w["Product_id"]:
                                l["ProductSalesCount"] += w["ProductSalesCount"]
                                l["Price"] += w["Price"]
                                found = True 
                                break

                        if not found:
                            q.append(w.copy())
                        q.sort(key = itemgetter('ProductSalesCount'), reverse=True)
                    return Response(q)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TotalSalesVendorPieChart(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                Storeid=request.data.get("Storeid")
                LastStartDate=request.data.get("LastStartDate",None)
                EndStartDate=request.data.get("EndStartDate",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    order=Order.objects.filter(OrderDate__icontains=EndDate).filter(Order_Status="Delivered").filter(Store=Storeid)
                    order1=Order.objects.filter(OrderDate__icontains=StartDate).filter(Order_Status="Delivered").filter(Store=Storeid)
                    if order1.count()!=0:
                        percentage=(order.count()- order1.count())*100/order1.count()
                        result = {"Pickup": 0, "Delivery": 0,"Curbsibe":0,"TotalSales":0,"Percentage":round(percentage,2),"Growth": (order.count()) >= (order1.count())}
                        for i in order:
                            result["TotalSales"] +=i.subtotal
                            if i.Order_Type == "Pickup":
                                result["Pickup"] += i.subtotal
                            elif i.Order_Type == "Delivery":
                                result["Delivery"] += i.subtotal
                            elif i.Order_Type == "Delivery and Pickup":
                                result["Curbsibe"] += i.subtotal
                    
                        return Response(result)
                    else:
                        result = {"Pickup": 0, "Delivery": 0,"Curbsibe":0,"TotalSales":0,"Percentage":0,"Growth": True}
                        for i in order:
                            result["TotalSales"] +=i.subtotal
                            if i.Order_Type == "Pickup":
                                result["Pickup"] += i.subtotal
                            elif i.Order_Type == "Delivery":
                                result["Delivery"] += i.subtotal
                            elif i.Order_Type == "Delivery and Pickup":
                                result["Curbsibe"] += i.subtotal
                        return Response(result)
                else:
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    lastStartDate=timezone.make_aware(datetime.strptime(LastStartDate, '%Y-%m-%d'))
                    endStartDate=timezone.make_aware(datetime.strptime(EndStartDate, '%Y-%m-%d'))
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=(today + timedelta(days=1))).filter(Order_Status="Delivered").filter(Store=Storeid)
                    order1=Order.objects.filter(OrderDate__gte=lastStartDate,OrderDate__lt=endStartDate).filter(Order_Status="Delivered").filter(Store=Storeid)
                    if order1.count()!=0:
                        percentage=(order.count()- order1.count())*100/order1.count()
                        result = {"Pickup": 0, "Delivery": 0,"Curbsibe":0,"TotalSales":0,"Percentage":round(percentage,2),"Growth": (order.count()) >= (order1.count())}
                        for i in order:
                            result["TotalSales"] +=i.subtotal
                            if i.Order_Type == "Pickup":
                                result["Pickup"] += i.subtotal
                            elif i.Order_Type == "Delivery":
                                result["Delivery"] += i.subtotal
                            elif i.Order_Type == "Delivery and Pickup":
                                result["Curbsibe"] += i.subtotal
                    
                        return Response(result)
                    else:
                        result = {"Pickup": 0, "Delivery": 0,"Curbsibe":0,"TotalSales":0,"Percentage":0,"Growth": True}
                        for i in order:
                            result["TotalSales"] +=i.subtotal
                            if i.Order_Type == "Pickup":
                                result["Pickup"] += i.subtotal
                            elif i.Order_Type == "Delivery":
                                result["Delivery"] += i.subtotal
                            elif i.Order_Type == "Delivery and Pickup":
                                result["Curbsibe"] += i.subtotal
                        return Response(result)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SalesPerformanceVendorGraph(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                SelectTime=request.data.get("SelectTime",None)
                store=request.data.get("store")
                StartDate = request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate")
                if SelectTime=="Today":
                    z=[]
                    TotalPrice=0
                    UnitSold=0
                    order=Order.objects.filter(OrderDate__icontains=StartDate ).filter(Order_Status="Delivered").filter(Store_id=store)
                    
                    for i in order:
                        TotalPrice += i.subtotal
                        for j in i.Product:
                            UnitSold += j["Cart_Quantity"]
                    result = {"Date":StartDate,"TotalPrice":TotalPrice,"UnitSold":UnitSold}
                    z.append(result)
                    return Response(z)

                if SelectTime=="ThisWeek":
                    z=[]
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    while week <= today:
                        TotalPrice=0
                        UnitSold=0
                        order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today ).filter(Order_Status="Delivered").filter(Store_id=store)
                        
                        for i in order:
                            TotalPrice += i.subtotal
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                        result = {"Date":week.strftime("%A"),"TotalPrice":TotalPrice,"UnitSold":UnitSold}
                        z.append(result)
                        week=week + timedelta(days=1)
                    return Response(z)
                if SelectTime=="ThisMonth":
                    z=[]
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    while week <= today:
                        UnitSold=0
                        TotalPrice=0
                        order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today ).filter(Order_Status="Delivered").filter(Store_id=store)
                        for i in order:
                            TotalPrice += i.subtotal
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                        result = {"Date":week.strftime("%x"),"TotalPrice":TotalPrice,"UnitSold":UnitSold}
                        z.append(result)
                        week=week + timedelta(days=1)
                    return Response(z)
                if SelectTime=="ThisYear":
                    z=[]
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    while week <= today:
                        UnitSold=0
                        TotalPrice=0
                        order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Order_Status="Delivered").filter(Store_id=store)
                        for i in order:
                            TotalPrice += i.subtotal
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                        result = {"Date":week.strftime("%B"),"TotalPrice":TotalPrice,"UnitSold":UnitSold}
                        z.append(result)
                        week += relativedelta(months=+1)
                    return Response(z)
                else:
                    z=[]
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    while week <= today:
                        UnitSold=0
                        TotalPrice=0
                        order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Order_Status="Delivered").filter(Store_id=store)
                        for i in order:
                            TotalPrice += i.subtotal
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                        result = {"Date":week.strftime("%x"),"TotalPrice":TotalPrice,"UnitSold":UnitSold}
                        z.append(result)
                        week += timedelta(days=1)
                    return Response(z)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)    
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ProductDetailsVendor(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                Storeid=request.data.get("Storeid")
                product=Product.objects.filter(Store_id=Storeid).order_by("-created")
                serialize=Serializer_Product(product,many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ViewProductById(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                id=request.data.get("id")
                Storeid=request.data.get("Storeid")
                product=Product.objects.filter(Store_id=Storeid).filter(id=id)
                serialize=Serializer_Product(product,many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EditProductById(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                id=request.data.get("id")
                Storeid=request.data.get("Storeid")
                Weightid=request.data.get("Weightid")
                prices=request.data.get("Multiple_prices")
                DeleteImageId=request.data.get("DeleteImageId")
                if Weightid:
                    WeightId=ProductWeight.objects.get(id=Weightid)
                    serialize=ProductWeightSerializer(WeightId,data=request.data, partial=True)
                    if serialize.is_valid():
                        serialize.save(Price=json.loads(prices))
                if id:
                    ProductId = Product.objects.filter(Store_id=Storeid).filter(id=id).first()
                    serialize=Serializer_Product(ProductId,data=request.data, partial=True)
                    if serialize.is_valid():
                        serialize.save()
                if DeleteImageId :
                            ProductId = Product.objects.get(id=id)
                            for j in json.loads(DeleteImageId):
                                User = get_object_or_404(ProductImage, id=j)
                                User.delete()
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DeleteProductById(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                User = get_object_or_404(Product, id=id)
                User.delete()
                return Response({"status": "success", "data": "Deleted"})
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
class OrderByStoreId(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                Storeid=request.data.get("Storeid")
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    order=Order.objects.filter(Store=Storeid).filter(OrderDate__icontains=StartDate).order_by("-OrderDate")
                    serialize=Serializer_Order(order,many=True)
                    return Response(serialize.data)
                else:
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    order=Order.objects.filter(Store=Storeid).filter(OrderDate__gte=week,OrderDate__lte=(today +timedelta(days=1))).order_by("-OrderDate")
                    serialize=Serializer_Order(order,many=True)
                    return Response(serialize.data)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AllReviews(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    Productreview=Review.objects.filter(created_at__icontains=StartDate)
                    Storereview=StoreReview.objects.filter(created_at__icontains=StartDate)
                    serialize=ReviewSerializer(Productreview,many=True)
                    serialize1=StoreReviewSerializer(Storereview,many=True)
                    data=serialize.data+serialize1.data
                    return Response(data)
                else:
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    Productreview=Review.objects.filter(created_at__gte=week,created_at__lte=(today +timedelta(days=1)))
                    Storereview=StoreReview.objects.filter(created_at__gte=week,created_at__lte=(today +timedelta(days=1)))
                    serialize=ReviewSerializer(Productreview,many=True)
                    serialize1=StoreReviewSerializer(Storereview,many=True)
                    data=serialize.data+serialize1.data
                    return Response(data)

            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ReviewsByStore(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                StoreId=request.data.get("StoreId")
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    Productreview=Review.objects.filter(created_at__icontains=StartDate).filter(product__Store_id=StoreId)
                    Storereview=StoreReview.objects.filter(created_at__icontains=StartDate).filter(Store=StoreId)
                    serialize=ReviewSerializer(Productreview,many=True)
                    serialize1=StoreReviewSerializer(Storereview,many=True)
                    data=serialize.data+serialize1.data
                    return Response(data)
                else:
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    Productreview=Review.objects.filter(created_at__gte=week,created_at__lte=(today +timedelta(days=1))).filter(product__Store_id=StoreId)
                    Storereview=StoreReview.objects.filter(created_at__gte=week,created_at__lte=(today +timedelta(days=1))).filter(Store=StoreId)
                    serialize=ReviewSerializer(Productreview,many=True)
                    serialize1=StoreReviewSerializer(Storereview,many=True)
                    data=serialize.data+serialize1.data
                    return Response(data)

            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DeleteReviews(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                StoreId=request.data.get("StoreId",None)
                productId=request.data.get("productId",None)

                if productId:
                    Productreview=Review.objects.get(id=productId)
                    Productreview.delete()
                    return Response('Deleted')
                elif StoreId:
                    Storereview=StoreReview.objects.get(id=StoreId)
                    Storereview.delete()
                    return Response('Deleted')
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class TotalSalesPage(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                delivery=0
                pickup=0
                curbsidepickup=0
                TotalSale=0
                LastStartDate=request.data.get("LastStartDate",None)
                EndStartDate=request.data.get("EndStartDate",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    z=[]
                    store=Stores.objects.all()
                    for i in store:
                        order=Order.objects.filter(OrderDate__icontains=EndDate).filter(Order_Status="Delivered").filter(Store=i.id)
                        order1=Order.objects.filter(OrderDate__icontains=StartDate).filter(Order_Status="Delivered").filter(Store=i.id)
                        for j in order:
                            if j.Order_Type == 'Delivery':
                                delivery += j.subtotal
                            elif j.Order_Type == 'Pickup':
                                pickup += j.subtotal
                            elif j.Order_Type == 'Delivery and Pickup':
                                curbsidepickup += j.subtotal
                            response = {"StoreName": i.Store_Name, "delivery": delivery, "Pickup": pickup, "curbsidepickup": curbsidepickup}
                            z.append(response)
                    for l in z:
                        TotalSale+=l["delivery"]+l["Pickup"]+l["curbsidepickup"]
                    z.append({"TotalSales":TotalSale})
                    return Response(z)
                else:
                    z=[]
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    lastStartDate=timezone.make_aware(datetime.strptime(LastStartDate, '%Y-%m-%d'))
                    endStartDate=timezone.make_aware(datetime.strptime(EndStartDate, '%Y-%m-%d'))
                    store=Stores.objects.all()
                    for i in store:
                        delivery=0
                        pickup=0
                        curbsidepickup=0
                        TotalSale=0
                        previous=0
                        order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=(today + timedelta(days=1))).filter(Order_Status="Delivered").filter(Store=i.id)
                        order1=Order.objects.filter(OrderDate__gte=lastStartDate,OrderDate__lt=endStartDate).filter(Order_Status="Delivered").filter(Store=i.id)
                        for j in order:
                            if j.Order_Type == 'Delivery':
                                delivery += j.subtotal
                            elif j.Order_Type == 'Pickup':
                                pickup += j.subtotal
                            elif j.Order_Type == 'Delivery and Pickup':
                                curbsidepickup += j.subtotal
                                for k in order1:
                                    previous += k.subtotal
                        response = {"StoreName": i.Store_Name, "delivery": delivery, "Pickup": pickup, "curbsidepickup": curbsidepickup}
                        z.append(response)
                    for l in z:
                        TotalSale+=l["delivery"]+l["Pickup"]+l["curbsidepickup"]
                    z.append({"TotalSales":TotalSale,"Growth":TotalSale>previous})
                    return Response(z)
                            
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class UserOrderandReview(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,id=None):
        try:
            user=request.user.user_type
            if user=='Admin':
                customer=User.objects.filter(id=id)
                serialize=UserSerializer(customer,many=True)
                order=Order.objects.filter(created_by=id).count()
                storereview=StoreReview.objects.filter(user=id).count()
                productreview=Review.objects.filter(user=id).count()
                TotalReview=storereview+productreview
                data=list(serialize.data)
                data.append({"order":order,"reviews":TotalReview})
                    
                return Response(data)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class OrderbyUser(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,id=None):
        try:
            user=request.user.user_type
            if user=='Admin':
                order=Order.objects.filter(created_by=id)
                serialize=Serializer_Order(order,many=True)
                return Response(serialize.data)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReviewbyUser(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,id=None):
        try:
            user=request.user.user_type
            if user=='Admin':
                storereview=StoreReview.objects.filter(user=id)
                productreview=Review.objects.filter(user=id)
                serializestore=StoreReviewSerializer(storereview,many=True).data
                serializerproduct=ReviewSerializer(productreview,many=True).data
                serialize=serializestore+serializerproduct
                return Response(serialize)
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PopularLocationGraph(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    z=[]
                    order=Order.objects.filter(OrderDate__icontains=StartDate).filter(Order_Status="Delivered")
                    if order.count()>0:
                        for i in order:
                            z.append({"State":i.State,"TotalSale":i.subtotal}) 
                            
                            temp = {}
                            for data in z:
                                if data["State"] in temp:
                                    temp[data["State"]]["TotalSale"] += data["TotalSale"]
                                else:
                                    temp[data["State"]] = data.copy()
                            category_delivery_list = list(temp.values())
                        return Response(category_delivery_list)
                    else:
                        return Response(z)
                else:
                    z=[]
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lte=(today+timedelta(days=1))).filter(Order_Status="Delivered")
                    if order.count()>0:
                        for i in order:
                            z.append({"State":i.State,"TotalSale":i.subtotal}) 
                            
                            temp = {}
                            for data in z:
                                if data["State"] in temp:
                                    temp[data["State"]]["TotalSale"] += data["TotalSale"]
                                else:
                                    temp[data["State"]] = data.copy()
                            category_delivery_list = list(temp.values())
                        return Response(category_delivery_list)
                    else:
                        return Response(z)
                    
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PopularLocationGraphPage(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            user=request.user.user_type
            if user=='Admin':
                LastStartDate=request.data.get("LastStartDate",None)
                EndStartDate=request.data.get("EndStartDate",None)
                StartDate=request.data.get("StartDate",None)
                EndDate=request.data.get("EndDate",None)
                SelectTime=request.data.get("SelectTime",None)
                if SelectTime=="Today":
                    z=[]
                    previousSale=0
                    totalsale=0
                    AllSale=0
                    order=Order.objects.filter(OrderDate__icontains=StartDate).filter(Order_Status="Delivered")
                    order1=Order.objects.filter(OrderDate__icontains=EndDate).filter(Order_Status="Delivered")
                    for k in order1:
                        previousSale=previousSale+k.subtotal
                    if order.count()>0:
                        for i in order:
                            totalsale =totalsale + i.subtotal
                            z.append({"State":i.State,"TotalSale":i.subtotal}) 
                            
                            temp = {}
                            for data in z:
                                if data["State"] in temp:
                                    temp[data["State"]]["TotalSale"] += data["TotalSale"]
                                else:
                                    temp[data["State"]] = data.copy()
                            category_delivery_list = list(temp.values())
                        for j in category_delivery_list:
                            AllSale=AllSale+j["TotalSale"]
                        category_delivery_list.append({"AllSale":AllSale,"Growth":AllSale>previousSale})    
                        return Response(category_delivery_list)
                        
                    else:
                        return Response(z)
                else:
                    z=[]
                    previousSale=0
                    totalsale=0
                    AllSale=0
                    week=timezone.make_aware(datetime.strptime(StartDate, '%Y-%m-%d'))
                    today=timezone.make_aware(datetime.strptime(EndDate, '%Y-%m-%d'))
                    lastStartDate=timezone.make_aware(datetime.strptime(LastStartDate, '%Y-%m-%d'))
                    endStartDate=timezone.make_aware(datetime.strptime(EndStartDate, '%Y-%m-%d'))
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lte=(today+timedelta(days=1))).filter(Order_Status="Delivered")
                    lastorder=Order.objects.filter(OrderDate__gte=lastStartDate,OrderDate__lte=endStartDate).filter(Order_Status="Delivered")
                    for k in lastorder:
                        previousSale=previousSale+k.subtotal
                    if order.count()>0:
                        for i in order:
                            totalsale =totalsale + i.subtotal
                            z.append({"State":i.State,"TotalSale":i.subtotal}) 
                            
                            temp = {}
                            for data in z:
                                if data["State"] in temp:
                                    temp[data["State"]]["TotalSale"] += data["TotalSale"]
                                else:
                                    temp[data["State"]] = data.copy()
                            category_delivery_list = list(temp.values())
                        for j in category_delivery_list:
                            AllSale=AllSale+j["TotalSale"]
                        category_delivery_list.append({"AllSale":AllSale,"Growth":AllSale>previousSale})    
                        return Response(category_delivery_list)
                    else:
                        return Response(z)
                    
            else:
                return Response("Not Authorized",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UserProfileAdminSideBar(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,format=None):
        try:
            data=request.user
            user=User.objects.filter(id=data.id).first()
            roles=user.Roles.all()
            serialize=UserSerializer(user).data
            # for j in serialize:
            response={"UserName":user.username,"Image":serialize["image"],"Designations":[]}
            for i in roles:
                if len(response["Designations"])>=1:
                    response["Designations"].append(i.RoleTitle)
                else:
                    response["Designations"].append(i.RoleTitle)
            return Response(response)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)