from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from AdminPanel.tokens import create_jwt_pair_for_user
from rest_framework import status
from Ecommerce.settings import EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_PORT
import smtplib,random,json
from AdminPanel.models import *
from AdminPanel.serializer import *
from django.shortcuts import get_object_or_404
from .models import *
from UserPanel.models import *
from UserPanel.serializer import *
from .serializer import *
from UserPanel.serializer import *
from django.utils import timezone
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EmailBody='''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <div>
       <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> Dear {username},</h4>

        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">  Thank you for choosing Cannabaze POS! To access your vendor panel, please use the following One-Time Password</h4>
            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> OTP:<b>{otp}</b></h4>
            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> This OTP is valid for a single login session and should be used within 10 minutes.</h4>
        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">  If you did not request this OTP or have any concerns about your account security, please contact our support team immediately.</h4>
        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">  Cannabaze POS</h4>
        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">  Phone:  <a  style="color:#0084ff;font-size:13px;font-weight: 500;"  href="tel:+1 (209) 655-0360">+1 (209) 655-0360</a></h4>
            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> Email: <a  style="color:#0084ff;font-size:13px;font-weight: 500;"  href="mailto:info@weedx.io">info@weedx.io</a></h4>
        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">  Website: <a  style="color:#0084ff;font-size:13px;font-weight: 500;"  href="https://cannabaze.com/"> cannabaze.com</a></h4>

            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> Note: Do not share your OTP with anyone. Cannabaze POS will never ask you for your OTP through email or any other means.</h4>

            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> Best regards,</h4>
            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> Cannabaze POS Team</h4>
    </div>
</body>
</html>'''

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
    email_message['Subject'] = "Your Cannabaze POS Vendor Panel Login OTP"
    email_message.attach(MIMEText(EmailBody.format(username=user.username,otp=str(Otp)), "html"))
    email_string = email_message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_from, password)
        server.sendmail(email_from, to_emails, email_string)    
        


EmailBody1='''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <div>
       <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> Dear {username},</h4>

        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">  Thank you for signing up with Cannabaze POS! We're excited to have you on board. To complete your registration, please use the following One-Time Password (OTP):</h4>
            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> OTP:<b>{otp}</b></h4>
            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> This OTP is valid for a limited time. Please use it to confirm your account within the next 10 minutes.</h4>
        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">  If you did not sign up for Cannabaze POS or have any concerns about your account, please contact our support team immediately.</h4>
        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">  Cannabaze POS</h4>
        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">  Phone:  <a  style="color:#0084ff;font-size:13px;font-weight: 500;"  href="tel:+1 (209) 655-0360">+1 (209) 655-0360</a></h4>
            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> Email: <a  style="color:#0084ff;font-size:13px;font-weight: 500;"  href="mailto:info@weedx.io">info@weedx.io</a></h4>
        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">  Website: <a  style="color:#0084ff;font-size:13px;font-weight: 500;"  href="https://cannabaze.com/"> cannabaze.com</a></h4>

            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> Note: Do not share your OTP with anyone. Cannabaze POS will never ask you for your OTP through email or any other means.</h4>

            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> Best regards,</h4>
            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> Cannabaze POS Team</h4>
    </div>
</body>
</html>'''

def RegisterEmailSend(to_emails='',from_email=''):
    Otp = random.randint(1000, 9999)
    user = User.objects.get(email=to_emails)
    user.otp = Otp
    user.save()
    email_from = EMAIL_HOST_USER
    password = EMAIL_HOST_PASSWORD
    email_message = MIMEMultipart()
    email_message['From'] = from_email
    email_message['To']=to_emails
    email_message['Subject'] = "Welcome to Cannabaze POS - Confirm Your Account"
    email_message.attach(MIMEText(EmailBody1.format(username=user.username,otp=str(Otp)), "html"))
    email_string = email_message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_from, password)
        server.sendmail(email_from, to_emails, email_string)
        
EmailBody2='''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <div>
       <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> Dear {username},</h4>

        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">  We received a request to reset the password associated with your Cannabaze POS vendor panel account. To proceed with the password reset, please use the following One-Time Password (OTP):</h4>
            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> OTP:<b>{otp}</b></h4>
            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> This OTP is valid for a single use and should be entered within the next 10 minutes.</h4>
        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">  If you did not request a password reset or have any concerns about your account security, please contact our support team immediately.</h4>
        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">  Cannabaze POS</h4>
        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">  Phone:  <a  style="color:#0084ff;font-size:13px;font-weight: 500;"  href="tel:+1 (209) 655-0360">+1 (209) 655-0360</a></h4>
            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> Email: <a  style="color:#0084ff;font-size:13px;font-weight: 500;"  href="mailto:info@weedx.io">info@weedx.io</a></h4>
        <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;">  Website: <a  style="color:#0084ff;font-size:13px;font-weight: 500;"  href="https://cannabaze.com/"> cannabaze.com</a></h4>

            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> Note: Do not share your OTP with anyone. Cannabaze POS will never ask you for your OTP through email or any other means.</h4>

            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> Best regards,</h4>
            <h4 style="color:#4e4e4e;font-size:13px;font-weight: 400;"> Cannabaze POS Team</h4>
    </div>
</body>
</html>'''

def ForgetEmailSend(to_emails='',from_email=''):
    Otp = random.randint(1000, 9999)
    user = User.objects.get(email=to_emails)
    user.otp = Otp
    user.save()
    email_from = EMAIL_HOST_USER
    password = EMAIL_HOST_PASSWORD
    email_message = MIMEMultipart()
    email_message['From'] = from_email
    email_message['To']=to_emails
    email_message['Subject'] = "Reset Your Cannabaze POS Vendor Panel Password"
    email_message.attach(MIMEText(EmailBody2.format(username=user.username,otp=str(Otp)), "html"))
    email_string = email_message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_from, password)
        server.sendmail(email_from, to_emails, email_string)



