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


def send_OneToOneMail(from_email='', to_emails=''):
    Otp = random.randint(1000, 9999)
    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
    server.ehlo()
    server.starttls()
    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    Subject = "Selnox"
    Text = "Your One Time Password is " + str(Otp)

    msg = 'Subject: {}\n\n{}'.format(Subject, Text)
    server.sendmail(from_email, to_emails, msg)
    user = User.objects.get(email=to_emails)
    user.otp = Otp
    user.save()
    server.quit()


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
                send_OneToOneMail(
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

                user = User.objects.filter(email=email)
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
                        send_OneToOneMail(
                            from_email='smtpselnox@gmail.com', to_emails=email)
                        return Response({
                            'message': 'Email sent',
                            'data': {"Otp_Sent_to": email}
                        },status=status.HTTP_200_OK)
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
                    send_OneToOneMail(
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
               # data=json.dumps(serializer.data)
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

class AddApplyCoupoun(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            serializer = Serializer_Coupoun(data=request.data, partial=True)
            if serializer.is_valid():
                    serializer.save()
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
            User = get_object_or_404(Serializer_Coupoun, id=id)
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


class VendorCardDashBoard(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,format=None):
        try:
            d=[]
            a=Stores.objects.filter(created_by=request.user).first()
            s=Order.objects.filter(Store=a) 
            product=Product.objects.filter(created_by=request.user)
            TotalProduct=product.all().count()
            ActiveProduct=product.filter(Status="Active").count()
            for i in s:
                for j in i.Product:
                    d.append(j['TotalPrice'])
            f=sum(d)    
            PendingOrder=s.filter(Order_Status="Pending").count()
             
            # CancelOrder=s.filter(Order_Status="Cancel").count()  
            return Response([{"title":"TotalProduct","total":TotalProduct},
                                    {"title":"ActiveProduct","total":ActiveProduct},
                                    {"title":"RecentOrder","total":PendingOrder},
                                    {"title":"TotalIncome","total":f}])
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
            User = Order.objects.filter(Store=id)
            top=User.filter(Order_Status="Delivered")
            for i in top:
                for j in i.Product:
                    productCount=Order.objects.filter(Product__icontains=j["Product_id"]).count()
                    product=Product.objects.filter(id=j["Product_id"])
                    serialize=Serializer_Product(product,many=True)
                    x.append({"Product":serialize.data,"ProductSalesCount":productCount})
            x.sort(key = itemgetter('ProductSalesCount'), reverse=True)
            return Response(x)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
        