class VerifyOtpLogin(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            email = request.data.get("email")
            otp = request.data.get("OTP") 
            user = User.objects.filter(email=email).first()
            if user.user_type=="Vendor":
                if user.otp != int(otp):
                    return Response({
                        'message': 'Something goes wrong',
                        'data': 'invalid Otp'
                    },status=status.HTTP_400_BAD_REQUEST)
                user = User.objects.get(email=email)
                if user is not None:
                    # if user.status =="Active" and store.Status == "Active":
                    store=Stores.objects.filter(created_by=user)
                    active=store.filter(Status='Active')
                    if store:
                        if active:
                                tokens = create_jwt_pair_for_user(user)

                                response = {"message": "Login Successfull", "tokens": tokens}
                                return Response(data=response, status=status.HTTP_200_OK)
                        else:
                                return Response({"message":"Our Team Will Contact You Soon"},status=status.HTTP_202_ACCEPTED)
                    else:
                        return Response({"message":"Store Not Found"},status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response(data={"message": "Invalid email or password"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Not Authorized")
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            content = {"user": str(request.user), "auth": str(request.auth)}

            return Response(data=content, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ForgetPasswordAPI(APIView):
    serializer_class = ChangePasswordSerializer
    model = User

    def get_object(self, queryset=None):
        try:
            obj = self.request.user
            return obj
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            serializer = ChangePasswordSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                ForgetEmailSend(
                    from_email='smtpselnox@gmail.com', to_emails=email)
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'mail sent successfully',
                    'data': {"Otp_Sent_To": email}
                }

                return Response(response)
            else:
                return Response({"message": "Something Goes Wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ValidateOTPForgetPassword(APIView):
    def post(self,request=None):
        try:
            email=request.data.get("email")
            otp=request.data.get("otp")
            user=User.objects.filter(email=email).first()
            if not user.exists():
                return Response({
                    'message': 'Something goes wrong',
                    'data': 'invalid Email'
                },status=status.HTTP_400_BAD_REQUEST)
            if user.otp != int(otp):
                return Response({
                    'message': 'Something goes wrong',
                    'data': 'invalid Otp'
                },status=status.HTTP_400_BAD_REQUEST)
            if user.otp == int(otp):
                return Response({
                    "message":"Otp matched",
                    "data":"OTP matched SuccessFully"
                },status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class VerifyOtpForgetPassword(APIView):
    def get_object(self, queryset=None):

        obj = self.request.user
        return obj

    def post(self, request):
        try:
            self.object = self.get_object()
            data = request.data
            serializer = PasswordReseetSerializer(data=data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                new_password = serializer.validated_data['new_password']

                user = User.objects.get(email=email)
                if not user.exists():
                    return Response({
                        'message': 'Something goes wrong',
                        'data': 'invalid Email'
                    },status=status.HTTP_400_BAD_REQUEST)
               
                if len(new_password) > 5:
                    self.object.set_password(
                        serializer.data.get("new_password"))
                    self.object.save()

                    return Response({
                        'message': 'Password is Update',
                    },status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({
                        'message': 'Password must be Strong',
                    },status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginAPI(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            if email:
                if password:
                    serializer = LoginSerializer(data=request.data)
                    if serializer.is_valid():
                        email = serializer.validated_data['email']
                        user=User.objects.get(email=email)
                        if user:
                            if user.user_type=="Vendor":
                                send_OneToOneMail(
                                    from_email='smtpselnox@gmail.com', to_emails=email)
                                return Response({
                                    'message': 'Email sent',
                                    'data': {"Otp_Sent_to": email}
                                },status=status.HTTP_200_OK)
                            else:
                                return Response({"error": "Not Vendor"}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({"error":"Vendor Not Register"},status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"error": "Enter the valid Password"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Enter the valid Email"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Get User API


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = UserSerializer

    def get_object(self):
        try:
            return self.request.user
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Class based view to register user
class RegisterAPI(generics.GenericAPIView):
    serializer_class =RegisterSerializer

    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get("username")
            email = request.data.get("email")
            serializer = RegisterSerializer(data=request.data)
            user = User.objects.filter(email=email)
            username = User.objects.filter(username=username)
            if username.exists():
                data = username.first()
                old_otp = data.otp
                if old_otp == None:
                    RegisterEmailSend(
                        from_email='smtpselnox@gmail.com', to_emails=email)
                    return Response({"message": {"Otp sent to": email}},status=status.HTTP_200_OK)
                else:
                    return Response({"username": "Username is already Registered"},status=status.HTTP_400_BAD_REQUEST)
                
            elif user.exists():
                data = user.first()
                old_otp = data.otp
                if old_otp == None:
                    send_OneToOneMail(
                        from_email='smtpselnox@gmail.com', to_emails=email)
                    return Response({"message": {"Otp sent to": email}},status=status.HTTP_200_OK)
                else:
                    return Response({"email": "email is already Registered"},status=status.HTTP_400_BAD_REQUEST)

            else:
                if serializer.is_valid():
                    user = serializer.save(user_type='Vendor')    
                    send_OneToOneMail(
                        from_email='smtpselnox@gmail.com', to_emails=email)
                    return Response({"message": {"Otp sent to": email}},status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OTPverificationForRegisterAPI(APIView):
    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get("email")
            otp = request.data.get("OTP")
            user = User.objects.filter(email=email).first()
            if user.otp !=int(otp):
                return Response({
                    'message': 'Something goes wrong',
                    'data': 'invalid Otp'
                },status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(email=email)
            if user is not None:
                return Response({
                    "user": UserSerializer(user).data,
                    # "token": AuthToken.objects.create(user)[1]
                },status=status.HTTP_200_OK)
            else:
                return Response({"message": "User is already Register"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPassword(APIView):
    serializer_class = PasswordReseetSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get(self, queryset=None):
        try:
            obj = self.request.user
            return obj
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get()
            serializer = PasswordReseetSerializer(data=request.data)

            if serializer.is_valid():
                if not self.object.check_password(serializer.data.get("old_password")):
                    return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
                self.object.set_password(serializer.data.get("new_password"))
                self.object.save()
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Password updated successfully'
                }

                return Response(response)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#Product
class GetProduct(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = Product.objects.filter(created_by=request.user) #created_by=self.request.user)
            serialize = Serializer_Product(User, many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddProduct(APIView):
    permission_classes = [IsAuthenticated]
 
    def post(self, request):
        try:
            serializer = Serializer_Product(data=request.data, partial=True)
            print(serializer)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class UpdateProduct(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            Productid=request.data.get("Productid")
            Weightid=request.data.get("Weightid")
            prices=request.data.get("Multiple_prices")
            images=request.FILES.get('Multiple_images')
            DeleteImageId=request.data.get("DeleteImageId")
            if Weightid:
                WeightId=ProductWeight.objects.get(id=Weightid)
                serialize=ProductWeightSerializer(WeightId,data=request.data, partial=True)
                if serialize.is_valid():
                    serialize.save(Price=json.loads(prices))
            if Productid:
                ProductId = Product.objects.get(id=Productid)
                serialize=Serializer_Product(ProductId,data=request.data, partial=True)
                if serialize.is_valid():
                    serialize.save(modified_by=request.user.username)
            if DeleteImageId :
                        ProductId = Product.objects.get(id=Productid)
                        for j in json.loads(DeleteImageId):
                            User = get_object_or_404(ProductImage, id=j)
                            User.delete()
                
            return Response({"status": "success","data": serialize.data}, status=status.HTTP_200_OK)
 
                                           
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteProduct(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id=None):
        try:
            User = get_object_or_404(Product, id=id)
            User.delete()
            return Response({"status": "success", "data": "Deleted"})
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
     
#Brand
class GetBrand(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = Brand.objects.filter(created_by=request.user)
            serialize = Serializer_Brand(User, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class AddBrand(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            name=request.data.get("name")
            Brand_description=request.data.get("Brand_description")
            Brand_Logo=request.data.get("Brand_Logo")
            if name:
                if Brand_description:
                    if Brand_Logo:
                        if len(name)>=3:
                            serializer = Serializer_Brand(data=request.data, partial=True)
                            if serializer.is_valid():
                                serializer.save(created_by=request.user)
                                return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                            else:
                                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({ "name": "Enter atleast 3 Alhabet"},status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"Brand_Logo": "Enter the Logo of Brand"},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"Brand_description":"Enter the Brand Description"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"name": "Enter the valid Name"},status=status.HTTP_400_BAD_REQUEST)
                        
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateBrand(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            name=request.data.get("name")
            Brand_description=request.data.get("Brand_description")
            Brand_Logo=request.data.get("Brand_Logo")
            if name:
                if Brand_description:
                    if Brand_Logo:
                        if len(name)>=3:
                            User = Brand.objects.get(id=id)
                            serializer = Serializer_Brand(User, data=request.data, partial=True)
                            if serializer.is_valid():
                                serializer.save(modified_by=self.request.user)
                                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                            else:
                                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({ "name": "Enter atleast 3 Alhabet"},status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"Brand_Logo": "Enter the Logo of Brand"},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"Brand_description":"Enter the Brand Description"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"name": "Enter the valid Name"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Stores 
class GetStores(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = Stores.objects.filter(created_by=request.user)
            active=Stores.objects.filter(Status='Active')
            if User and active:
                serialize = Serializer_Store(User, many=True)
                return Response(serialize.data)
            else:
                return Response("No Store Available")
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

class AddStores(APIView):
    def post(self, request):
        try:
            email=request.data.get("email")
            Stores_MobileNo=request.data.get("Stores_MobileNo")
            LicenceNo=request.data.get("LicenceNo")
            a=Stores.objects.filter(Stores_MobileNo=Stores_MobileNo)
            s=Stores.objects.filter(LicenceNo=LicenceNo)
            if len(Stores_MobileNo) == 15:
                if a.exists():
                    return Response({"Stores_MobileNo":"Mobile no. is already Exist"},status=status.HTTP_400_BAD_REQUEST) 
                elif s.exists():
                    return Response({"LicenceNo":"Licence No. already Exist"},status=status.HTTP_400_BAD_REQUEST)
                else:         
                    user=User.objects.get(email=email)      
                    serializer = Serializer_Store(data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save(created_by=user) #created_by=self.request.user)
                        return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"Stores_MobileNo":"Enter the valid No."},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateStores(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:

            User = Stores.objects.get(id=id)
            serializer = Serializer_Store(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=self.request.user)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#NET Weight 
class GetNet_Weight(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = Net_Weight.objects.filter(created_by=self.request.user)
            serialize = Serializer_Net_Weight(User, many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class AddNet_Weight(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            Weight_type=request.data.get("Weight_type")
            Weight_Price=request.data.get("Weight_Price")
            if Weight_type:
                if Weight_Price:
                    if len(Weight_type)>=3:
                        serializer = Serializer_Net_Weight(data=request.data, partial=True)
                        if serializer.is_valid():
                            serializer.save(created_by=request.user)
                            return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
                        else:
                            return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"Weight_type": "Enter atleast 3 alphabet"},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({ "Weight_Price":"Enter the valid Price"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({ "Weight_type":"Enter the Weight Type"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateNet_Weight(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            Weight_type=request.data.get("Weight_type")
            Weight_Price=request.data.get("Weight_Price")
            if Weight_type:
                if Weight_Price:
                    if len(Weight_type)>=3:
                        User = Net_Weight.objects.get(id=id)
                        serializer = Serializer_Net_Weight(User, data=request.data, partial=True)
                        if serializer.is_valid():
                            serializer.save(modified_by=self.request.user)
                            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
                        else:
                            return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"Weight_type": "Enter atleast 3 alphabet"},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({ "Weight_Price":"Enter the valid Price"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({ "Weight_type":"Enter the Weight Type"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Category Api
class GetCategories(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = Category.objects.select_related().all()
            serialize = Serializer_Category(User, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

#Sub Category Api
class GetSubCategories(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = SubCategory.objects.select_related().all()
            serialize = Serializer_SubCategory(User, many=True)
            return Response({"data":serialize.data},status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FilterbyCategory(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,id=None):
        try:
            User = SubCategory.objects.filter(category=id)
            active=User.filter(Status="Active")
            if active:
                serializer = Serializer_SubCategory(active,many=True)
                
                return Response({"status": "success", "data":serializer}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
class FilterStatesByCountry(APIView):
    def get(self,request,id=None):
        try:
            User = States.objects.filter(Country_id=id)
            active=User.filter(Status="Active")
            if active:
                serializer = Serializer_States(active,many=True)
                return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FilterCitiesByStates(APIView):
    def get(self,request,id=None):
        try:
            User = Cities.objects.filter(States_id=id)
            active=User.filter(Status="Active")
            if active:
                serializer = Serializer_Cities(active,many=True)
                return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        
class ActiveCategory(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            User=Category.objects.filter(Status="Active").using("Product")
            serializer = Serializer_Category(User,many=True)
            return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
class ActiveSubCategory(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            User=SubCategory.objects.filter(Status="Active").order_by("name")
            serializer = Serializer_SubCategory(User,many=True)
            return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ActiveCountry(APIView):
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
            User=Stores.objects.filter(Status="Active").filter(created_by=request.user)
            if User:
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


from .serializer import *

class CategoryOnProduct(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,id=None):
        try:
            product=Product.objects.filter(Store_id=id)
            serialize=Serializer_CategoryinProduct(product,many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetOrderByVendors(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            a=Stores.objects.filter(created_by=request.user).first()
            RecentOrder=Order.objects.filter(Store=a)
            serialize=Serializer_Order(RecentOrder,many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteProductImage(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self, request, id=None):
        try:
            User = get_object_or_404(ProductImage, id=id)
            User.delete()
            return Response({"status": "success", "data": "Deleted"})
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StatusVendor(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            User = Product.objects.get(id=id)
            serializer = Serializer_Product(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=self.request.user)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TotalCountOrder(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,format=None):
        try:
            a=Stores.objects.filter(created_by=request.user).first()
            s=Order.objects.filter(Store=a).order_by('created_by')
            NewOrder=s.filter(Order_Status="Pending").count()
            PendingOrder=s.filter(Order_Status="Processing").count()
            ConfirmOrder=s.filter(Order_Status="Delivered").count()
            CancelOrder=s.filter(Order_Status="Cancel").count()
            return Response({"Data":[{"title":"New Order","total":NewOrder},
                                    {"title":"Pending Order","total":PendingOrder},
                                    {"title":"Confirm Order","total":ConfirmOrder},
                                    {"title":"Cancel Order","total":CancelOrder},]})
        except Exception as e:
            return Response({'error' : str(e)},status=500) 

class GetApplyCoupoun(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User =Coupoun.objects.filter(created_by=request.user)
            serialize = Serializer_Coupoun(User, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res
class AddApplyCoupoun(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            q=[]
            
            a=request.data
            serializer = Serializer_Coupoun(data=request.data, partial=True)
            if serializer.is_valid():
                    serializer.save(created_by=request.user)
                    s=Coupoun.objects.filter(created_by=request.user).last()
                    for i in s.product:
                        z=ProductWeight.objects.filter(product_id=i["Product_Id"]).first()
                        for j in z.Price:
                            if j["id"]==i["Price_Id"]:
                                asd={"id":s.id}
                                result=(Merge(a,asd))
                                j["Coupoun"].append(result)
                                q.append({"Price":z.Price}) 
                        for n in q:
                            weight=ProductWeightSerializer(z,data=n,partial=True)
                            if weight.is_valid():
                                weight.save()
                    return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateApplyCoupoun(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            User = Coupoun.objects.get(id=id)
            serializer = Serializer_Coupoun(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.username)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DeleteApplyCoupoun(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            q=[]
            User=Coupoun.objects.filter(id=id).first()
            for i in User.product:
                a=ProductWeight.objects.filter(product=i["Product_Id"]).first()
                for j in a.Price:
                    for l in j["Coupoun"]:
                        
                        if User.DiscountCode==l["DiscountCode"]:
                            j["Coupoun"].remove(l)
                            q.append({"Price":a.Price})
                    for n in q:
                            z=ProductWeightSerializer(a,data=n,partial=True)
                            if z.is_valid():
                                z.save()
            User.delete()
            return Response({"status": "success", "data": "Deleted"})
        except Exception as e:
            return Response({'error' : str(e)},status=500)


class GetStoreByVendor(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            user=Stores.objects.filter(created_by=request.user)
            serialize=Serializer_Store(user,many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500) 


class GetStoreById(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,id=None):
        try:
            user=Stores.objects.filter(id=id)
            serialize=Serializer_Store(user,many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)  




class CountryFilter(APIView):
    def post(self,request):
        try:
            search=request.data.get("search", None)
            AdministratorArea=request.data.get("AdministratorArea")
            
            Country=USACountry.objects.all()
            if search:
                if AdministratorArea=="administrative_area_level_1":
                    a=Country.filter(state_name__icontains=search)
                    if  a:
                        serialize=Serializer_USAData(a,many=True).data
                        return Response(serialize)
                    else:
                        return Response("Not Found",status=status.HTTP_202_ACCEPTED)
                    
                if AdministratorArea=='sublocality_level_1':
                    s=Country.filter(county_name__icontains=search)
                    if s:
                        serialize=Serializer_USAData(s,many=True).data
                        return Response(serialize)
                    else:
                        return Response("Not Found",status=status.HTTP_202_ACCEPTED)
                    
                if AdministratorArea=="administrative_area_level_2":
                    d=Country.filter(city__icontains=search)
                    if d:
                        serialize=Serializer_USAData(d,many=True).data
                        return Response(serialize)
                    else:
                        return Response("Not Found",status=status.HTTP_202_ACCEPTED)
                
            else:
                return Response("Blank",status=status.HTTP_202_ACCEPTED)
        except Exception as e:  
             return Response({'error' : str(e)},status=500)


class GetLaw(APIView):

    def get(self, request, id=None):
        try:
            User =Law.objects.all()
            serialize = Serializer_Law(User, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class GetLawbyid(APIView):

    def get(self, request, id=None):
        try:
            User =Law.objects.filter(id=id)
            serialize = Serializer_Law(User, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
        
class GetAboutUs(APIView):

    def get(self, request, format=None):
        try:
            User =AboutUs.objects.select_related().all()
            serialize = Serializer_AboutUs(User, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
        
class GetTermsandCondition(APIView):

    def get(self, request, format=None):
        try:
            User =TermsandCondition.objects.select_related().all()
            serialize = Serializer_TermsAndCondition(User, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)


class GetPrivacyandPolicies(APIView):

    def get(self, request, format=None):
        try:
            User =PrivacyandPolicies.objects.select_related().all()
            serialize = Serializer_PrivacyAndPolicies(User, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)


class CategoryByStore(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            user=request.user
            s=[]
            Store_Id=Stores.objects.filter(created_by=user).first()
            product=Product.objects.filter(Store_id=Store_Id)
            for i in product:
                a=SubCategory.objects.filter(id=i.Sub_Category_id_id)
                for j in a:
                    b=Category.objects.filter(id=j.category_id_id)
                    for i in b:
                    # serialize=Serializer_Category(b,many=True)
                        response = {'name':i.name,'id':i.id,"image":i.categoryImages.url}
                    
                    s.append(response)
            return Response(s,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=500)


class ProductByCategory(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            a=[]
            category=request.data.get("category")
            user=request.user
            for i in category:
                product=Product.objects.filter(Sub_Category_id__category_id=i).filter(Status="Active")
                vendor=product.filter(created_by=user)
                if vendor:
                    for i in vendor:
                        response = {'id':i.id}
                        a.append(response)
            return Response(a,status=200)
        except Exception as e:
            return Response({'error' : str(e)},status=500)


class CustomerSegmentsCustomersWhoHavePurchasedMoreThanOnce(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            user=request.user
            s=[]
            Store_Id=Stores.objects.filter(created_by=user).first()
            order=Order.objects.filter(Store=Store_Id)
            for i in order:
                a=User.objects.filter(id=i.created_by_id)
                for j in a:
                    response = {'name':j.username,'id':j.id,'email':j.email}
                    s.append(response)
            return Response(s,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=500)


class ConvertZipIntoName(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            a=[]
            user=request.user
            store=Stores.objects.filter(created_by=user).first()
            for i in store.Locations:
                location=USACountry.objects.filter(zip=i["Zip"])
                for j in location:
                    response = {'City':j.city}
                    a.append(response)
            return Response(a,status=200)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class MainCategoryProductCount(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:

            a=[] 
            Delivery = Stores.objects.filter(Order_Type="Delivery")
            DeliveryandPickup=Stores.objects.filter(Store_Type="Delivery and Pickup")
            User=Delivery or DeliveryandPickup
            addressCheck=User.filter(created_by=request.user)
            serialize=Serializer_Store(addressCheck,many=True).data 
            for i in serialize:
                product=Product.objects.filter(Store_id=i["id"])
                for j in product:
                    Subcategory=SubCategory.objects.filter(id=j.Sub_Category_id_id)
                    for k in Subcategory:
                        category=Category.objects.filter(id=k.category_id_id)
                        serialize1=Serializer_Category(category,many =True).data
                        for l in serialize1:
                            for m in category:
                                productCount=Product.objects.filter(Sub_Category_id__category_id_id=m.id).filter(Store_id=i["id"]).count()
                                response={"Store_Name":i["Store_Name"],"TotalRating":i["TotalRating"],"rating":i["rating"],"id":i["id"],"Category":l["name"],"ProductCount":productCount,"Store_Image":i["Store_Image"],"Store_Address":i["Store_Address"]}
                                a.append(response)
            if a:
                a= { each['Store_Name'] + each['Category'] : each for each in a }.values()
            return Response(a)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)  

from django.http import JsonResponse

class GetPendingOrder(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            User = Order.objects.filter(Store=id)
            pending=User.filter(Order_Status="Pending")
            serialize = Serializer_Order(pending, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return JsonResponse({'error' : str(e)},status=500)
        
class GetDeliveredOrder(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            User = Order.objects.filter(Store=id)
            Delivered=User.filter(Order_Status="Delivered")
            serialize = Serializer_Order(Delivered, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
class GetCancelOrder(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            User = Order.objects.filter(Store=id)
            Cancel=User.filter(Order_Status="Cancel")
            serialize = Serializer_Order(Cancel, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
class GetProcessingOrder(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            User = Order.objects.filter(Store=id)
            Processing=User.filter(Order_Status="Processing")
            serialize = Serializer_Order(Processing, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
        
class GetOrderBYID(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,id=None):
        try:
            User = Order.objects.filter(OrderId=id)
            serialize = Serializer_Order(User, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
     
class UpdateOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            
            User = Order.objects.get(OrderId=id)
            serializer = Serializer_Order(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.username)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class SearchOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            search=request.data.get("search",None)
            store=Order.objects.filter(Store=id)
            User=store.filter(OrderId__icontains=search)
            if User:
                serializer = Serializer_Order(User, many=True)
                return Response(serializer.data)
            else:
                a=store.filter(Product__icontains=search)
                serializer = Serializer_Order(a, many=True).data
                return Response(serializer)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from operator import itemgetter

class GetTopSellingProduct(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            x=[]
            y=[]
            User = Order.objects.filter(Store=id)
            top=User.filter(Order_Status="Delivered")
            for i in top:
                for j in i.Product:
                    a=ProductImage.objects.filter(product=j["Product_id"]).first()
                    qwe=0
                    cart=0
                    qwe = qwe + j["TotalPrice"]
                    cart= cart +j["Cart_Quantity"]
                    response={"ProductName":j["ProductName"],"ProductSalesCount":cart,"Price":qwe,"Image":a.image.url,"category":j["category"],"Product_id":j["Product_id"]}
                    x.append(response)
            for l in x:
                if l not in y:
                    y.append(l)
            y.sort(key = itemgetter('ProductSalesCount'), reverse=True)
            return Response(y)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
        

class AddReplyonStoreReview(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, id=None):
        try:
            User = StoreReview.objects.get(id=id)
            serializer = StoreRatingAndReviewSerializer(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.username)
                return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetReplyonStoreReview(APIView):
    def get(self,request,id=None):
        try:
            like=StoreReview.objects.filter(Store=id)
            serialize=StoreRatingAndReviewSerializer(like,many=True).data
            return Response(serialize)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
 
class ReplyProductReview(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, id=None):
        try:
            User = Review.objects.get(id=id)
            serializer = ReviewSerializer(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.username)
                a=Review.objects.get(id=id)
                if a.Reply != None:
                    ProductReview={"ProductReview":a.id,"user":request.user}
                    s=Serializer_UserNotification(data=ProductReview,partial=True)
                    if s.is_valid():
                        s.save()
                return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)       


class SearchProduct(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            search=request.data.get("search",None)
            store=Product.objects.filter(Store=id)
            User=store.filter(Product_Name__icontains=search)
            serializer = Serializer_Product(User, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class DeleteMultipleProduct(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self,request):
        try:
            id=request.data.get("id")
            for i in id:
                User = get_object_or_404(Product, id=i)
                User.delete()
            return Response({"status": "success", "data": "Deleted"})
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BookDemo(APIView):
    def post(self,request):
        try:
            pass
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LoginResendOtpAPI(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        try:
            email = request.data.get("email")
            if email:
                serializer = LoginSerializer1(data=request.data)
                if serializer.is_valid():
                    email = serializer.validated_data['email']
                    send_OneToOneMail(
                        from_email='smtpselnox@gmail.com', to_emails=email)
                    return Response({
                        'message': 'Email sent',
                        'data': {"Otp_Sent_to": email}
                    },status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Enter the valid Email"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
from datetime import datetime,timedelta

class SalesPerformancePieChart(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            SelectTime=request.data.get("SelectTime",None)
            store=request.data.get("store")
            StartDate = request.data.get("StartDate",None)
            EndDate=request.data.get("EndDate")
            if SelectTime=="Today":
                order=Order.objects.filter(OrderDate__icontains=StartDate).filter(Order_Status="Delivered").filter(Store_id=store)
                result = {"Pickup": 0, "Delivery": 0,"Curbsibe":0}
                for i in order:
                    if i.Order_Type == "Pickup":
                        result["Pickup"] += i.subtotal
                    elif i.Order_Type == "Delivery":
                        result["Delivery"] += i.subtotal
                    elif i.Order_Type == "Delivery and Pickup":
                        result["Curbsibe"] += i.subtotal
                return Response(result)

            else:
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Order_Status="Delivered").filter(Store_id=store)
                result = {"Pickup": 0, "Delivery": 0,"Curbsibe":0}
                for i in order:
                    if i.Order_Type == "Pickup":
                        result["Pickup"] += i.subtotal
                    elif i.Order_Type == "Delivery":
                        result["Delivery"] += i.subtotal
                    elif i.Order_Type == "Delivery and Pickup":
                        result["Curbsibe"] += i.subtotal
                return Response(result)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

class RecentOrderPieChart(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            SelectTime=request.data.get("SelectTime",None)
            store=request.data.get("store")
            StartDate = request.data.get("StartDate",None)
            EndDate=request.data.get("EndDate")
            if SelectTime=="Today":
                Pending=Order.objects.filter(OrderDate__icontains=StartDate).filter(Order_Status="Pending").filter(Store_id=store).count()
                Processing=Order.objects.filter(OrderDate__icontains=StartDate).filter(Order_Status="Processing").filter(Store_id=store).count()
                Delivered=Order.objects.filter(OrderDate__icontains=StartDate).filter(Order_Status="Delivered").filter(Store_id=store).count()
                Cancel=Order.objects.filter(OrderDate__icontains=StartDate).filter(Order_Status="Cancel").filter(Store_id=store).count()
                response={"Pending":Pending,"Processing":Processing,"Delivered":Delivered,"Cancel":Cancel}
                return Response(response)
            else:
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                Pending=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Order_Status="Pending").filter(Store_id=store).count()
                Processing=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Order_Status="Processing").filter(Store_id=store).count()
                Delivered=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Order_Status="Delivered").filter(Store_id=store).count()
                Cancel=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Order_Status="Cancel").filter(Store_id=store).count()
                response={"Pending":Pending,"Processing":Processing,"Delivered":Delivered,"Cancel":Cancel}
                return Response(response)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SalesByCategoryPieChart(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            category=[]
            SelectTime=request.data.get("SelectTime",None)
            store=request.data.get("store")
            StartDate = request.data.get("StartDate",None)
            EndDate=request.data.get("EndDate")
            if SelectTime=="Today":
                Delivered=Order.objects.filter(OrderDate__icontains=StartDate).filter(Order_Status="Delivered").filter(Store_id=store)
                for i in Delivered:
                    for j in i.Product:
                        category.append(j["category"])
                response={i:category.count(i) for i in category}
                return Response(response)
            else:
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                Delivered=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Order_Status="Delivered").filter(Store_id=store)
                for i in Delivered:
                    for j in i.Product:
                        category.append(j["category"])
                response={i:category.count(i) for i in category}
                return Response(response)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ProductByCategoryPieChart(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,id=None):
        try:
            s=[]
            z=[]
            product=Product.objects.filter(Store_id=id)
            for i in product:
                a=Category.objects.filter(id=i.Sub_Category_id.category_id_id)
                for j in a:
                    count=Product.objects.filter(Sub_Category_id__category_id_id=j.id).count()
                    response={j.name:count}
                    s.append(response)
            for m in s:
               if m not in z:
                    z.append(m)
            return Response(z,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class SalesInsights(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            a=[]
            SelectTime=request.data.get("SelectTime",None)
            store=request.data.get("store")
            StartDate = request.data.get("StartDate",None)
            EndDate=request.data.get("EndDate")
            if SelectTime=="Today":
                add=0
                productsold=0
                TodaySales=Order.objects.filter(OrderDate__icontains=StartDate).filter(Store=store)
                order=TodaySales.count()
                for i in TodaySales:
                    add=add+i.subtotal
                    for j in i.Product:
                       productsold = productsold + j["Cart_Quantity"]
                cancelorder=TodaySales.filter(Order_Status="Cancel").count()
                response={"Date":StartDate,"Order":order,"CancelledOrder":cancelorder,"ProductSold":productsold,"Sale":add}
                a.append(response)
            if SelectTime=="ThisWeek":
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                while week <= today:
                    add=0
                    productsold=0
                    TodaySales=Order.objects.filter(OrderDate__gte=week,OrderDate__lte=today).filter(Store=store)
                    order=TodaySales.count()
                    for i in TodaySales:
                        add=add+i.subtotal
                        for j in i.Product:
                            productsold = productsold + j["Cart_Quantity"]
                    cancelorder=TodaySales.filter(Order_Status="Cancel").count()
                    response={"Date":week.strftime("%A"),"Order":order,"CancelledOrder":cancelorder,"ProductSold":productsold,"Sale":add}
                    a.append(response)
                    week=week + timedelta(days=1)
            if SelectTime=="ThisMonth":
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                while week <= today:
                    add=0
                    productsold=0
                    TodaySales=Order.objects.filter(OrderDate__gte=week,OrderDate__lte=today).filter(Store=store)
                    order=TodaySales.count()
                    for i in TodaySales:
                        add=add+i.subtotal
                        for j in i.Product:
                            productsold = productsold + j["Cart_Quantity"]
                    cancelorder=TodaySales.filter(Order_Status="Cancel").count()
                    response={"Date":week.strftime("%x"),"Order":order,"CancelledOrder":cancelorder,"ProductSold":productsold,"Sale":add}
                    a.append(response)
                    week=week + timedelta(days=1)
            if SelectTime=="ThisYear":
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                while week <= today:
                    add=0
                    productsold=0
                    TodaySales=Order.objects.filter(OrderDate__gte=week,OrderDate__lte=today).filter(Store=store)
                    order=TodaySales.count()
                    for i in TodaySales:
                        add=add+i.subtotal
                        for j in i.Product:
                            productsold = productsold + j["Cart_Quantity"]
                    cancelorder=TodaySales.filter(Order_Status="Cancel").count()
                    response={"Date":week.strftime("%B"),"Order":order,"CancelledOrder":cancelorder,"ProductSold":productsold,"Sale":add}
                    a.append(response)
                    week=week + timedelta(days=30)
            return Response(a)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
 
class SalesOverviewcard(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            a=[]
            SelectTime=request.data.get("SelectTime",None)
            store=request.data.get("store")
            StartDate = request.data.get("StartDate",None)
            EndDate=request.data.get("EndDate")
            if SelectTime=="Today":
                add=0
                productsold=0
                TodaySales=Order.objects.filter(OrderDate__icontains=StartDate).filter(Store=store)
                order=TodaySales.count()
                for i in TodaySales:
                    add=add+i.subtotal
                    for j in i.Product:
                       productsold = productsold + j["Cart_Quantity"]
                if productsold>1:
                    AverageSales=add/order
                else:
                    AverageSales=0
                response={"Order":order,"TotalSale":add,"ProductSold":productsold,"AverageSales":AverageSales}
                a.append(response)
                return Response(a)
            else :
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                add=0
                productsold=0
                TodaySales=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Store=store)
                order=TodaySales.count()
                for i in TodaySales:
                    add=add+i.subtotal
                    for j in i.Product:
                       productsold = productsold + j["Cart_Quantity"]
                if productsold>1:
                    AverageSales=add/order
                else:
                    AverageSales=0
                response={"Order":order,"TotalSale":add,"ProductSold":productsold,"AverageSales":AverageSales}
                a.append(response)
                return Response(a)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
import base64
import requests


def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)

# q=get_as_base64(url="https://selnoxmedia.s3.amazonaws.com/media/product_images/12c29b_7f4c8d01e3d244fba7a50c36c7c201ffmv21.jpeg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAS4WSA6KJNP6NPPES%2F20240108%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20240108T111034Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=815ada9e110d068ec667910113fdf0640e2747c67fe45ee40d4bc73eb2179591")
# print(q)
class ImageToBase64(APIView):
    def post(self,request):
        try:
            a=[]
            url=request.data.get("url")
            for i in url:
                z=get_as_base64(i)
                a.append(z)
            return Response(a)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
 
class ProductInsight(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:

            x=[]
            y=[]
            SelectTime=request.data.get("SelectTime",None)
            store=request.data.get("store")
            StartDate = request.data.get("StartDate",None)
            EndDate=request.data.get("EndDate")
            if SelectTime=="Today":
                User = Order.objects.filter(Store=store).filter(OrderDate__icontains=StartDate)
                top=User.filter(Order_Status="Delivered")
                for i in top:
                    for j in i.Product:
                        a=ProductImage.objects.filter(product=j["Product_id"]).first()
                        qwe=0
                        cart=0
                        qwe = qwe + j["TotalPrice"]
                        cart= cart +j["Cart_Quantity"]
                        response={"ProductName":j["ProductName"],"ProductSalesCount":cart,"Price":qwe,"Image":a.image.url,"category":j["category"],"Product_id":j["Product_id"]}
                        x.append(response)
                for l in x:
                    if l not in y:
                        y.append(l)
                y.sort(key = itemgetter('ProductSalesCount'), reverse=True)
            if SelectTime=="ThisWeek":
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                TodaySales=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Store=store)
                top=TodaySales.filter(Order_Status="Delivered")
                for i in top:
                    for j in i.Product:
                        a=ProductImage.objects.filter(product=j["Product_id"]).first()
                        qwe=0
                        cart=0
                        qwe = qwe + j["TotalPrice"]
                        cart= cart +j["Cart_Quantity"]
                        response={"ProductName":j["ProductName"],"ProductSalesCount":cart,"Price":qwe,"Image":a.image.url,"category":j["category"],"Product_id":j["Product_id"]}
                        x.append(response)
                for l in x:
                    if l not in y:
                        y.append(l)
                y.sort(key = itemgetter('ProductSalesCount'), reverse=True)
            if SelectTime=="ThisMonth":
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                TodaySales=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Store=store)
                top=TodaySales.filter(Order_Status="Delivered")
                for i in top:
                    for j in i.Product:
                        a=ProductImage.objects.filter(product=j["Product_id"]).first()
                        qwe=0
                        cart=0
                        qwe = qwe + j["TotalPrice"]
                        cart= cart +j["Cart_Quantity"]
                        response={"ProductName":j["ProductName"],"ProductSalesCount":cart,"Price":qwe,"Image":a.image.url,"category":j["category"],"Product_id":j["Product_id"]}
                        x.append(response)
                for l in x:
                    if l not in y:
                        y.append(l)
                y.sort(key = itemgetter('ProductSalesCount'), reverse=True)
            if SelectTime=="ThisYear":
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                TodaySales=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Store=store)
                top=TodaySales.filter(Order_Status="Delivered")
                for i in top:
                    for j in i.Product:
                        a=ProductImage.objects.filter(product=j["Product_id"]).first()
                        qwe=0
                        cart=0
                        qwe = qwe + j["TotalPrice"]
                        cart= cart +j["Cart_Quantity"]
                        response={"ProductName":j["ProductName"],"ProductSalesCount":cart,"Price":qwe,"Image":a.image.url,"category":j["category"],"Product_id":j["Product_id"]}
                        x.append(response)
                for l in x:
                    if l not in y:
                        y.append(l)
                y.sort(key = itemgetter('ProductSalesCount'), reverse=True)
            return Response(y)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
   
class OrderInsight(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            SelectTime=request.data.get("SelectTime",None)
            store=request.data.get("store")
            StartDate = request.data.get("StartDate",None)
            EndDate=request.data.get("EndDate")
            if SelectTime=="Today":
                TodaySales=Order.objects.filter(OrderDate__icontains=StartDate).filter(Store=store)
                serialize=Serializer_Order(TodaySales,many=True)
                return Response(serialize.data)
            if SelectTime=="ThisWeek":
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                TodaySales=Order.objects.filter(OrderDate__gte=week,OrderDate__lte=today).filter(Store=store)
                serialize=Serializer_Order(TodaySales,many=True)
                return Response(serialize.data)
            if SelectTime=="ThisMonth":
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                TodaySales=Order.objects.filter(OrderDate__gte=week,OrderDate__lte=today).filter(Store=store)
                serialize=Serializer_Order(TodaySales,many=True)
                return Response(serialize.data)
            if SelectTime=="ThisYear":
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                TodaySales=Order.objects.filter(OrderDate__gte=week,OrderDate__lte=today).filter(Store=store)
                serialize=Serializer_Order(TodaySales,many=True)
                return Response(serialize.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class CategoryInsight(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            SelectTime=request.data.get("SelectTime",None)
            store=request.data.get("store")
            StartDate = request.data.get("StartDate",None)
            EndDate=request.data.get("EndDate")
            if SelectTime=="Today":
                Delivered=Order.objects.filter(OrderDate__icontains=week).filter(Order_Status="Delivered").filter(Store_id=store)
                TotalOrder=Order.objects.filter(OrderDate__icontains=week).filter(Store_id=store)
                category_stats = []
                for order in Delivered:
                    for product in order.Product:
                        category_stats.append({
                            "category": product["category"],
                            "Item": product["Cart_Quantity"],
                            "Order": 1,  
                            "Amount": product["TotalPrice"]  
                        })
                for order in TotalOrder:
                    for product in order.Product:
                        found = False
                        for stat in category_stats:
                            if stat["category"] == product["category"]:
                                stat["Item"] += product["Cart_Quantity"]
                                stat["Order"] += 1
                                stat["Amount"] += product["TotalPrice"] 
                                found = True
                                break
                        if not found:
                            category_stats.append({
                                "category": product["category"],
                                "Item": product["Cart_Quantity"],
                                "Order": 1,
                                "Amount": product["TotalPrice"]  
                            })

                return Response(category_stats)
            if SelectTime=="ThisWeek":
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                Delivered=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Order_Status="Delivered").filter(Store_id=store)
                TotalOrder=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Store_id=store)
                category_stats = []
                for order in Delivered:
                    for product in order.Product:
                        category_stats.append({
                            "category": product["category"],
                            "Item": product["Cart_Quantity"],
                            "Order": 1,  
                            "Amount": product["TotalPrice"]  
                        })
                for order in TotalOrder:
                    for product in order.Product:
                        found = False
                        for stat in category_stats:
                            if stat["category"] == product["category"]:
                                stat["Item"] += product["Cart_Quantity"]
                                stat["Order"] += 1
                                stat["Amount"] += product["TotalPrice"] 
                                found = True
                                break
                        if not found:
                            category_stats.append({
                                "category": product["category"],
                                "Item": product["Cart_Quantity"],
                                "Order": 1,
                                "Amount": product["TotalPrice"]  
                            })

                return Response(category_stats)
            if SelectTime=="ThisMonth":
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                Delivered=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today ).filter(Order_Status="Delivered" ).filter(Store_id=store)
                TotalOrder=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Store_id=store)
                category_stats = []
                for order in Delivered:
                    for product in order.Product:
                        category_stats.append({
                            "category": product["category"],
                            "Item": product["Cart_Quantity"],
                            "Order": 1,  
                            "Amount": product["TotalPrice"]  
                        })
                for order in TotalOrder:
                    for product in order.Product:
                        found = False
                        for stat in category_stats:
                            if stat["category"] == product["category"]:
                                stat["Item"] += product["Cart_Quantity"]
                                stat["Order"] += 1
                                stat["Amount"] += product["TotalPrice"] 
                                found = True
                                break
                        if not found:
                            category_stats.append({
                                "category": product["category"],
                                "Item": product["Cart_Quantity"],
                                "Order": 1,
                                "Amount": product["TotalPrice"]  
                            })

                return Response(category_stats)
            if SelectTime=="ThisYear":
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                Delivered=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today ).filter(Order_Status="Delivered").filter(Store_id=store)
                TotalOrder=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Store_id=store)
                category_stats = []
                for order in Delivered:
                    for product in order.Product:
                        category_stats.append({
                            "category": product["category"],
                            "Item": product["Cart_Quantity"],
                            "Order": 1,  
                            "Amount": product["TotalPrice"]  
                        })
                for order in TotalOrder:
                    for product in order.Product:
                        found = False
                        for stat in category_stats:
                            if stat["category"] == product["category"]:
                                stat["Item"] += product["Cart_Quantity"]
                                stat["Order"] += 1
                                stat["Amount"] += product["TotalPrice"] 
                                found = True
                                break
                        if not found:
                            category_stats.append({
                                "category": product["category"],
                                "Item": product["Cart_Quantity"],
                                "Order": 1,
                                "Amount": product["TotalPrice"]  
                            })

                return Response(category_stats)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# from io import BytesIO
# import io, base64,boto3
# from PIL import Image

# import requests
# from PIL import Image
# from io import BytesIO

# # def link_to_image(link, output_path):
# #     try:
# #         response = requests.get(link)
# #         if response.status_code == 200:
# #             image = Image.open(BytesIO(response.content))
# #             image.save(output_path)
# #             print(f"Image saved to {output_path}")
# #         else:
# #             print(f"Failed to retrieve the image. Status code: {response.status_code}")
# #     except Exception as e:
# #         print(f"An error occurred: {e}")
# def download_file(link, destination):
#     try:
#         # Send a GET request to the URL
#         response = requests.get(link)
#         response.raise_for_status()  # Raise an exception for bad requests

#         # Open the image using Pillow
#         image = Image.open(BytesIO(response.content))

#         # Save the image to the specified output path
#         image.save(destination)

#         print(f"Image saved successfully at {destination}")

#     except Exception as e:
#         print(f"Error: {e}")

# import base64
# import json
# from PIL import Image

# # def image_to_json(image_path):
# #     try:
# #         # Open the image using Pillow
# #         with open(image_path, "rb") as image_file:
# #             # Convert image data to base64
# #             base64_data = base64.b64encode(image_file.read()).decode('utf-8')

# #         # Create a dictionary with the image data
# #         image_data = {
# #             "image_path": image_path,
# #             "base64_data": base64_data
# #         }

# #         # Convert the dictionary to JSON
# #         json_data = json.dumps(image_data, indent=2)

# #         # Print or return the JSON data
# #         print(json_data)
# #         return json_data

# #     except Exception as e:
# #         print(f"Error: {e}")
# def encode_image_to_base64(image_path):
#     with open(image_path, "rb") as image_file:
#         # Convert binary image data to base64
#         base64_data = base64.b64encode(image_file.read()).decode('utf-8')
#     return base64_data
# def create_json_with_image(image_path):
#     # Encode image to base64
#     base64_data = encode_image_to_base64(image_path)

#     # Create a dictionary with image data
#     image_data = {
#         "image_path": image_path,
#         "base64_data": base64_data
#     }

#     # Convert the dictionary to JSON
#     json_data = json.dumps(image_data, indent=2)
#     return json_data

# # Example usage:





# from django.core.files import File


# class ImportXcel(APIView):
#     permission_classes=[IsAuthenticated]
#     def post(self,request):
#         try:
#             data=request.data.get("data")
#             for i in data:
#                 b=Brand.objects.filter(name=i["Brand_Name"]).first()
#                 c=SubCategory.objects.filter(name=i["SubcategoryName"]).first()
#                 for j in i["images"]:
#                     response = requests.get(j)
#                     if response.status_code == 200:
#                         response.encoding="utf-8"
#                         temp_image_path = "/home/selnoxinfotech/Anshuman/BackwoodAroma/output_image.jpg"
#                         with open(temp_image_path, 'wb') as temp_image_file:
#                             temp_image_file.write(response.content)
#                         i['image'] = File(open(temp_image_path, 'rb'))
#                 createdata={"Brand_id":b.id,"Sub_Category_id":c.id,"Multiple_images":i['image']}
#                 i.update(createdata)
#                 product=Product.objects.filter(Specialid=i["Specialid"]).first()
#                 if product:
#                     serailze=Serializer_Product(product,data=i,partial=True)
#                     if serailze.is_valid():
#                         serailze.save()
#                         return Response(serailze.data)
#                     else:
#                         return Response(serailze.errors,status=status.HTTP_400_BAD_REQUEST)
#                 else:
#                     serailze=Serializer_Product(i,partial=True)
#                     if serailze.is_valid():
#                         serailze.save()
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SalesPerformance(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
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
                week=week + timedelta(days=1)
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
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today   ).filter(Order_Status="Delivered").filter(Store_id=store)
                    
                    for i in order:
                        TotalPrice += i.subtotal
                        for j in i.Product:
                            UnitSold += j["Cart_Quantity"]
                    result = {"Date":week.strftime("%B"),"TotalPrice":TotalPrice,"UnitSold":UnitSold}
                    z.append(result)
                    week += timedelta(days=30)
                return Response(z)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
class SalesByProductGraph(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            SelectTime=request.data.get("SelectTime")
            store=request.data.get("store")
            startdate = request.data.get("StartDate",None)
            if SelectTime=="Today":
                z=[]
                week=(datetime.now()-timedelta(days=startdate))
                date=datetime.today()
                while week <= date:
                    UnitSold=0
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=date ).filter(Order_Status="Delivered").filter(Store_id=store)
                    for i in order:
                        for j in i.Product:
                            UnitSold += j["Cart_Quantity"]
                    result = {"Date":week.strftime("%B"),"UnitSold":UnitSold}
                    z.append(result)
                    week=week + timedelta(days=1)
                return Response(z)

            if SelectTime=="ThisWeek":
                z=[]
                week=(datetime.now()-timedelta(days=startdate))
                date=datetime.today()
                while week <= date:
                    UnitSold=0
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=date ).filter(Order_Status="Delivered").filter(Store_id=store)
                    for i in order:
                        for j in i.Product:
                            UnitSold += j["Cart_Quantity"]
                    result = {"Date":week.strftime("%A"),"UnitSold":UnitSold}
                    z.append(result)
                    week=week + timedelta(days=1)
                return Response(z)
            if SelectTime=="ThisMonth":
                z=[]
                week=(datetime.now()-timedelta(days=startdate))
                date=datetime.today()
                while week <= date:
                    UnitSold=0
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=date ).filter(Order_Status="Delivered").filter(Store_id=store)
                    for i in order:
                        for j in i.Product:
                            UnitSold += j["Cart_Quantity"]
                    result = {"Date":week.strftime("%x"),"UnitSold":UnitSold}
                    z.append(result)
                    week=week + timedelta(days=1)
                return Response(z)
            if SelectTime=="ThisYear":
                z=[]
                week=(datetime.now()-timedelta(days=startdate))
                date=datetime.today()
                while week <= date:
                    UnitSold=0
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=date ).filter(Order_Status="Delivered").filter(Store_id=store)
                    for i in order:
                        for j in i.Product:
                            UnitSold += j["Cart_Quantity"]
                    result = {"Date":week.strftime("%B"),"UnitSold":UnitSold}
                    z.append(result)
                    week=week + timedelta(days=30)
                return Response(z)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class SalesByOrderGraph(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            SelectTime=request.data.get("SelectTime")
            store=request.data.get("store")
            StartDate=request.data.get("StartDate")
            EndDate=request.data.get("EndDate")
            if SelectTime=="Today":
                z=[]
                UnitSold=0
                order=Order.objects.filter(OrderDate__icontains=StartDate).filter(Store_id=store)
                for i in order:
                    for j in i.Product:
                        UnitSold += j["Cart_Quantity"]
                result = {"Date":StartDate,"UnitSold":UnitSold}
                z.append(result)
                return Response(z)

            if SelectTime=="ThisWeek":
                z=[]
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                while week <= today:
                    UnitSold=0
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today ).filter(Store_id=store)
                    for i in order:
                        for j in i.Product:
                            UnitSold += j["Cart_Quantity"]
                    result = {"Date":week.strftime("%A"),"UnitSold":UnitSold}
                    z.append(result)
                    week=week + timedelta(days=1)
                return Response(z)
            if SelectTime=="ThisMonth":
                z=[]
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                while week <= today:
                    UnitSold=0
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today ).filter(Store_id=store)
                    for i in order:
                        for j in i.Product:
                            UnitSold += j["Cart_Quantity"]
                    result = {"Date":week.strftime("%x"),"UnitSold":UnitSold}
                    z.append(result)
                    week=week + timedelta(days=1)
                return Response(z)
            if SelectTime=="ThisYear":
                z=[]
                l={}
                week=datetime.strptime(StartDate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                while week <= today:
                    UnitSold=0
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today ).filter(Store_id=store)
                    for i in order:
                        for j in i.Product:
                            UnitSold += j["Cart_Quantity"]
                    result = {"Date":week.strftime("%B"),"UnitSold":UnitSold}
                    z.append(result)
                    week=week + timedelta(days=1)
                for qwe in range(0,len(z)):
                    for rty in z:
                        if (z[qwe]==rty):
                            l.update(rty)
                return Response([l])
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class SalesGraph(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            SelectTime=request.data.get("SelectTime")
            store=request.data.get("store")
            startdate = request.data.get("StartDate",None)
            EndDate=request.data.get("EndDate")
            if SelectTime=="Today":
                z=[]
                UnitSold=0
                DeliverSale=0
                StoreSale=0
                order=Order.objects.filter(OrderDate__icontains=startdate).filter(Store_id=store).filter(Order_Status="Delivered")
                for i in order:
                    if i.Order_Type == "Delivery":
                        for j in i.Product:
                            UnitSold += j["Cart_Quantity"]
                            DeliverSale += j["Cart_Quantity"]
                    elif i.Order_Type == "Pickup":
                        for j in i.Product:
                            UnitSold += j["Cart_Quantity"]
                            StoreSale += j["Cart_Quantity"]
                result = {"Date":startdate,"UnitSold":UnitSold,"DeliverSale":DeliverSale,"StoreSale":StoreSale}
                z.append(result)
                return Response(z)

            if SelectTime=="ThisWeek":
                z=[]
                week=datetime.strptime(startdate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                while week <= today:
                    UnitSold=0
                    DeliverSale=0
                    StoreSale=0
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Store_id=store).filter(Order_Status="Delivered")
                    for i in order:
                        if i.Order_Type == "Delivery":
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                                DeliverSale += j["Cart_Quantity"]
                        elif i.Order_Type == "Pickup":
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                                StoreSale += j["Cart_Quantity"]
                            
                    result = {"Date":week.strftime("%A"),"UnitSold":UnitSold,"DeliverSale":DeliverSale,"StoreSale":StoreSale} 
                    z.append(result)
                    week=week + timedelta(days=1)
                return Response(z)
            if SelectTime=="ThisMonth":
                z=[]
                week=datetime.strptime(startdate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                while week <= today:
                    UnitSold=0
                    DeliverSale=0
                    StoreSale=0
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today ).filter(Store_id=store).filter(Order_Status="Delivered")
                    for i in order:
                        if i.Order_Type == "Delivery":
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                                DeliverSale += j["Cart_Quantity"]
                        elif i.Order_Type == "Pickup":
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                                StoreSale += j["Cart_Quantity"]
                    result = {"Date":week.strftime("%x"),"UnitSold":UnitSold,"DeliverSale":DeliverSale,"StoreSale":StoreSale}
                    z.append(result)
                    week=(week) + timedelta(days=1)
                return Response(z)
            if SelectTime=="ThisYear":
                z=[]
                l={}
                week=datetime.strptime(startdate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                UnitSold=0
                DeliverSale=0
                StoreSale=0
                while week <= today:
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today ).filter(Store_id=store).filter(Order_Status="Delivered")
                    for i in order:
                        if i.Order_Type == "Delivery":  
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                                DeliverSale += j["Cart_Quantity"]
                        elif i.Order_Type == "Pickup":
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                                StoreSale += j["Cart_Quantity"]
                    week=week + timedelta(days=1)
                    result = {"Date":week.strftime("%B"),"UnitSold":UnitSold,"DeliverSale":DeliverSale,"StoreSale":StoreSale}  #"Date":week.strftime("%B"),
                    z.append(result)
                for qwe in range(0,len(z)):
                    for rty in z:
                        if (z[qwe]==rty):
                            l.update(rty)
                return Response([l])
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
class OrderGraph(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            SelectTime=request.data.get("SelectTime")
            store=request.data.get("store")
            startdate = request.data.get("StartDate")
            EndDate=request.data.get("EndDate")
            if SelectTime=="Today":
                z=[]
                UnitSold=0
                DeliverSale=0
                StoreSale=0
                order=Order.objects.filter(OrderDate__icontains=startdate).filter(Store_id=store)
                for i in order:
                    if i.Order_Type == "Delivery":
                        for j in i.Product:
                            UnitSold += j["Cart_Quantity"]
                            DeliverSale += j["Cart_Quantity"]
                    elif i.Order_Type == "Pickup":
                        for j in i.Product:
                            UnitSold += j["Cart_Quantity"]
                            StoreSale += j["Cart_Quantity"]
                result = {"Date":startdate,"UnitSold":UnitSold,"DeliverSale":DeliverSale,"StoreSale":StoreSale}
                z.append(result)
                return Response(z)

            if SelectTime=="ThisWeek":
                z=[]
                week=datetime.strptime(startdate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                while week <= today:
                    UnitSold=0
                    DeliverSale=0
                    StoreSale=0
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Store_id=store)
                    for i in order:
                        if i.Order_Type == "Delivery":
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                                DeliverSale += j["Cart_Quantity"]
                        elif i.Order_Type == "Pickup":
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                                StoreSale += j["Cart_Quantity"]
                            
                    result = {"Date":week.strftime("%A"),"UnitSold":UnitSold,"DeliverSale":DeliverSale,"StoreSale":StoreSale}
                    z.append(result)
                    week=week + timedelta(days=1)
                return Response(z)
            if SelectTime=="ThisMonth":
                z=[]
                week=datetime.strptime(startdate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                while week <= today:
                    UnitSold=0
                    DeliverSale=0
                    StoreSale=0
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Store_id=store)
                    for i in order:
                        if i.Order_Type == "Delivery":
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                                DeliverSale += j["Cart_Quantity"]
                        elif i.Order_Type == "Pickup":
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                                StoreSale += j["Cart_Quantity"]
                    result = {"Date":week.strftime("%x"),"UnitSold":UnitSold,"DeliverSale":DeliverSale,"StoreSale":StoreSale}
                    z.append(result)
                    week=week + timedelta(days=1)
                return Response(z)
            if SelectTime=="ThisYear":
                z=[]
                l={}
                week=datetime.strptime(startdate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                while week <= today:
                    UnitSold=0
                    DeliverSale=0
                    StoreSale=0
                    order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today ).filter(Store_id=store)
                    for i in order:
                        if i.Order_Type == "Delivery":
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                                DeliverSale += j["Cart_Quantity"]
                        elif i.Order_Type == "Pickup":
                            for j in i.Product:
                                UnitSold += j["Cart_Quantity"]
                                StoreSale += j["Cart_Quantity"]
                    result = {"Date":week.strftime("%B"),"UnitSold":UnitSold,"DeliverSale":DeliverSale,"StoreSale":StoreSale}
                    z.append(result)
                    week=week + timedelta(days=1)
                for qwe in range(0,len(z)):
                    for rty in z:
                        if (z[qwe]==rty):
                            l.update(rty)
                return Response([l])
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
class SalesByCategoryGraph(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            selectTime=request.data.get("selectTime")
            store=request.data.get("store")
            startdate = request.data.get("StartDate")
            EndDate=request.data.get("EndDate")
            if selectTime=="Today":
                Delivered=Order.objects.filter(OrderDate__icontains=startdate).filter(Order_Status="Delivered").filter(Store_id=store)
                TotalOrder=Order.objects.filter(OrderDate__icontains=startdate).filter(Store_id=store)
                category_stats = []
                for order in Delivered:
                    if order.Order_Type == "Delivery":
                        for product in order.Product:
                            category_stats.append({
                                "category": product["category"],
                                "Item": product["Cart_Quantity"],
                                "Order": 1,  
                                "Amount": product["TotalPrice"]  
                            })
                    elif order.Order_Type == "Delivery":
                        for product in order.Product:
                            category_stats.append({
                                "category": product["category"],
                                "Item": product["Cart_Quantity"],
                                "Order": 1,  
                                "Amount": product["TotalPrice"]  
                            })
                for order in TotalOrder:
                    for product in order.Product:
                        found = False
                        for stat in category_stats:
                            if stat["category"] == product["category"]:
                                stat["Item"] += product["Cart_Quantity"]
                                stat["Order"] += 1
                                stat["Amount"] += product["TotalPrice"] 
                                found = True
                                break
                        if not found:
                            category_stats.append({
                                "category": product["category"],
                                "Item": product["Cart_Quantity"],
                                "Order": 1,
                                "Amount": product["TotalPrice"]  
                            })

                return Response(category_stats)
            if selectTime=="ThisWeek":
                week=datetime.strptime(startdate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                Delivered=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Order_Status="Delivered").filter(Store_id=store)
                TotalOrder=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Store_id=store)
                category_stats = []
                for order in Delivered:
                    for product in order.Product:
                        category_stats.append({
                            "category": product["category"],
                            "Item": product["Cart_Quantity"],
                            "Order": 1,  
                            "Amount": product["TotalPrice"]  
                        })
                for order in TotalOrder:
                    for product in order.Product:
                        found = False
                        for stat in category_stats:
                            if stat["category"] == product["category"]:
                                stat["Item"] += product["Cart_Quantity"]
                                stat["Order"] += 1
                                stat["Amount"] += product["TotalPrice"] 
                                found = True
                                break
                        if not found:
                            category_stats.append({
                                "category": product["category"],
                                "Item": product["Cart_Quantity"],
                                "Order": 1,
                                "Amount": product["TotalPrice"]  
                            })

                return Response(category_stats)
            if selectTime=="ThisMonth":
                week=datetime.strptime(startdate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                Delivered=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today ).filter(Order_Status="Delivered" ).filter(Store_id=store)
                TotalOrder=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Store_id=store)
                category_stats = []
                for order in Delivered:
                    for product in order.Product:
                        category_stats.append({
                            "category": product["category"],
                            "Item": product["Cart_Quantity"],
                            "Order": 1,  
                            "Amount": product["TotalPrice"]  
                        })
                for order in TotalOrder:
                    for product in order.Product:
                        found = False
                        for stat in category_stats:
                            if stat["category"] == product["category"]:
                                stat["Item"] += product["Cart_Quantity"]
                                stat["Order"] += 1
                                stat["Amount"] += product["TotalPrice"] 
                                found = True
                                break
                        if not found:
                            category_stats.append({
                                "category": product["category"],
                                "Item": product["Cart_Quantity"],
                                "Order": 1,
                                "Amount": product["TotalPrice"]  
                            })

                return Response(category_stats)
            if selectTime=="ThisYear":
                week=datetime.strptime(startdate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                Delivered=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today ).filter(Order_Status="Delivered").filter(Store_id=store)
                TotalOrder=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Store_id=store)
                category_stats = []
                for order in Delivered:
                    for product in order.Product:
                        category_stats.append({
                            "category": product["category"],
                            "Item": product["Cart_Quantity"],
                            "Order": 1,  
                            "Amount": product["TotalPrice"]  
                        })
                for order in TotalOrder:
                    for product in order.Product:
                        found = False
                        for stat in category_stats:
                            if stat["category"] == product["category"]:
                                stat["Item"] += product["Cart_Quantity"]
                                stat["Order"] += 1
                                stat["Amount"] += product["TotalPrice"] 
                                found = True
                                break
                        if not found:
                            category_stats.append({
                                "category": product["category"],
                                "Item": product["Cart_Quantity"],
                                "Order": 1,
                                "Amount": product["TotalPrice"]  
                            })

                return Response(category_stats)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VendorCardDashBoard(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            SelectTime=request.data.get("SelectTime",None)
            store=request.data.get("store")
            startdate = request.data.get("StartDate")
            EndDate=request.data.get("EndDate")
            if SelectTime=="Today":
                z=[]
                d=[]
                s=Order.objects.filter(Store_id=store).filter(OrderDate__icontains=startdate)
                PendingOrder=s.filter(Order_Status="Pending").count()
                CancelOrder=s.filter(Order_Status="Cancel").count()  
                OrderComplete=s.filter(Order_Status="Delivered").count()
                product=Product.objects.filter(created_by=request.user)  
                for i in s:
                    for j in i.Product:
                        d.append(j['TotalPrice'])
                f=sum(d)     
                for l in product:
                    weight=ProductWeight.objects.filter(product=l.id).first()
                    for m in weight.Price:
                        if m["Stock"]=="Out Stock":
                            z.append(m)
                return Response([{"title":"OrderInProgress","total":PendingOrder},
                                        {"title":"TotalSales","total":f},
                                        {"title":"CancelOrder","total":CancelOrder},
                                        {"title":"OrderComplete","total":OrderComplete}])
            else:
                z=[]
                d=[]
                week=datetime.strptime(startdate, '%Y-%m-%d')
                today=datetime.strptime(EndDate, '%Y-%m-%d')
                order=Order.objects.filter(OrderDate__gte=week,OrderDate__lt=today).filter(Store_id=store)
                PendingOrder=order.filter(Order_Status="Pending").count()
                CancelOrder=order.filter(Order_Status="Cancel").count()  
                OrderComplete=order.filter(Order_Status="Delivered").count()
                product=Product.objects.filter(created_by=request.user)  
                for i in order:
                    for j in i.Product:
                        d.append(j['TotalPrice'])
                f=sum(d)     
                for l in product:
                    weight=ProductWeight.objects.filter(product=l.id).first()
                    for m in weight.Price:
                        if m["Stock"]=="Out Stock":
                            z.append(m)
                return Response([{"title":"OrderInProgress","total":PendingOrder},
                                        {"title":"TotalSales","total":f},
                                        {"title":"CancelOrder","total":CancelOrder},
                                        {"title":"OrderComplete","total":OrderComplete}])
        except Exception as e:
            return Response({'error' : str(e)},status=500)  
        
