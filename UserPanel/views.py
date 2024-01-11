#gunicorn --bind 0.0.0.0:8000 Ecommerce.wsgi
# docker run -p 8000:8000 ecommerce:latest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics, permissions
from AdminPanel.models import *
from AdminPanel.serializer import * 
from VendorPanel.serializer import *
from django.shortcuts import get_object_or_404
from AdminPanel.tokens import create_jwt_pair_for_user
from rest_framework.permissions import IsAuthenticated
from Ecommerce.settings import EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_PORT
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
import requests,smtplib,random
from rest_framework_simplejwt.tokens import RefreshToken   
from .serializer import *
from .ordercheck import sendmailoforderdetailsVendor,sendmailoforderdetailsCustomer,sendmailoforderdetailsAdmin


class Login(APIView): 
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = User.objects.filter(email=email).first()
                if user.user_type=="Customer":
               
                    if user is not None :
                        tokens = create_jwt_pair_for_user(user)
                        response = {"message": "Login Successfull", "tokens": tokens}
                        return Response(data=response, status=status.HTTP_200_OK)
                    else:
                        return Response(data={"message": "Invalid email or password"},status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response("Not Authorised")
            else:
                return Response(data={"message": "Invalid email or password"},status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            content = {"user": str(request.user), "auth": str(request.auth)}

            return Response(data=content, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            if not user:
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
    def post(self, request):
        try:
            email=request.data.get("email")
            password=request.data.get("password")
            user = User.objects.get(email=email)
            serializer = PasswordReseetSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                if not user:
                    return Response({
                        'message': 'Something goes wrong',
                        'data': 'invalid Email'
                    },status=status.HTTP_400_BAD_REQUEST)
               
                if len(password) > 5:
                    email=User.objects.get(email=email)
                    email.set_password(password)
                    email.save()
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


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = UserSerializer

    def get_object(self):
        try:
            return self.request.user
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserAlreadyExist(APIView):
    def post(self,request):
        try:
            email = request.data.get("email")
            if email:
                user=User.objects.filter(email=email)
                if user.exists():
                    return Response({"email": "Email is already Registered"})
                else:
                    return Response({"email": "Email is Not Registered"})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# Class based view to register user
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
                                user = serializer.save(user_type="Customer")

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

class ResetPassword(APIView):
    serializer_class = PasswordReseetSerializer
    model = User
    # permission_classes = (IsAuthenticated,)

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

#Category Api
class GetCategories(APIView):

    def get(self, request, format=None):
        try:
            User = Category.objects.select_related().all()
            serialize = Serializer_Category(User, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#SubCategory filter according to Category    

class GetSubCategory(APIView):
    def get(self,request,id=None):
        try:
            User = SubCategory.objects.filter(category_id=id)
            active=User.filter(Status="Active")
            serializer = Serializer_SubCategory(active,many=True)
            
            return Response({"status": "success", "data":serializer.data}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#Stores 
class GetStores(APIView):

    def get(self, request, format=None):
        try:
            User = Stores.objects.select_related().all()
            serialize = Serializer_Store(User, many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#Product
class GetAllProduct(APIView):
    def post(self, request, format=None):
        try:
            Country=request.data.get("Country")
            State=request.data.get("State")
            City=request.data.get("City")
            if City or State or Country:
                User = Product.objects.filter(Status="Active").filter(Store_id__City=City).order_by('-created_by')
                serialize = Serializer_Product(User, many=True)
                if len(User)==0:
                    User1 = Product.objects.filter(Status="Active").filter(Store_id__State=State).order_by('-created_by')
                    serialize1 = Serializer_Product(User1, many=True)
                    if len(User1)==0:
                        User2 = Product.objects.filter(Status="Active").filter(Store_id__Country=Country).order_by('-created_by')
                        serialize2 = Serializer_Product(User2, many=True)
                        return Response(serialize2.data)
                    return Response(serialize1.data)
                        
                return Response(serialize.data)
            else:
                return Response("No Product Found")
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
#All Product by Category
class ProductByCategorybyStore(APIView):
    def get(self,request,id=None):
        try:
            store_id=request.GET.get('store_id')
            user= Product.objects.filter(Sub_Category_id__category_id=id).filter(Store_id=store_id).filter(Status="Active")
            # active=Product.objects.filter(Status="Active")
            if user:
                serialize=Serializer_Product(user,many=True)
                return Response(serialize.data)
            else:
                return Response("There is no Product",status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ProductBySubCategory(APIView):
    def post(self,request,id=None):
        try:
            Country=request.data.get("Country")
            State=request.data.get("State")
            City=request.data.get("City")
            if City or State or Country:
                user=Product.objects.filter(Sub_Category_id=id).filter(Status="Active").filter(Store_id__Country=Country)
                serialize = Serializer_Product(user, many=True)
                if len(user)==0:
                    User1 = Product.objects.filter(Sub_Category_id=id).filter(Status="Active").filter(Store_id__State=State) 
                    serialize1 = Serializer_Product(User1, many=True)
                    if len(User1)==0:
                        User2 = Product.objects.filter(Sub_Category_id=id).filter(Status="Active").filter(Store_id__Country=Country)
                        serialize2 = Serializer_Product(User2, many=True)
                        return Response(serialize2.data)
                    return Response(serialize1.data)
                        
                return Response(serialize.data)
            else:
                return Response("No Product Found")
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class StoreByCities(APIView):
    def get(self,request,id=None):
        try:
            store=Stores.objects.filter(City_id=id)
            active=store.filter(Status="Active")
            if active:
                serialize=Serializer_Store(active,many=True)
                return Response(serialize.data,status=status.HTTP_200_OK)
            else:
                return Response("No Active Store in Your City",status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetNews(APIView):
    def get(self, request, format=None):
        try:
            z=[]
            User = News.objects.select_related().all()
            serialize=Serializer_News(User,many=True).data
            for i in serialize:
                a=BlogComment.objects.filter(Blog=i["id"]).count()
                b=BlogLike.objects.filter(Blog=i["id"]).count()
                c=BlogView.objects.filter(blog=i["id"]).first()
                response={"id":i["id"],"Title":i["Title"],"Description":i["Description"],"username":i["username"],"Image":i["Image"],"Publish_Date":i["Publish_Date"],"likeCount":a,"commentCount":b,"ViewCount":i["ViewCount"]}
                z.append(response)
            return Response(z)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetAllDispensaries(APIView):
    def post(self,request,format=None):
        try:
            Country=request.data.get("Country")
            State=request.data.get("State")
            City=request.data.get("City")
            if City or State or Country:
                user = Stores.objects.filter(Store_Type="dispensary").filter(Status="Active").filter(City=City)
                serialize=Serializer_Store(user,many=True)
                if len(user) == 0:
                    user1 = Stores.objects.filter(Store_Type="dispensary").filter(Status="Active").filter(State=State)
                    serialize1=Serializer_Store(user1,many=True)
                    if len(user1)==0:
                        user2 = Stores.objects.filter(Store_Type="dispensary").filter(Status="Active").filter(Country=Country)
                        serialize2=Serializer_Store(user2,many=True)
                        return Response(serialize2.data,status=status.HTTP_200_OK)
                    return Response(serialize1.data,status=status.HTTP_200_OK)
                return Response(serialize.data,status=status.HTTP_200_OK)
            else:
                return Response("No Dispensary in your area")
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class GetAllDelivery(APIView):
    def get(self,request,format=None):
        try:
            user = Stores.objects.filter(Store_Type="delivery")
            active=user.filter(Status="Active")
            if active:
                serialize=Serializer_Store(user,many=True)
                return Response(serialize.data,status=status.HTTP_200_OK)
            else:
                return Response("No Available Delivery",status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
class GetDispensaryByid(APIView):
    def get(self,request,id=None):
        try:
            store=Stores.objects.filter(id=id)
            dispensary=store.filter(Store_Type='dispensary')
            if store:
                serialize=Serializer_Store(dispensary,many=True)
                return Response(serialize.data,status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SortingFilter(APIView):
    def get(self,request,id=None):
        try:
            
            product=Product.objects.filter(Store_id=id).order_by("Product_Name")
            serialize=Serializer_Product(product,many=True)
            return Response(serialize.data,status=status.HTTP_200_OK)
        except Exception as e:
             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductAccordingToDispensaries(APIView):
    def get(self,request,id=None):
        try:
            product=Product.objects.filter(Store_id=id).filter(Status="Active")     
            serialize=Serializer_Product(product,many=True)
            return Response(serialize.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetProductById(APIView):
    def get(self,request,id=None):
        try:
            product=Product.objects.filter(id=id)
            serialize=Serializer_Product(product,many=True)
            # review=Review.objects.filter(product=id)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from VendorPanel.serializer import *

class CategoryOnProduct(APIView):
    # permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            product=Product.objects.all()
            serialize=Serializer_CategoryinProduct(product,many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetStrainType(APIView):
    def post(self,request):
        try:
            user=request.data.get("type")
            product=Product.objects.filter(strain=user)
            serialize=Serializer_Product(product,many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
from .serializer import *      
class GetFilterBrand(APIView):
    def get(self,request):
        try:
            product=Brand.objects.all()
            serialize=Serializer_FilterBrand(product,many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class GetProductbyBrand(APIView):
    def get(self,request,id=None):
        try:
            product=Product.objects.filter(Brand_id=id)
            serialize=Serializer_Product(product,many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductByCategory(APIView):
    def post(self,request,id=None):
        try:
            
            Country=request.data.get("Country")
            State=request.data.get("State")
            City=request.data.get("City")        
            if City or State or Country: 
                user= Product.objects.filter(Sub_Category_id__category_id=id).filter(Status="Active").filter(Store_id__City=City)
                if len(user)!=0:
                    serialize=Serializer_Product(user,many=True)
                    return Response(serialize.data)
                else:
                    user1= Product.objects.filter(Sub_Category_id__category_id=id).filter(Status="Active").filter(Store_id__State=State)
                    if len(user1)!=0:
                        serialize1=Serializer_Product(user1,many=True)
                        return Response(serialize1.data)
                    else:
                        user2= Product.objects.filter(Sub_Category_id__category_id=id).filter(Status="Active").filter(Store_id__Country=Country)
                        if len(user2)!=0:
                            serialize1=Serializer_Product(user1,many=True)
                            return Response(serialize1.data)
                        else:
                            return Response("There is no Product")
            else:
                return Response("No Product Found")
                        
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        


class GetAddtocart(APIView):
    permission_classes_by_action = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            a=[]
            User = AddtoCart.objects.filter(created_by=request.user)
            for i in User:
                image=ProductImage.objects.filter(product=i.Product_id).first()
                product=ProductWeight.objects.filter(product_id=i.Product_id).first()
                for j in product.Price:
                    if j["id"]==i.Price["id"]:
                        if i.Brand_Id !=None and i.Image_id != None:
                            response={"id":i.id,"username":i.created_by.username,"StoreName":i.Store_id.Store_Name,"ProductName":i.Product_id.Product_Name,"Image":image.image.url,
                                    "StoreDelivery":i.Store_id.Delivery,"StorePickup":i.Store_id.StoreFront,"StoreCurbsidePickup":i.Store_id.CurbSide_Pickup,"StoreAddress":i.Store_id.Store_Address,
                                    "StoreHours":i.Store_id.Hours,"StoreCurbSidePickupHours":i.Store_id.CurbSidePickupHours,"SubcategoryName":i.Sub_Category_id.name,"Cart_Quantity":i.Cart_Quantity,
                                    "Price":j,"TotalPrice":i.TotalPrice,"category":i.category,"created_by":i.created_by.id,"Product_id":i.Product_id.id,"Store_id":i.Store_id.id,"Image_id":i.Image_id.id,
                                    "Brand_Id":i.Brand_Id.id,"Sub_Category_id":i.Sub_Category_id.id,"CoupounField":i.CoupounField,"CustomerGets":i.CustomerGets}
                            a.append(response)
                        elif i.Brand_Id ==None:
                            response={"id":i.id,"username":i.created_by.username,"StoreName":i.Store_id.Store_Name,"ProductName":i.Product_id.Product_Name,"Image":image.image.url,
                                    "StoreDelivery":i.Store_id.Delivery,"StorePickup":i.Store_id.StoreFront,"StoreCurbsidePickup":i.Store_id.CurbSide_Pickup,"StoreAddress":i.Store_id.Store_Address,
                                    "StoreHours":i.Store_id.Hours,"StoreCurbSidePickupHours":i.Store_id.CurbSidePickupHours,"SubcategoryName":i.Sub_Category_id.name,"Cart_Quantity":i.Cart_Quantity,
                                    "Price":j,"TotalPrice":i.TotalPrice,"category":i.category,"created_by":i.created_by.id,"Product_id":i.Product_id.id,"Store_id":i.Store_id.id,"Image_id":i.Image_id.id,
                                    "Brand_Id":i.Brand_Id,"Sub_Category_id":i.Sub_Category_id.id,"CoupounField":i.CoupounField,"CustomerGets":i.CustomerGets}
                            a.append(response)
                        elif i.Image_id == None:
                            response={"id":i.id,"username":i.created_by.username,"StoreName":i.Store_id.Store_Name,"ProductName":i.Product_id.Product_Name,"Image":image.image.url,
                                    "StoreDelivery":i.Store_id.Delivery,"StorePickup":i.Store_id.StoreFront,"StoreCurbsidePickup":i.Store_id.CurbSide_Pickup,"StoreAddress":i.Store_id.Store_Address,
                                    "StoreHours":i.Store_id.Hours,"StoreCurbSidePickupHours":i.Store_id.CurbSidePickupHours,"SubcategoryName":i.Sub_Category_id.name,"Cart_Quantity":i.Cart_Quantity,
                                    "Price":j,"TotalPrice":i.TotalPrice,"category":i.category,"created_by":i.created_by.id,"Product_id":i.Product_id.id,"Store_id":i.Store_id.id,"Image_id":i.Image_id,
                                    "Brand_Id":i.Brand_Id.id,"Sub_Category_id":i.Sub_Category_id.id,"CoupounField":i.CoupounField,"CustomerGets":i.CustomerGets}
                            a.append(response)
                        elif i.Brand_Id ==None and i.Image_id == None:
                            response={"id":i.id,"username":i.created_by.username,"StoreName":i.Store_id.Store_Name,"ProductName":i.Product_id.Product_Name,"Image":image.image.url,
                                    "StoreDelivery":i.Store_id.Delivery,"StorePickup":i.Store_id.StoreFront,"StoreCurbsidePickup":i.Store_id.CurbSide_Pickup,"StoreAddress":i.Store_id.Store_Address,
                                    "StoreHours":i.Store_id.Hours,"StoreCurbSidePickupHours":i.Store_id.CurbSidePickupHours,"SubcategoryName":i.Sub_Category_id.name,"Cart_Quantity":i.Cart_Quantity,
                                    "Price":j,"TotalPrice":i.TotalPrice,"category":i.category,"created_by":i.created_by.id,"Product_id":i.Product_id.id,"Store_id":i.Store_id.id,"Image_id":i.Image_id,
                                    "Brand_Id":i.Brand_Id,"Sub_Category_id":i.Sub_Category_id.id,"CoupounField":i.CoupounField,"CustomerGets":i.CustomerGets}
                            a.append(response)
                        else:
                            response={"id":i.id,"username":i.created_by.username,"StoreName":i.Store_id.Store_Name,"ProductName":i.Product_id.Product_Name,"Image":image.image.url,
                                    "StoreDelivery":i.Store_id.Delivery,"StorePickup":i.Store_id.StoreFront,"StoreCurbsidePickup":i.Store_id.CurbSide_Pickup,"StoreAddress":i.Store_id.Store_Address,
                                    "StoreHours":i.Store_id.Hours,"StoreCurbSidePickupHours":i.Store_id.CurbSidePickupHours,"SubcategoryName":i.Sub_Category_id.name,"Cart_Quantity":i.Cart_Quantity,
                                    "Price":j,"TotalPrice":i.TotalPrice,"category":i.category,"created_by":i.created_by.id,"Product_id":i.Product_id.id,"Store_id":i.Store_id.id,"Image_id":"",
                                    "Brand_Id":"","Sub_Category_id":i.Sub_Category_id.id,"CoupounField":i.CoupounField,"CustomerGets":i.CustomerGets}
                            a.append(response)

            return Response(a)

        except Exception as e:
            return Response({'error' : str(e)},status=500)


class AddAddtoCart(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            Store_id=request.data.get('Store_id')
            Product_id=request.data.get('Product_id')
            PriceId=request.data.get('PriceId')
            PromoCodeid=request.data.get("PromoCodeid")
            serializer = Serializer_AddtoCart(data=request.data, partial=True)
            if serializer.is_valid():
                User = AddtoCart.objects.filter(created_by=request.user)    
                if User:
                    for i in User:
                        if i.Store_id_id == Store_id:
                            s=User.filter(Product_id_id=Product_id)
                            if s:
                                d=s.filter(Price__id=PriceId)
                                if d:
                                    User = d.first()
                                    a=User.Cart_Quantity+request.data.get("Cart_Quantity")
                                    if User.Price["Quantity"]>= a:
                                        data = {"Cart_Quantity": a} 
                                        serialize=Serializer_AddtoCart(User,data=data,partial=True)
                                        if serialize.is_valid():
                                            serialize.save(update_fields=[{"Cart_Quantity": data}]) 
                                            coupoun=Coupoun.objects.filter(id=PromoCodeid).first()
                                            if coupoun:
                                                cart=AddtoCart.objects.filter(created_by=request.user)
                                                if cart:
                                                    for q in cart:
                                                        if q.CoupounField !=None:
                                                            for o in q.Price["Coupoun"]:       
                                                                if PromoCodeid==o["id"]:
                                                                    if PromoCodeid==q.CoupounField["id"]:
                                                                        pass
                                                                    else:
                                                                        CoupounField={"CoupounField":None}
                                                                        addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                                        if addtocartupdate.is_valid():
                                                                            addtocartupdate.save()
                                                                else:
                                                                    CoupounField={"CoupounField":None}
                                                                    addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                                    if addtocartupdate.is_valid():
                                                                        addtocartupdate.save()
                                                        else:
                                                            for o in q.Price["Coupoun"]:
                                                                if PromoCodeid==o["id"]:
                                                                    if coupoun.PercentageAmount:
                                                                        coupounField={"CoupounField":{"Product": q.Product_id_id, "Amount": None, "Reflect": False, "Percentage": coupoun.PercentageAmount, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "AutomaticDiscount": coupoun.AutomaticDiscount,"id":coupoun.id,"price":request.data["CoupounField"]["price"]}}
                                                                        addtocartupdate=Serializer_AddtoCart(q,data=coupounField,partial=True)
                                                                        if addtocartupdate.is_valid():
                                                                            addtocartupdate.save()
                                                                    elif coupoun.ValueAmount:
                                                                        CoupounField={"CoupounField":{"Product": q.Product_id_id, "Amount": coupoun.ValueAmount, "Reflect": False, "Percentage":None, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "AutomaticDiscount": coupoun.AutomaticDiscount,"id":coupoun.id,"price":request.data["CoupounField"]["price"]}}
                                                                        addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                                        if addtocartupdate.is_valid():
                                                                            addtocartupdate.save()
                                                                else:
                                                                    CoupounField={"CoupounField":None}
                                                                    addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                                    if addtocartupdate.is_valid():
                                                                        addtocartupdate.save()
    
                                            return Response({"status": "Update success", "data": serializer.data}, status=status.HTTP_200_OK)
                                        else:
                                            return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
                                    else:
                                        return Response({"Out of Stock"},status=status.HTTP_406_NOT_ACCEPTABLE)
                                else:
                                    serializer.save(created_by=request.user)
                                    coupoun=Coupoun.objects.filter(id=PromoCodeid).first()
                                    if coupoun:
                                        cart=AddtoCart.objects.filter(created_by=request.user)
                                        if cart:
                                            for q in cart:
                                                if q.CoupounField !=None:
                                                    for o in q.Price["Coupoun"]:
                                                        if PromoCodeid==o["id"]:
                                                            if PromoCodeid==q.CoupounField["id"]:
                                                                pass
                                                            else:
                                                                CoupounField={"CoupounField":None}
                                                                addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                                if addtocartupdate.is_valid():
                                                                    addtocartupdate.save()
                                                        else:
                                                            CoupounField={"CoupounField":None}
                                                            addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                            if addtocartupdate.is_valid():
                                                                addtocartupdate.save()
                                                else:
                                                    for o in q.Price["Coupoun"]:
                                                        if PromoCodeid==o["id"]:
                                                            if coupoun.PercentageAmount:
                                                                coupounField={"CoupounField":{"Product": q.Product_id_id, "Amount": None, "Reflect": False, "Percentage": coupoun.PercentageAmount, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "AutomaticDiscount": coupoun.AutomaticDiscount,"id":coupoun.id,"price":request.data["CoupounField"]["price"]}}
                                                                addtocartupdate=Serializer_AddtoCart(q,data=coupounField,partial=True)
                                                                if addtocartupdate.is_valid():
                                                                    addtocartupdate.save()
                                                            elif coupoun.ValueAmount:
                                                                CoupounField={"CoupounField":{"Product": q.Product_id_id, "Amount": coupoun.ValueAmount, "Reflect": False, "Percentage":None, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "AutomaticDiscount": coupoun.AutomaticDiscount,"id":coupoun.id,"price":request.data["CoupounField"]["price"]}}
                                                                addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                                if addtocartupdate.is_valid():
                                                                    addtocartupdate.save()
                                                        else:
                                                            CoupounField={"CoupounField":None}
                                                            addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                            if addtocartupdate.is_valid():
                                                                addtocartupdate.save()
                                    else:
                                        CoupounField={"CoupounField":None}
                                        addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                        if addtocartupdate.is_valid():
                                            addtocartupdate.save()
                                    return Response({"status": "New Add to cart","data": serializer.data}, status=status.HTTP_200_OK)                  
                            else:
                                
                                serializer.save(created_by=request.user)
                                coupoun=Coupoun.objects.filter(id=PromoCodeid).first()
                                if coupoun:
                                    cart=AddtoCart.objects.filter(created_by=request.user)
                                    if cart:
                                        for q in cart:
                                            if q.CoupounField !=None:
                                                for o in q.Price["Coupoun"]:
                                                    if PromoCodeid==o["id"]:
                                                        if PromoCodeid==q.CoupounField["id"]:
                                                            pass
                                                        else:
                                                            CoupounField={"CoupounField":None}
                                                            addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                            if addtocartupdate.is_valid():
                                                                addtocartupdate.save()
                                                    else:
                                                        CoupounField={"CoupounField":None}
                                                        addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                        if addtocartupdate.is_valid():
                                                            addtocartupdate.save()
                                            else:
                                                for o in q.Price["Coupoun"]:
                                                    if PromoCodeid==o["id"]:
                                                        if coupoun.PercentageAmount:
                                                            coupounField={"CoupounField":{"Product": q.Product_id_id, "Amount": None, "Reflect": False, "Percentage": coupoun.PercentageAmount, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "AutomaticDiscount": coupoun.AutomaticDiscount,"id":coupoun.id,"price":request.data["CoupounField"]["price"]}}
                                                            addtocartupdate=Serializer_AddtoCart(q,data=coupounField,partial=True)
                                                            if addtocartupdate.is_valid():
                                                                addtocartupdate.save()
                                                        elif coupoun.ValueAmount:
                                                            CoupounField={"CoupounField":{"Product": q.Product_id_id, "Amount": coupoun.ValueAmount, "Reflect": False, "Percentage":None, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "AutomaticDiscount": coupoun.AutomaticDiscount,"id":coupoun.id,"price":request.data["CoupounField"]["price"]}}
                                                            addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                            if addtocartupdate.is_valid():
                                                                addtocartupdate.save()
                                                    else:
                                                        CoupounField={"CoupounField":None}
                                                        addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                        if addtocartupdate.is_valid():
                                                            addtocartupdate.save()

                                return Response({"status": "success","data": serializer.data}, status=status.HTTP_200_OK)
                        else:
                            return Response('Empty Add to Cart',status=status.HTTP_201_CREATED) 
                else:
                    serializer.save(created_by=request.user)
                    coupoun=Coupoun.objects.filter(id=PromoCodeid).first()
                    if coupoun:
                        cart=AddtoCart.objects.filter(created_by=request.user)
                        if cart:
                            for q in cart:
                                if q.CoupounField !=None:
                                    for o in q.Price["Coupoun"]:
                                        if PromoCodeid==o["id"]:
                                            if q.CoupounField !=None:
                                                if PromoCodeid==q.CoupounField["id"]:
                                                    pass
                                                else:
                                                    CoupounField={"CoupounField":None}
                                                    addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                    if addtocartupdate.is_valid():
                                                        addtocartupdate.save()
                                            else:
                                                for o in q.Price["Coupoun"]:
                                                    if PromoCodeid==o["id"]:
                                                        if coupoun.PercentageAmount:
                                                            coupounField={"CoupounField":{"Product": q.Product_id_id, "Amount": None, "Reflect": False, "Percentage": coupoun.PercentageAmount, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "AutomaticDiscount": coupoun.AutomaticDiscount,"id":coupoun.id,"price":request.data["CoupounField"]["price"]}}
                                                            addtocartupdate=Serializer_AddtoCart(q,data=coupounField,partial=True)
                                                            if addtocartupdate.is_valid():
                                                                addtocartupdate.save()
                                                        elif coupoun.ValueAmount:
                                                            CoupounField={"CoupounField":{"Product": q.Product_id_id, "Amount": coupoun.ValueAmount, "Reflect": False, "Percentage":None, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "AutomaticDiscount": coupoun.AutomaticDiscount,"id":coupoun.id,"price":request.data["CoupounField"]["price"]}}
                                                            addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                            if addtocartupdate.is_valid():
                                                                addtocartupdate.save()
                                                    else:
                                                        CoupounField={"CoupounField":None}
                                                        addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                        if addtocartupdate.is_valid():
                                                            addtocartupdate.save()
                                else:
                                    for o in q.Price["Coupoun"]:
                                        if PromoCodeid==o["id"]:
                                            if coupoun.PercentageAmount:
                                                coupounField={"CoupounField":{"Product": q.Product_id_id, "Amount": None, "Reflect": False, "Percentage": coupoun.PercentageAmount, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "AutomaticDiscount": coupoun.AutomaticDiscount,"id":coupoun.id,"price":request.data["CoupounField"]["price"]}}
                                                addtocartupdate=Serializer_AddtoCart(q,data=coupounField,partial=True)
                                                if addtocartupdate.is_valid():
                                                    addtocartupdate.save()
                                            elif coupoun.ValueAmount:
                                                CoupounField={"CoupounField":{"Product": q.Product_id_id, "Amount": coupoun.ValueAmount, "Reflect": False, "Percentage":None, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "AutomaticDiscount": coupoun.AutomaticDiscount,"id":coupoun.id,"price":request.data["CoupounField"]["price"]}}
                                                addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                                if addtocartupdate.is_valid():
                                                    addtocartupdate.save()
                                        else:
                                            CoupounField={"CoupounField":None}
                                            addtocartupdate=Serializer_AddtoCart(q,data=CoupounField,partial=True)
                                            if addtocartupdate.is_valid():
                                                addtocartupdate.save()

                    return Response({"status": "New Add to Cart","data": serializer.data},status=status.HTTP_200_OK)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class UpdateAddtoCart(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            User = AddtoCart.objects.get(id=id)
            serializer = Serializer_AddtoCart(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.username)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DeleteAddtoCart(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            User = get_object_or_404(AddtoCart, id=id)
            User.delete()
            return Response({"status": "success", "data": "Deleted"})
        except Exception as e:
            return Response({'error' : str(e)},status=500)    


class ClearAddtoCart(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            AddtoCart.objects.filter(created_by=request.user).delete()
            serializer = Serializer_AddtoCart(data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error' : str(e)},status=500)


class GetAddtoCartImage(APIView):
    def get(self,request,id=None):
        try:
            image=ProductImage.objects.filter(id=id)
            serialize=ProductImageSerializer(image,many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class GetOrder(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = Order.objects.filter(created_by=request.user)
            serialize = Serializer_Order(User, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
    
    
from .ordercheck import sendmailoforderdetailsVendor,sendmailoforderdetailsCustomer
    
    
class AddOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            index=0
            w=[]
            d=[]
            f=[]
            q=[]
            Store=request.data.get('Store')
            serializer = Serializer_Order(data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                a=Order.objects.filter(created_by=request.user).last()
                noti={"OrderStausUpdate":a.OrderId}
                notiserialize=Serializer_UserNotification(data=noti,partial=True)
                if notiserialize.is_valid():
                    notiserialize.save()
                AddtoCart.objects.filter(created_by=request.user).delete()
                User=Order.objects.filter(created_by=request.user).filter(Store=Store).first()
                Customer=User.created_by.email
                CustomerName=User.created_by.username
                vendoremail=User.Store.created_by.email
                storeaddress=User.Store.Store_Address
                s=a.Product
                icard=a.IdCard
                Store_Name=User.Store.Store_Name
                if len(s):
                    for i in s:
                        d.append(i["ProductName"])
                        e=i["StoreName"]
                        w.append(i["Price"]["Weight"])
                        f.append(i["Cart_Quantity"])
                        q.append(i["Price"]["SalePrice"])
                        zxc=Product.objects.filter(id=i["Product_id"]).first()
                        serialize=Serializer_Product(zxc).data
                        z=serialize["Prices"] 
                        for j in z:
                            for k in j["Price"]:
                                if k["id"]==i["Price"]["id"]:   
                                    k.update({ "Quantity" : k["Quantity"] - i["Cart_Quantity"]})
                                    if k["Quantity"]<1:
                                        k.update({ "Stock" : "Out of Stock"})
                                    weight=ProductWeight.objects.filter(product=i["Product_id"]).first()
                                    serializer1 = ProductWeightSerializer(weight, data=j, partial=True)
                                    if serializer1.is_valid():
                                        serializer1.save()
                sendmailoforderdetailsVendor(email_to=vendoremail,OrderId=a.OrderId,subtotal=a.subtotal,Address=a.Address,ProductName=d,Weight=w,Quantity=f,Price=q,storeaddress=storeaddress,IdCard=icard,CustomerName=CustomerName,Store_Name=Store_Name)
                sendmailoforderdetailsCustomer(email_to=Customer,OrderId=a.OrderId,subtotal=a.subtotal,Address=a.Address,ProductName=d,Weight=w,Quantity=f,Price=q,storeaddress=storeaddress,CustomerName=CustomerName)
                sendmailoforderdetailsAdmin(email_to="selnox88@gmail.com",OrderId=a.OrderId,subtotal=a.subtotal,Address=a.Address,ProductName=d,Weight=w,Quantity=f,Price=q,storeaddress=storeaddress,IdCard=z,CustomerName=CustomerName,Store_Name=Store_Name)
                return Response({"status": "success","data": serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UpdateOrder(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, id=None):
        try:
            cancel=request.data.get("cancel",None)
            User = Order.objects.get(OrderId=id)
            serializer = Serializer_Order(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.username)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            if cancel:
                for i in User["Product"]:
                    i["Cart_Quantity"],i["Quantity"]
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteOrder(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            User = get_object_or_404(Order, id=id)
            User.delete()
            return Response({"status": "success", "data": "Deleted"})
        except Exception as e:
            return Response({'error' : str(e)},status=500)


class GetDeliveryStores(APIView):

    def post(self, request):
        try:
            Country=request.data.get("Country") 
            State=request.data.get("State")
            City=request.data.get("City")
            a=[] 
            if Country or State or City:
                Delivery = Stores.objects.filter(Order_Type="Delivery")
                DeliveryandPickup=Stores.objects.filter(Store_Type="Delivery and Pickup")
                User=Delivery or DeliveryandPickup
                addressCheck=User.filter(City=City) or User.filter(Country=Country) or User.filter(State=State)
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

            else:
                return Response({"message":"No Delivery Found in your Area"})
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
        
        
class GetPickupStores(APIView):

    def get(self, request):
        try:
            Delivery = Stores.objects.filter(Order_Type="Pickup")
            DeliveryandPickup=Stores.objects.filter(Order_Type="Delivery and Pickup")
            User=Delivery or DeliveryandPickup
            serialize = Serializer_Store(User, many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GetWishList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            q=[]
            User = Wishlist.objects.filter(created_by=request.user)
            for i in User:
                a=Product.objects.filter(id=i.product.id)       
                serialize = Serializer_Product(a, many=True).data
                for j in serialize:
                    q.append(j)
            return Response(q) 
        except Exception as e:
            return Response({'error' : str(e)},status=500)  
    
    
class AddWishList(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            product=request.data.get("product")
            a=Wishlist.objects.filter(created_by=request.user)
            s=a.filter(product=product).first()
            if s:
                User = get_object_or_404(Wishlist, id=s.id)
                User.delete()
                return Response({"status": "success", "data": "Remove From WishList"})
            else:
                serializer = Serializer_Wishlist(data=request.data,partial=True)
                if serializer.is_valid():
                    serializer.save(created_by=request.user)
                    return Response({"status": "success","data": serializer.data},status=status.HTTP_200_OK)
                else:
                    return Response({ "error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateWishList(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            

            User = Wishlist.objects.get(id=id)
            serializer = Serializer_Wishlist(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.username)
                return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    

class DeleteWishList(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            User = get_object_or_404(Wishlist, id=id)
            User.delete()
            return Response({"status": "success", "data": "Deleted"})
        except Exception as e:
            return Response({'error' : str(e)},status=500)
 
class AllSubCategory(APIView):
    def get(self,request):
        try:
            category=Category.objects.all()
            serailize=Serializer_CategoryName(category,many=True)
            return Response(serailize.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=500)


#Brand
class GetBrand(APIView):

    def get(self, request, format=None):
        try:
            User = Brand.objects.all()
            serialize = Serializer_Brand(User, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryByStore(APIView):
    def post(self,request):
        try:
            s=[]
            Store_Id=request.data.get("Store_Id")
            product=Product.objects.filter(Store_id=Store_Id)
            for i in product:
                a=SubCategory.objects.filter(id=i.Sub_Category_id_id)
                for j in a:
                    b=Category.objects.filter(id=j.category_id_id)
                    serialize=Serializer_Category(b,many=True)
                    s.append(serialize.data)
                
            return Response(s,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=500)


class filterSubcategorybyStoreandCategory(APIView):
    def post(self,request):
        try:
            k=[]
            # l=[]
            Store_Id=request.data.get("Store_Id")
            Category_Id=request.data.get("Category_Id")
            product=Product.objects.filter(Store_id=Store_Id)
            
            
            for i in product:
                a=SubCategory.objects.filter(id=i.Sub_Category_id_id)
                s=a.filter(category_id_id=Category_Id)
                for j in s:
                    response={"SubCategory_name":j.name,"id":j.id,"CatgoryId":j.category_id.id}
                    k.append(response)
            return Response(k,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class filterProductbyStoreandSubCategory(APIView):
    def post(self,request):
        try:
            Store_Id=request.data.get("Store_Id")
            SubCategory_Id=request.data.get("SubCategory_Id")
            product=Product.objects.filter(Store_id=Store_Id)
            a=product.filter(Sub_Category_id=SubCategory_Id)
            serialize=Serializer_Product(a,many=True)
            return Response(serialize.data,status=status.HTTP_200_OK)
                
        except Exception as e:  
            return Response({'error' : str(e)},status=500)

class filterProductbyStoreandCategory(APIView):
    def post(self,request):
        try:
            Category_Id=request.data.get('Category_Id')
            Store_Id=request.data.get('Store_Id')
            user= Product.objects.filter(Sub_Category_id__category_id_id=Category_Id).filter(Store_id=Store_Id).filter(Status="Active")
            if user:
                serialize=Serializer_Product(user,many=True)
                return Response(serialize.data)
            else:
                return Response("There is no Product",status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HomePageFilter(APIView):
    def post(self,request):
        try:
            search=request.data.get("search", None)
            product=Product.objects.all()
            store=Stores.objects.all()
            brand=Brand.objects.all()
            category=Category.objects.all()
            subcategory=SubCategory.objects.all()
            if search:
                a=product.filter(Product_Name__icontains=search)
                s=store.filter(Store_Name__icontains=search)
                d=brand.filter(name__icontains=search)
                f=category.filter(name__icontains=search)
                g=subcategory.filter(name__icontains=search)
                if a or s or d or f or g:
                    if a:
                        serialize1=Serializer_Product(a,many=True).data
                        h={"Product":serialize1}
                    if s:
                        serialize2=Serializer_Store(s,many=True).data
                        h={"Store":serialize2}
                        if a:
                            h={"Product":serialize1,"Store":serialize2}
                    if d:
                        serialize3=Serializer_Brand(d,many=True).data
                        h={"Brand":serialize3}
                        if a:
                            h={"Product":serialize1,"Brand":serialize3}
                        if s:
                            h={"Store":serialize2,"Brand":serialize3}
                        if a and s:
                            h={"Product":serialize1,"Store":serialize2,"Brand":serialize3}
                    if f:
                        serialize4=Serializer_Category(f,many=True).data
                        h={"Category":serialize4}
                        if a:
                            h={"Product":serialize1,"Category":serialize4}
                        if s:
                            h={"Store":serialize2,"Category":serialize4}
                        if d:
                            h={"Brand":serialize3,"Category":serialize4}
                        if a and s:
                            h= {"Product":serialize1,"Store":serialize2,"Category":serialize4}
                        if a and s and d:
                            h= {"Product":serialize1,"Store":serialize2,"Brand":serialize3,"Category":serialize4}
                    if g:
                        serialize5=Serializer_SubCategory(g,many=True).data
                        h={"Sub_Category":serialize5}
                        if a:
                            h={"Product":serialize1,"Sub Category":serialize5}
                        if s:
                            h= {"Store":serialize2,"Sub Category":serialize5}
                        if d:
                            h ={"Brand":serialize3,"Sub Category":serialize5}
                        if f:
                            h={"Category":serialize4,"Sub Category":serialize5}
                        if a and s:
                            h= {"Product":serialize1,"Store":serialize2,"Sub Category":serialize5}
                        if a and s and d:
                            h= {"Product":serialize1,"Store":serialize2,"Brand":serialize3,"Sub Category":serialize5}
                        if a and s and d and f:
                            h= {"Product":serialize1,"Store":serialize2,"Brand":serialize3,"Category":serialize4,"Sub Category":serialize5}
                    return Response(h)
                else:
                    return Response("Not Found",status=status.HTTP_202_ACCEPTED)
            else:
                return Response("Blank",status=status.HTTP_202_ACCEPTED)
        except Exception as e:  
             return Response({'error' : str(e)},status=500)


from urllib.parse import unquote
import random            
class GoogleView(APIView):
    def post(self, request):
        a=random.randint(10, 99)
        payload = {'access_token': request.data.get("token")}  # validate the token
        r = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', params=payload)
        data = json.loads(r.text)

        if 'error' in data:
            content = {'message': 'wrong google token / this google token is already expired.'}
            return Response(content,status=status.HTTP_400_BAD_REQUEST)

        # create user if not exist
        try:
            user = User.objects.get(email=data['email'])
            
        except User.DoesNotExist:
            user = User()
            s = User.objects.filter(username=data['name'])
            if s:
                user.username = data['name']+str(a)
            else:
                user.username = data['name']
            # provider random default password
            user.password = make_password(BaseUserManager().make_random_password())
            user.email = data['email']
            user.image=unquote(data['picture'])
            user.user_type="Customer"
            user.save()

        token = RefreshToken.for_user(user)  # generate token without username & password
        response = {}
        response['username'] = user.username
        response['email']=user.email
        response['access_token'] = str(token.access_token)
        response['refresh_token'] = str(token)
        response['picture']=unquote(user.image)
        return Response(response)



class AllHomePageBanner(APIView):
    def get(self,request):
        try:
            category=HomePageBanner.objects.all()
            serailize=Serializer_HomePageBanner(category,many=True)
            return Response(serailize.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=500)



class ResultHomeSearchFilter(APIView):
    def post(self,request):
        try:
            type=request.data.get('type')
            id=request.data.get('id')
            if type and id:
                if type == "Product":
                    product=Product.objects.filter(id=id)
                    serialize=Serializer_Product(product,many=True).data
                if type == "Store":
                    store=Stores.objects.filter(id=id)
                    serialize=Serializer_Store(store,many=True).data
                if type == "Brand":
                    brand=Brand.objects.filter(id=id)
                    serialize=Serializer_Brand(brand,many=True).data
                if type == "Category":
                    category=Category.objects.filter(id=id)
                    serialize=Serializer_Category(category,many=True).data
                if type == "Sub_Category":
                    subcategory=SubCategory.objects.filter(id=id)
                    serialize=Serializer_SubCategory(subcategory,many=True).data
                return Response({type:serialize})
            else:
                return Response({"Not Found"})
                    
        except Exception as e:
            return Response({'error':str(e)},status=500)


class GetBrandById(APIView):
    def get(self,request,id=None):
        try:
            product=Brand.objects.filter(id=id)
            serialize=Serializer_Brand(product,many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetDispensary(APIView):
    def get(self,request,id=None):
        try:
            store=Stores.objects.filter(Store_Type='dispensary')
            serialize=Serializer_Store(store,many=True)
            return Response(serialize.data,status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetStoreById(APIView):
    def get(self,request,id=None):
        try:
            user=Stores.objects.filter(id=id)
            serialize=Serializer_Store(user,many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)  


class GetReview(APIView):
    def get(self, request, id=None):
        try:
            User = Review.objects.filter(product=id)
            serialize = ReviewSerializer(User, many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
    
    
class AddReview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            product=request.data.get("product")

            User = Review.objects.filter(user=request.user.id)
            product=User.filter(product=product).first()
            if product and User:
                serializer = ReviewSerializer(product, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    x = Review.objects.filter(user=request.user.id).last()
                    a={"ProductReview":x.id}
                    z=Serializer_UserNotification(data=a,partial=True)
                    if z.is_valid():
                        z.save()
                    return Response({"status": "update", "data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = ReviewSerializer(data=request.data,partial=True)
                if serializer.is_valid():
                    serializer.save(user=request.user)
                    x = Review.objects.filter(user=request.user.id).last()
                    a={"ProductReview":x.id}
                    z=Serializer_UserNotification(data=a,partial=True)
                    if z.is_valid():
                        z.save()
                    return Response({"status": "success","data": serializer.data},status=status.HTTP_200_OK)
                else:
                    return Response({ "error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)             
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateReview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            

            User = Review.objects.get(id=id)
            serializer = ReviewSerializer(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.username)
                return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class DeleteReview(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            User = get_object_or_404(Review, id=id)
            User.delete()
            return Response({"status": "success", "data": "Deleted"})
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class GetComment(APIView):

    def get(self, request, id=None):
        try:
            User = BlogComment.objects.filter(Blog=id)
            CommentCount=BlogComment.objects.filter(Blog=id).filter(user=request.user).count()
            serialize = CommentSerializer(User, many=True)
            response={"Comments":serialize.data,"CommentCounts":CommentCount}
            return Response(response)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
     
class AddComment(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        try:
            Blog=request.data.get("Blog")
            User = BlogComment.objects.filter(user=request.user)
            product=User.filter(Blog=Blog).first()
            if product and User:
                serializer = CommentSerializer(product, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    count=BlogComment.objects.filter(Blog=Blog).count()
                    return Response({"status": "update", "data": serializer.data,"CommentCounts":count}, status.HTTP_200_OK)
                else:
                    return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = CommentSerializer(data=request.data,partial=True)
                if serializer.is_valid():
                    serializer.save(user=request.user)
                    count=BlogComment.objects.filter(Blog=Blog).count()
                    return Response({"status": "success","data": serializer.data,"CommentCounts":count},status=status.HTTP_200_OK)
                else:
                    return Response({ "error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)             
                   
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateComment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None):
        try:
            User = BlogComment.objects.get(id=id)
            serializer = CommentSerializer(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.username)
                return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class DeleteComment(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            User = get_object_or_404(BlogComment, id=id)
            User.delete()
            return Response({"status": "success", "data": "Deleted"})
        except Exception as e:
            return Response({'error' : str(e)},status=500)

import os
FACEBOOK_DEBUG_TOKEN_URL = "https://graph.facebook.com/debug_token"
FACEBOOK_ACCESS_TOKEN_URL = "https://graph.facebook.com/v7.0/oauth/access_token"
FACEBOOK_URL = "https://graph.facebook.com/"                                                                            
class FacebookSignInView(APIView):
    def post(self, request):
        # get users access token from code in the facebook login dialog redirect
        # https://graph.facebook.com/v7.0/oauth/access_token?client_id={your-facebook-apps-id}&redirect_uri=http://localhost:8000/login/&client_secret={app_secret}&code={code-generated-from-login-result}
        user_access_token_payload = {
            "client_id": os.environ.get("FACEBOOK_APP_ID"),
            "redirect_uri": "https://sweede.net/login/",
            "client_secret": os.environ.get("FACEBOOK_APP_SECRET"),
            "code": request.query_params.get("code"),
        }
        user_access_token_request = requests.get(
            FACEBOOK_ACCESS_TOKEN_URL, params=user_access_token_payload
        )
        user_access_token_response = json.loads(user_access_token_request.text)
        if "error" in user_access_token_response:
            user_access_token_error = {
                "message": "wrong facebook access token / this facebook access token is already expired."
            }
            return Response(user_access_token_error)

        user_access_token = user_access_token_response["access_token"]

        # get developers access token
        # https://graph.facebook.com/v7.0/oauth/access_token?client_id={your-app-id}&client_secret={your-app-secret}&grant_type=client_credentials
        developers_access_token_payload = {
            "client_id": os.environ.get("FACEBOOK_APP_ID"),
            "client_secret": os.environ.get("FACEBOOK_APP_SECRET"),
            "grant_type": "client_credentials",
        }
        developers_access_token_request = requests.get(
            FACEBOOK_ACCESS_TOKEN_URL, params=developers_access_token_payload
        )
        developers_access_token_response = json.loads(
            developers_access_token_request.text
        )

        if "error" in developers_access_token_response:
            developers_access_token_error = {
                "message": "Invalid request for access token."
            }
            return Response(developers_access_token_error)

        developers_access_token = developers_access_token_response["access_token"]
        # inspect the users access token --> validate to make sure its still valid
        # https://graph.facebook.com/debug_token?input_token={token-to-inspect}&access_token={app-token-or-admin-token}

        verify_user_access_token_payload = {
            "input_token": user_access_token,
            "access_token": developers_access_token,
        }

        verify_user_access_token_request = requests.get(
            FACEBOOK_DEBUG_TOKEN_URL, params=verify_user_access_token_payload
        )
        verify_user_access_token_response = json.loads(
            verify_user_access_token_request.text
        )

        if "error" in verify_user_access_token_response:
            verify_user_access_token_error = {
                "message": "Could not verifying user access token."
            }
            return Response(verify_user_access_token_error)

        user_id = verify_user_access_token_response["data"]["user_id"]

        # get users email
        # https://graph.facebook.com/{your-user-id}?fields=id,name,email&access_token={your-user-access-token}
        user_info_url = FACEBOOK_URL + user_id
        user_info_payload = {
            "fields": "id,name,email",
            "access_token": user_access_token,
        }

        user_info_request = requests.get(user_info_url, params=user_info_payload)
        user_info_response = json.loads(user_info_request.text)

        users_email = user_info_response["email"]

        # create user if not exist
        try:
            user = User.objects.get(email=user_info_response["email"])
        except User.DoesNotExist:
            user = User()
            user.username = user_info_response["email"]
            # provider random default password
            user.password = make_password(BaseUserManager().make_random_password())
            user.email = user_info_response["email"]
            user.save()

        token = RefreshToken.for_user(
            user
        )  # generate token without username & password
        response = {}
        response["username"] = user.username
        response["access_token"] = str(token.access_token)
        response["refresh_token"] = str(token)
        return Response(response)


class DeliveryAddress(APIView):
    def post(self, request,id=None):
        try:
            delivery=request.data.get('delivery')
            s=Stores.objects.filter(id=id).first()
            for i in s.Locations:
                a=i["Zip"]
                if delivery==a:
                    return Response("Matched")
            else:
                return Response("Not Matched")
        except Exception as e:
            return Response({'error' : str(e)},status=500)


class GetPromotionalBanners(APIView):
    def get(self, request, format=None):
        try:
            User =PromotionalBanners.objects.select_related().all()
            serialize = Serializer_PromotionalBanners(User, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)


class GetDeliveryCheck(APIView):
    def post(self, request, format=None):
        try:
            PinCode=request.data.get('PinCode')
            Store=request.data.get('Store')
            User =Stores.objects.filter(id=Store).filter(Locations__icontains=PinCode)
            if User:
                return Response("Success")
            else:
                return Response("Not Found")
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class CountProductAccordingToCategory(APIView):
    def get(self, request, id=None):
        try:
            s=[]
            product =Product.objects.filter(Store_id=id)
            for i in product:
                a=SubCategory.objects.filter(id=i.Sub_Category_id_id)
                for j in a:
                    b=Category.objects.filter(id=j.category_id_id)
                    for k in b:
                        response={"Category":k.name,"Count":b.count()}
                        s.append(response)
            return Response(s)
        except Exception as e:
            return Response({'error' : str(e)},status=500)


class GetNewsById(APIView):
    def get(self, request, id=None):
        try:
            User = News.objects.filter(id=id)
            serialize = Serializer_News(User, many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateUserProfile(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            a=request.user.id
            user = User.objects.get(id=a)
            serializer = UserProfileSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.username)
                return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
class GetUserProfile(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            a=request.user.id
            user = User.objects.get(id=a)
            serializer = UserProfileSerializer(user)
            return Response( serializer.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class YouMayAlsoLike(APIView):
    def post(self,request):
        try:
            category=request.data.get('category')
            store_id=request.data.get('store_id')
            user= Product.objects.filter(Sub_Category_id__category_id=int(category)).filter(Store_id=int(store_id)).filter(Status="Active")
            if user:
                serialize=Serializer_Product(user,many=True)
                return Response(serialize.data)
            else:
                return Response("There is no Product",status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
          
class GetDeliveryStoresHomepage(APIView):
    def post(self, request):
        try:
            Country=request.data.get("Country")
            State=request.data.get("State")
            City=request.data.get("City")
            if Country:
                Delivery = Stores.objects.filter(Order_Type="Delivery").filter(Status="Active").filter(Country=Country)
                DeliveryandPickup=Stores.objects.filter(Order_Type="Delivery and Pickup").filter(Status="Active").filter(Country=Country)
                User=Delivery or DeliveryandPickup
                serialize=Serializer_Store(User,many=True)
                return Response( serialize.data, status.HTTP_200_OK)
            elif State:
                Delivery = Stores.objects.filter(Order_Type="Delivery").filter(State=State)
                DeliveryandPickup=Stores.objects.filter(Order_Type="Delivery and Pickup").filter(State=State)
                User=Delivery or DeliveryandPickup              
                serialize=Serializer_Store(User,many=True)
                return Response( serialize.data, status.HTTP_200_OK)
            elif City:
                Delivery = Stores.objects.filter(Order_Type="Delivery").filter(City=City)
                DeliveryandPickup=Stores.objects.filter(Order_Type="Delivery and Pickup").filter(City=City)
                User=Delivery or DeliveryandPickup
                serialize=Serializer_Store(User,many=True)
                return Response( serialize.data, status.HTTP_200_OK)
            elif Country and State and City:
                Delivery = Stores.objects.filter(Order_Type="Delivery").filter(Country=Country).filter(State=State).filter(City=City)
                DeliveryandPickup=Stores.objects.filter(Order_Type="Delivery and Pickup").filter(Country=Country).filter(State=State).filter(City=City)
                User=Delivery or DeliveryandPickup
                serialize=Serializer_Store(User,many=True)
                return Response( serialize.data, status.HTTP_200_OK)
            else:
                return Response("No Delivery in your Area",status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

       
class GetPendingOrder(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = Order.objects.filter(created_by=request.user)
            pending=User.filter(Order_Status="Pending")
            serialize = Serializer_Order(pending, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
class GetDeliveredOrder(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = Order.objects.filter(created_by=request.user)
            Delivered=User.filter(Order_Status="Delivered")
            serialize = Serializer_Order(Delivered, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
class GetCancelOrder(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = Order.objects.filter(created_by=request.user)
            Cancel=User.filter(Order_Status="Cancel")
            serialize = Serializer_Order(Cancel, many=True)
            
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
class GetProcessingOrder(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            User = Order.objects.filter(created_by=request.user)
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
  
  
class AllUser(APIView):
    def get(self,request):
        try:
            a=[]
            user=User.objects.all()
            for i in user:
                response=i.id
                a.append(response)
            return Response(a)
                  
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
# class PromoCodeCheck(APIView):
#     permission_classes = [IsAuthenticated]
#     def post(self,request):
#         try:
#             Category=request.data.get("Category")
#             product=request.data.get("product")
#             Code=request.data.get("Code")
#             TotalPrice=request.data.get("TotalPrice")
#             CartQuantity=request.data.get("CartQuantity")
#             date=request.data.get("date")
#             coupoun=Coupoun.objects.filter(DiscountCode=Code).first() 
#             if coupoun.product :
#                     a=coupoun.product.all()
#                     for i in product:
#                         for j in a:
#                             if i==j.id:
#                                 if coupoun :
#                                     if coupoun.NoMinimumRequirements==True:
#                                         if coupoun.LimitToOneUsePerCustomer==True:
#                                                 for l in coupoun.AllCustomer:
#                                                     if l==request.user.id:
#                                                         if coupoun.PercentageAmount :
#                                                             percentageAmount=TotalPrice*coupoun.PercentageAmount/100
#                                                         elif coupoun.ValueAmount:
#                                                             valueAmount=TotalPrice-coupoun.ValueAmount
#                                                         coupoun.AllCustomer.remove(request.user.id)
#                                                     else:
#                                                         return Response("You Have Already Used This Coupoun")
#                                         elif coupoun.LimitNumberOfTime!=None:
#                                                 if coupoun.PercentageAmount :
#                                                     percentageAmount=TotalPrice*coupoun.PercentageAmount/100
#                                                 elif coupoun.ValueAmount:
#                                                     valueAmount=TotalPrice-coupoun.ValueAmount
#                                                 coupoun.LimitNumberOfTime-1
                                                    
#                                     elif coupoun.MinimumPurchaseAmount<=TotalPrice:
#                                         if coupoun.LimitToOneUsePerCustomer==True:
#                                                 for l in coupoun.AllCustomer:
#                                                     if l==request.user.id:
#                                                         if coupoun.PercentageAmount :
#                                                             percentageAmount=TotalPrice*coupoun.PercentageAmount/100
#                                                         elif coupoun.ValueAmount:
#                                                             valueAmount=TotalPrice-coupoun.ValueAmount
#                                                         coupoun.AllCustomer.remove(request.user.id)
#                                                     else:
#                                                         return Response("You Have Already Used This Coupoun")
#                                         elif coupoun.LimitNumberOfTime!=None:
#                                                 if coupoun.PercentageAmount :
#                                                     percentageAmount=TotalPrice*coupoun.PercentageAmount/100
#                                                 elif coupoun.ValueAmount:
#                                                     valueAmount=TotalPrice-coupoun.ValueAmount
#                                                 coupoun.LimitNumberOfTime-1
                                                           
#                                     elif coupoun.MinimumQuantityofItem<=CartQuantity:
#                                         if coupoun.LimitToOneUsePerCustomer==True:
#                                                 for l in coupoun.AllCustomer:
#                                                     if l==request.user.id:
#                                                         if coupoun.PercentageAmount :
#                                                             percentageAmount=TotalPrice*coupoun.PercentageAmount/100
#                                                         elif coupoun.ValueAmount:
#                                                             valueAmount=TotalPrice-coupoun.ValueAmount
#                                                         coupoun.AllCustomer.remove(request.user.id)
#                                                     else:
#                                                         return Response("You Have Already Used This Coupoun")
#                                         elif coupoun.LimitNumberOfTime!=None:
#                                                 if coupoun.PercentageAmount :
#                                                     percentageAmount=TotalPrice*coupoun.PercentageAmount/100
#                                                 elif coupoun.ValueAmount:
#                                                     valueAmount=TotalPrice-coupoun.ValueAmount
#                                                 coupoun.LimitNumberOfTime-1    
#             elif coupoun.category :
#                     a=coupoun.category.all()
#                     for i in Category:
#                         for j in a:
#                             if i==j.id:
#                                 if coupoun.NoMinimumRequirements==True:
#                                         if coupoun.AllCustomer!=[]:
#                                             if coupoun.LimitToOneUsePerCustomer==True:
#                                                 for l in coupoun.AllCustomer:
#                                                     if l==request.user.id:
#                                                         if coupoun.PercentageAmount :
#                                                             percentageAmount=TotalPrice*coupoun.PercentageAmount/100
#                                                         elif coupoun.ValueAmount:
#                                                             valueAmount=TotalPrice-coupoun.ValueAmount
#                                                         coupoun.AllCustomer.remove(request.user.id)
#                                                     else:
#                                                         return Response("You Have Already Used This Coupoun")
#                                             elif coupoun.LimitNumberOfTime!=None:
#                                                 if coupoun.PercentageAmount :
#                                                     percentageAmount=TotalPrice*coupoun.PercentageAmount/100
#                                                 elif coupoun.ValueAmount:
#                                                     valueAmount=TotalPrice-coupoun.ValueAmount
#                                                 coupoun.LimitNumberOfTime-1
                                                    
#                                 elif coupoun.MinimumPurchaseAmount<=TotalPrice:
#                                     if coupoun.AllCustomer!=[]:
#                                         if coupoun.LimitToOneUsePerCustomer==True:
#                                             for l in coupoun.AllCustomer:
#                                                 if l==request.user.id:
#                                                     if coupoun.PercentageAmount :
#                                                         percentageAmount=TotalPrice*coupoun.PercentageAmount/100
#                                                     elif coupoun.ValueAmount:
#                                                         valueAmount=TotalPrice-coupoun.ValueAmount
#                                                     coupoun.AllCustomer.remove(request.user.id)
#                                                 else:
#                                                     return Response("You Have Already Used This Coupoun")
#                                         elif coupoun.LimitNumberOfTime!=None:
#                                             if coupoun.PercentageAmount :
#                                                 percentageAmount=TotalPrice*coupoun.PercentageAmount/100
#                                             elif coupoun.ValueAmount:
#                                                 valueAmount=TotalPrice-coupoun.ValueAmount
#                                             coupoun.LimitNumberOfTime-1
                                                        
#                                     elif coupoun.SpecificCustomer != None:
#                                         for k in coupoun.SpecificCustomer:
#                                             if k['id']==request.user.id:
#                                                 if coupoun.PercentageAmount :
#                                                     percentageAmount=TotalPrice*coupoun.PercentageAmount/100
#                                                 elif coupoun.ValueAmount:
#                                                     valueAmount=TotalPrice-coupoun.ValueAmount 
                                                    
#                                 elif coupoun.MinimumQuantityofItem<=CartQuantity:
#                                         if coupoun.AllCustomer==True:
#                                             if coupoun.PercentageAmount :
#                                                 percentageAmount=TotalPrice*coupoun.PercentageAmount/100
#                                             elif coupoun.ValueAmount:
#                                                 valueAmount=TotalPrice-coupoun.ValueAmount
#                                         elif coupoun.SpecificCustomer != None:
#                                             for k in coupoun.SpecificCustomer:
#                                                 if k['id']==request.user.id:
#                                                     if coupoun.PercentageAmount :
#                                                         percentageAmount=TotalPrice*coupoun.PercentageAmount/100
#                                                     elif coupoun.ValueAmount:
#                                                         valueAmount=TotalPrice-coupoun.ValueAmount       

                                        
#             else:
#                 return Response("Not Applicable",status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                  
#         except Exception as e:
#                 return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
class GetDispensary_Product(APIView):
    def get(self,request,format=None):
        try:
            user = Stores.objects.filter(Store_Type="dispensary")
            active=user.filter(Status="Active")
            if active:
                for i in active:
                    product=Product.objects.filter(Store_id=i.id)
                    serialize=Serializer_Product(product,many=True)
                return Response(serialize.data,status=status.HTTP_200_OK)
            else:
                return Response("No Available Dispensaries",status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class getReviewbyId(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,id=None,productId=None):
        try:
            user = Review.objects.filter(user=id)
            product=user.filter(product=productId)
            serialize=ReviewSerializer(product,many=True)
            return Response(serialize.data,status=status.HTTP_200_OK)
           
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
        
class AverageReviewAndRating(APIView):
    def get(self,request,id=None):
        try:
            user = Review.objects.filter(product=id)
            totalUser=user.count()
            if user :
                onestarCount=user.filter(rating=1).count()
                twostarCount=user.filter(rating=2).count()
                threestarCount=user.filter(rating=3).count()
                fourstarCount=user.filter(rating=4).count()
                fivestarCount=user.filter(rating=5).count()
                sum=(onestarCount+twostarCount+threestarCount+fourstarCount+fivestarCount)            
                OneStar=(1*onestarCount)*100/sum
                TwoStar=(2*twostarCount)*80/sum
                ThreeStar=(3*threestarCount)*60/sum
                FourStar=(4*fourstarCount)*40/sum
                FiveStar=(5*fivestarCount)*20/sum
                
                AverageReview=(1*OneStar+2*TwoStar+3*ThreeStar+4*FourStar+5*FiveStar)/(OneStar+TwoStar+ThreeStar+FourStar+FiveStar)
                product=Product.objects.filter(id=id)
                serialize=Serializer_Product(product,data=request.data,partial=True)
                if serialize.is_valid():
                    serialize.save(rating=AverageReview,TotalRating=totalUser)
                    return Response({"OneStar":round(OneStar,0),"TwoStar":round(TwoStar,0),"ThreeStar":round(ThreeStar,0),"FourStar":round(FourStar,0),"FiveStar":round(FiveStar,0),"AverageReview":round(AverageReview,2),"TotalReview":totalUser})
            else:
                return Response({"OneStar":0,"TwoStar":0,"ThreeStar":0,"FourStar":0,"FiveStar":0,"AverageReview":0,"TotalReview":0})
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
class GetBlankImage(APIView): #LikeSerializer BlogLike

    def get(self, request, format=None):
        try:

            User = BlankImage.objects.select_related().all()
            serialize = Serializer_BlankImage(User, many=True)
            return Response(serialize.data)

        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddBlankImage(APIView):

    def post(self, request):
        try:

            serializer = Serializer_BlankImage(data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UpdateBlankImage(APIView):

    def post(self, request, id=None):
        try:

            User = BlankImage.objects.get(id=id)
            serializer = Serializer_BlankImage(User, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.username)
                return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteBlankImage(APIView):

    def delete(self, request, id=None):
        try:

            User = get_object_or_404(BlankImage, id=id)
            User.delete()
            return Response({"status": "success", "data": "Deleted"})

        except Exception as e:
            return Response({'error' : str(e)},status=500)

class GetBlogLike(APIView): 

    def get(self, request, id=None):
        try:

            User = BlogLike.objects.filter(Blog=id)
            LikeCount=BlogLike.objects.filter(Blog=id).filter(like=True).count()
            serialize = LikeSerializer(User, many=True)
            response={serialize.data,LikeCount}
            return Response(response,LikeCount)

        except Exception as e:
            return Response({'error' : str(e)},status=500)
    
class AddBlogLike(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            User = BlogLike.objects.filter(user=request.user).first()
            if User:
                serializer = LikeSerializer(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
            else:
                serializer = LikeSerializer(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(user=request.user)
                    return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class AddBlankImage(APIView):

    def post(self, request):
        try:

            serializer = StoreRatingAndReviewSerializer(data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
        
class AddBlogView(APIView):
    def post(self, request):
        try: 
            bolg=request.data.get("bolg")
            count=BlogView.objects.filter(blog=bolg).count()
            view=BlogView.objects.filter(blog=bolg).first()
            if view.ViewCount==0:
                serialize=Serializer_BlogView(data=request.data,partial=True)
                if serialize.is_valid():
                    serialize.save(ViewCount=view.ViewCount+1)
                    response={"data":serialize.data,"ViewCount":count}
                    
                    return Response(response)
            else:
                serialize=Serializer_BlogView(view, data=request.data,partial=True)
                if serialize.is_valid():
                    serialize.save(ViewCount=view.ViewCount+1)
                    response={"data":serialize.data,"ViewCount":count}              
                
                return Response(response)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class FilterDispensaries(APIView):
    def post(self,request):
        try:
            store=request.data.get("store")
            Country=request.data.get("Country")
            State=request.data.get("State")
            City=request.data.get("City")
            if City or State or Country:
                check=Stores.objects.filter(Store_Name__icontains=store).filter(Store_Type="dispensary").filter(City=City)
                serialize=Serializer_Store(check,many=True)
                if len(check)==0:
                    check1=Stores.objects.filter(Store_Name__icontains=store).filter(Store_Type="dispensary").filter(State=State)
                    serialize1=Serializer_Store(check1,many=True)

                    if len(check1)==0:
                        check2=Stores.objects.filter(Store_Name__icontains=store).filter(Store_Type="dispensary").filter(Country=Country)
                        serialize2=Serializer_Store(check2,many=True)
                        return Response(serialize2.data)
                    return Response(serialize1.data)
                return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
 

class HighPriceToLowPrice(APIView):
    def get(self,request,id=None):
        try:
            a=[]
            z=[]
            q=[]
            product=Product.objects.filter(Store_id=id)
            serialize=Serializer_Product(product,many=True).data
            for i in serialize:
                for j in  i["Prices"]:
                    for k in j["Price"]:
                        response={"Price":k,"Product":i["id"]}
                        a.append(response)
                        
            lines = sorted(a, key=lambda k: k['Price'].get('SalePrice', 0), reverse=True)
            for m in lines: 
                product=Product.objects.filter(id=m["Product"])
                serialize=Serializer_Product(product,many=True).data
                z.append(serialize)
            for x in z:
                if x not in q:
                    q.append(x)
            return Response(q)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class AddRecentViews(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            serialize=Serializer_RecentView(data=request.data,partial=True)
            if serialize.is_valid():
                serialize.save()
                return Response({"status": "success","data": serialize.data}, status.HTTP_200_OK)
            else:
                return Response({ "error":serialize.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class GetRecentViews(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            view=RecentView.objects.filter(user=request.user.id)
            serialize=Serializer_RecentView(view,many=True)
            return Response(serialize.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         

class AddSubscribe(APIView):
    def post(self,request):
        try:
            serialize=Serializer_Subscribe(data=request.data,partial=True)
            if serialize.is_valid():
                serialize.save()
                return Response({"status": "success","data": serialize.data}, status.HTTP_200_OK)
            else:
                return Response({ "error":serialize.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AddUserProfileOrderDetails(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:
            User = UserProfileOrderDetails.objects.filter(user=request.user).first()
            if User:
                serializer = Serializer_UserProfileOrderDetails(User, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
            else:
                serializer = Serializer_UserProfileOrderDetails(data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(user=request.user)
                    return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class GetUserProfileOrderDetails(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            view=UserProfileOrderDetails.objects.filter(user=request.user.id)
            serialize=Serializer_UserProfileOrderDetails(view,many=True)
            return Response(serialize.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class BuyXGetYDiscount(APIView):
    def get(self,request):
        try:
            z=[]
            discount=Coupoun.objects.filter(DiscountType='Buy X get Y')
            for i in discount:
                a=i.CustomerBuys
                if a:
                    for j in a:
                        for k in j["Product"]:
                            l=Product.objects.filter(id=k)
                            serialize=Serializer_Product(l,many=True).data
                            for m in serialize:
                                z.append(m)
            return Response(z, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
from operator import itemgetter
class PopularStrain(APIView):
    def get(self, request):
        try:
            x=[]
            User = Order.objects.all()
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

       
class ProductDiscountCoupoun(APIView):
    def get(self,request):
        try:
            z=[]
            discount=Coupoun.objects.filter(DiscountType='Amount off Products')
            for i in discount:
                a=i.CustomerBuys
                if a:
                    for j in a:
                        for k in j["Product"]:
                            l=Product.objects.filter(id=k)
                            serialize=Serializer_Product(l,many=True).data
                            for m in serialize:
                                z.append(m)
            return Response(z, status.HTTP_200_OK)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class PriceFilter(APIView):
    def post(self,request):
        try:
            a=[]
            z=[]
            p=[]
            Store=request.data.get("Store")
            MinPrice=request.data.get("MinPrice")
            MaxPrice=request.data.get("MaxPrice")
            product=Product.objects.filter(Store_id=Store)
            serialize=Serializer_Product(product,many=True).data
            for i in serialize:
                for j in i["Prices"]:
                    for k in j["Price"]:
                        if MinPrice <= k["SalePrice"] <= MaxPrice:
                            response={"Product":i["id"],"Price":k["SalePrice"]}
                            a.append(response)
            for l in a:
                product=Product.objects.filter(id=l["Product"])
                serialize=Serializer_Product(product,many=True).data
                for m in serialize:
                    z.append(m)
            for t in z:
                    if t not in p:
                        p.append(t)
            return Response(p)
            
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
class GetSiteMap(APIView):
    def get(self, request):
        try:
            User = SiteMap.objects.all()
            serialize = Serializer_SiteMap(User, many=True)
            return Response(serialize.data,status=200)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

class AddSiteMap(APIView):
    def post(self, request):
        try:
            serializer = Serializer_SiteMap(data=request.data, partial=True)
            if serializer.is_valid(): 
                serializer.save()
                return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateSiteMap(APIView):
    def post(self, request, id=None):
        try:
            j=request.data.get("j")
            if j!=None:
                User = SiteMap.objects.filter(id=id).first()
                if j not in User.Xml:
                            User.Xml.append(j)
                asd={"Xml":User.Xml}
                serializer = Serializer_SiteMap(User,data=asd, partial=True)    
                if serializer.is_valid():
                    serializer.save(modified_by=request.user.username)
                    return Response({"status": "success", "data": serializer.data}, status.HTTP_200_OK)
                else:
                    return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("")
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteSiteMap(APIView):
    def delete(self, request, id=None):
        try:
            User = get_object_or_404(SiteMap, id=id)
            User.delete()
            return Response({"status": "success", "data": "Deleted"})
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
        
class getSitemapbyId(APIView):
    def get(self,request,id=None):
        try:
            site=SiteMap.objects.filter(id=id)
            serialize=Serializer_SiteMap(site,many=True)
            return Response(serialize.data,status=200)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
class GetProductByStoreAndBrand(APIView):
    def get(self,request,store=None,brand=None):
        try:
            product=Product.objects.filter(Store_id=store).filter(Brand_id=brand)
            serialize=Serializer_Product(product,many=True)
            return Response(serialize.data,status=200)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
class GetBrandByStore(APIView):
    def get(self,request,id=None):
        try:
            z=[]
            x=[]
            brand=Product.objects.filter(Store_id=id)
            for i in brand:
                a=brand.filter(Brand_id=i.Brand_id)
                if a:
                    for j in a:
                        if j.Brand_id == None:
                            x.append({"None":None})
                        else:
                            response={"name":j.Brand_id.name,"id":j.Brand_id_id,"Store_id":j.Store_id_id}
                            z.append(response)
                    return Response(z,status=200)
                else:
                    return Response("No Brand in this Store")
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
        
class ProductFilterByWeightandStore(APIView):
    def post(self,request):
        try:
            a=[]
            z=[]
            store=request.data.get("store")
            weight=request.data.get("weight")
            product=Product.objects.filter(Store_id=store)
            serialize=Serializer_Product(product,many=True).data
            for i in serialize:
                for j in i["Prices"]:
                    for k in j["Price"]:
                        if k["Weight"]==weight:
                            response={"Product":i["id"],"Price":k["Weight"]}
                            a.append(response)
                        else:
                            continue
            for l in a:
                product=Product.objects.filter(id=l["Product"])
                serialize=Serializer_Product(product,many=True).data
                for m in serialize:
                    z.append(m)
            return Response(z,status=200)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
class ProductFilterByUnitandStore(APIView):
    def post(self,request):
        try:
            a=[]
            z=[]
            Store=request.data.get("Store")
            MinUnit=request.data.get("MinUnit")
            MaxUnit=request.data.get("MaxUnit")
            product=Product.objects.filter(Store_id=Store)
            serialize=Serializer_Product(product,many=True).data
            for i in serialize:
                for j in i["Prices"]:
                    for k in j["Price"]:
                        if k["Unit"]=='' or k["Unit"]==None:
                            continue
                        else:
                            if (MinUnit) <= int(k["Unit"]) <= (MaxUnit):
                                response={"Product":i["id"],"Unit":k["Unit"]}
                                a.append(response)
                            else:
                                continue
            for l in a:
                product=Product.objects.filter(id=l["Product"])
                serialize=Serializer_Product(product,many=True).data
                for m in serialize:
                    z.append(m)
            return Response(z)
            
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BlogSearchApi(APIView):
    def post(self, request):
        try:
            search=request.data.get('search')
            blog=News.objects.filter(Title__icontains=search)
            serializer = Serializer_News(blog,many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class StrainFilterProduct(APIView):
    def post(self,request):
        try:
            a=[]
            z=[]
            store=request.data.get("store")
            strain=request.data.get("strain")
            for i in strain:
                product=Product.objects.filter(strain=i).filter(Store_id=store)
                if product:
                    serialize=Serializer_Product(product,many=True).data
                    a.append(serialize)
            for j in a:
                for l in j:
                    z.append(l)
            return Response(z)  
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DeleteStoreReview(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id=None):
        try:
            User = get_object_or_404(StoreReview, id=id)
            User.delete()
            return Response({"status": "success", "data": "Deleted"})
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
        
class UpdateStoreReview(APIView):
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

class AddTest(APIView):
    def post(self, request):
        try:
            serializer = Serializer_test(data=request.data, partial=True)
            if serializer.is_valid(): 
                serializer.save()
                return Response({"status": "success","data": serializer.data}, status.HTTP_200_OK)
            else:
                return Response({ "error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetTest(APIView):
    def get(self,request):
        try:
            a=Test.objects.all()
            serialize=Serializer_test(a,many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetNet_Weight(APIView):
    def get(self, request, format=None):
        try:
            User = Net_Weight.objects.select_related().all()
            serialize = Serializer_Net_Weight(User, many=True)
            return Response({"data":serialize.data},status=200)

        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
class WeightFilter(APIView):
    def post(self,request):
        try:
            a=[]
            z=[]
            q=[]
            store=request.data.get("store")
            weight=request.data.get("weight")
            product=Product.objects.filter(Store_id=store) 
            serialize=Serializer_Product(product,many=True).data
            for i in serialize:
                for j in i["Prices"]:
                    for k in j["Price"]:
                        for asd in weight:
                            if asd==k["Weight"]:
                                response={"Product":i["id"],"Unit":k["Unit"]}
                                a.append(response)
                                
            for l in a:
                product=Product.objects.filter(id=l["Product"])
                serialize=Serializer_Product(product,many=True).data
                for m in serialize:
                    z.append(m)
            for o in z:
                if o not in q:
                    q.append(o)
            return Response(q)
        except Exception as e:
            return Response({'error' : str(e)},status=500)

                
class AddHelpfull(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:

            userid=request.data.get("userid")
            review=request.data.get("review")
            a=StoreReview.objects.filter(id=review).first()
            
            if userid in a.helpfull:
                a.helpfull.remove(userid)
            else:
                a.helpfull.append(userid)
            l=len(a.helpfull)
            response={"helpfull":a.helpfull,"count":l}
            serialize=StoreRatingAndReviewSerializer(a,data=response,partial=True)
            if serialize.is_valid():
                serialize.save()
                storeReview={"storeReview":a.id,"user":request.user}
                s=Serializer_UserNotification(data=storeReview,partial=True)
                if s.is_valid():
                    s.save()
            return Response(serialize.data,status=201)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
        
class GetStoreReview(APIView):
    def get(self,request,id=None):
        try:
            like=StoreReview.objects.filter(Store=id)
            serialize=StoreRatingAndReviewSerializer(like,many=True).data
            return Response(serialize)
        except Exception as e:
            return Response({'error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddProductHelpfull(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        try:

            userid=request.data.get("userid")
            review=request.data.get("review")
            a=Review.objects.filter(id=review).first()
            
            if userid in a.helpfull:
                a.helpfull.remove(userid)
            else:
                a.helpfull.append(userid)
            l=len(a.helpfull)
            response={"helpfull":a.helpfull,"count":l}
            serialize=ReviewSerializer(a,data=response,partial=True)
            if serialize.is_valid():
                serialize.save()
            return Response(serialize.data,status=201)
        except Exception as e:
            return Response({'error' : str(e)},status=500)



class ProductListView(APIView):
    def post(self,request):
        try:
            search=request.data.get("search")
            store=request.data.get("store")
            product=Product.objects.filter(Product_Name__icontains=search).filter(Store_id=store)
            serialize=Serializer_Product(product,many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error':str(e)},status=500)
        
class UnitFilter(APIView):
    def post(self,request):
        try:
            a=[]
            z=[]
            store=request.data.get("store")
            unit=request.data.get("unit")
            product=Product.objects.filter(Store_id=store) 
            serialize=Serializer_Product(product,many=True).data
            for i in serialize:
                for j in i["Prices"]:
                    for k in j["Price"]:
                        # for asd in unit:
                            if unit==True:
                                if k["Unit"]!=None and k["Unit"]!="" and k["Unit"]!=0:
                                    response={"Product":i["id"],"Unit":k["Unit"]}
                                    a.append(response)
                                else:
                                    return Response("No Unit in Product")
                                
            for l in a:
                product=Product.objects.filter(id=l["Product"])
                serialize=Serializer_Product(product,many=True).data
                for m in serialize:
                    z.append(m)
            return Response(z)
        except Exception as e:
            return Response({'error' : str(e)},status=500)
        
class SearchProductbyBrand(APIView):
    def post(self,request):
        try:
            brand=request.data.get("brand")
            search=request.data.get("search")
            product=Product.objects.filter(Brand_id=brand).filter(Product_Name__icontains=search)
            serialize=Serializer_Product(product,many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# class ComboFilter(APIView):
#     def post(self,request):
#         try:
            
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PromoCodeCheck(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            PromoCode=request.data.get("PromoCode")
            coupoun=Coupoun.objects.filter(DiscountCode=PromoCode).first()
            if coupoun:
                if coupoun.EndDate == None:
                    # if datetime.now().date()<=coupoun.EndDate:
                        cart=AddtoCart.objects.filter(created_by=request.user)
                        
                        for i in cart:
                            if i.CoupounField==None:
                           
                                a=ProductWeight.objects.filter(product=i.Product_id_id).first()
                                for j in a.Price:
                                    for l in j["Coupoun"]:
                                        if l["DiscountCode"]==coupoun.DiscountCode:
                                            if coupoun.PercentageAmount:
                                                
                                                    CoupounField={"CoupounField":{"Product": i.Product_id_id, "Amount": None, "Reflect": False, "Percentage": coupoun.PercentageAmount, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "DiscountCode": coupoun.DiscountCode}}
                                                    addtocartupdate=Serializer_AddtoCart(i,data=CoupounField,partial=True)
                                                    if addtocartupdate.is_valid():
                                                        addtocartupdate.save()
                                            elif coupoun.ValueAmount:
                                                CoupounField={"CoupounField":{"Product": i.Product_id, "Amount": coupoun.ValueAmount, "Reflect": False, "Percentage":None, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "DiscountCode": coupoun.DiscountCode}}
                                                addtocartupdate=Serializer_AddtoCart(i,data=CoupounField,partial=True)
                                                if addtocartupdate.is_valid():
                                                    addtocartupdate.save()
                            else:
                                a=ProductWeight.objects.filter(product=i.Product_id_id).first()
                                CoupounField={"CoupounField":None}
                                addtocartupdate=Serializer_AddtoCart(i,data=CoupounField,partial=True)
                                if addtocartupdate.is_valid():
                                    addtocartupdate.save()
                                for j in a.Price:
                                    for l in j["Coupoun"]:
                                        if l["DiscountCode"]==coupoun.DiscountCode:
                                            if coupoun.PercentageAmount:
                                                if i.CoupounField == None:
                                                    CoupounField={"CoupounField":{"Product": i.Product_id_id, "Amount": None, "Reflect": False, "Percentage": coupoun.PercentageAmount, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "DiscountCode": coupoun.DiscountCode}}
                                                    addtocartupdate=Serializer_AddtoCart(i,data=CoupounField,partial=True)
                                                    if addtocartupdate.is_valid():
                                                        addtocartupdate.save()
                                                elif coupoun.ValueAmount:
                                                    CoupounField={"CoupounField":{"Product": i.Product_id, "Amount": coupoun.ValueAmount, "Reflect": False, "Percentage":None, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "DiscountCode": coupoun.DiscountCode}}
                                                    addtocartupdate=Serializer_AddtoCart(i,data=CoupounField,partial=True)
                                                    if addtocartupdate.is_valid():
                                                        addtocartupdate.save()
                                
                                                        
                        return Response("Success")
                elif coupoun.EndDate != None:
                    if datetime.now().date()<=coupoun.EndDate:
                        cart=AddtoCart.objects.filter(created_by=request.user)
                        for i in cart:
                            if i.CoupounField !=None:
                                a=ProductWeight.objects.filter(product=i.Product_id_id).first()
                                for j in a.Price:
                                    for l in j["Coupoun"]:
                                        if l["DiscountCode"]==coupoun.DiscountCode:
                                            if coupoun.PercentageAmount:
                                                result={"CoupounField":{"Product": i.Product_id, "Amount": None, "Reflect": False, "Percentage": coupoun.PercentageAmount, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "DiscountCode": coupoun.DiscountCode}}
                                                addtocartupdate=Serializer_AddtoCart(cart,data=result,partial=True)
                                                if addtocartupdate.is_valid():
                                                    addtocartupdate.save()
                                            elif coupoun.ValueAmount:
                                                result={"CoupounField":{"Product": i.Product_id, "Amount": coupoun.ValueAmount, "Reflect": False, "Percentage":None, "CouponMassage": "", "DiscountType": coupoun.DiscountType, "DiscountCode": coupoun.DiscountCode}}
                                                addtocartupdate=Serializer_AddtoCart(cart,data=result,partial=True)
                                                if addtocartupdate.is_valid():
                                                    addtocartupdate.save()
                        return Response("Success")
            
            else:
                return Response({"Error":"Invalid Code"},status=406)
                                    
                                
                              

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class GetallProductReviewbyStore(APIView):
    def post(self,request):
        try:
            store=request.data.get("store")
            product=Review.objects.filter(product__Store_id=store)
            serialize=ReviewSerializer(product,many=True)
            return Response(serialize.data)
        except Exception as e:
            return Response({'error':str(e)},status=500) 

class GetProductReviewbyUser(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            a=[]
            s=[]
            product=Review.objects.filter(user=request.user)
            serialize=ReviewSerializer(product,many=True).data
            for i in product:
                z=Product.objects.filter(id=i.product.id)
                serialize1=Serializer_Product(z,many=True).data
                for k in serialize:
                    for j in serialize1:
                        d={"review":k,"Product":j}
                        a.append(d) 
            for l in a:
                if l not in s:
                    s.append(l)
            return Response(s)
        except Exception as e:
            return Response({'error':str(e)},status=500) 
        
class GetStoreReviewbyUser(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:

            product=StoreReview.objects.filter(user=request.user)
            serialize=StoreRatingAndReviewSerializer(product,many=True).data

            return Response(serialize)
        except Exception as e:
            return Response({'error':str(e)},status=500) 
        
class OrderSearch(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            search=request.data.get("search")
            order=Order.objects.filter(OrderId__icontains=search).filter(created_by=request.user)
            order1=Order.objects.filter(Store__Store_Name__icontains=search).filter(created_by=request.user)
            order2=Order.objects.filter(Product__icontains=search).filter(created_by=request.user)
            order3=Order.objects.filter(Store__created_by__Name__icontains=search).filter(created_by=request.user)
            if order:
                serialize=Serializer_Order(order,many=True).data
                return Response(serialize)
            elif order1:
                serialize=Serializer_Order(order1,many=True).data
                return Response(serialize)
            elif order2:
                serialize=Serializer_Order(order2,many=True).data
                return Response(serialize)
            elif order3:
                serialize=Serializer_Order(order3,many=True).data
                return Response(serialize)
            else:
                return Response('No Matching Data Found')
            
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
from datetime import datetime

class GetUserNotification(APIView):
    def get(self,request):
        try:
            a=[]
            z=[]
            noti=UserNotification.objects.all()
            for i in noti:
                if i.Blog:
                    if i.lastday == None:
                        d=i.created_at + i.days
                        lastday={"lastday":d}
                        l=UserNotification.objects.filter(id=i.id).first()
                        serialize1=Serializer_UserNotification(l,data=lastday,partial=True)
                        if serialize1.is_valid():
                            serialize1.save()
                    if i.lastday==datetime.now():
                        blog=UserNotification.objects.filter(Blog=i.Blog_id).first()    
                        blog.delete()
                    blog=News.objects.filter(id=i.Blog_id)
                    serialize=Serializer_News(blog,many=True).data
                    a.append(serialize)
            for j in a:
                for k in j:
                    z.append(k)
            return Response({"Blog":z})  
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetUserNotificationByLogin(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            z=[]
            q=[]
            noti=UserNotification.objects.all()
            for i in noti:
                if i.lastday == None:
                    d=i.created_at + i.days
                    lastday={"lastday":d}
                    l=UserNotification.objects.filter(id=i.id).first()
                    serialize1=Serializer_UserNotification(l,data=lastday,partial=True)
                    if serialize1.is_valid():
                        serialize1.save()
                if i.lastday==datetime.now():
                    blog=UserNotification.objects.filter(ProductReview=i.ProductReview).first()    
                    blog.delete()
                a=Review.objects.filter(id=i.ProductReview_id).filter(user=request.user).first()
                if a:
                    if a.Reply != None:
                        seraialize=ReviewSerializer(a).data
                else:
                    seraialize=[]
                if a:
                    if len(a.helpfull) >3:
                        seraialize3=ReviewSerializer(a,many=True).data
                else:
                    seraialize3=[]
                    
                if i.lastday==datetime.now():
                    blog=UserNotification.objects.filter(storeReview=i.storeReview).filter(user=request.user).first()    
                    blog.delete()
                s=StoreReview.objects.filter(id=i.storeReview).first()
                if s:
                    if s.Reply != None:
                        seraialize4=StoreRatingAndReviewSerializer(s,many=True).data
                else:
                    seraialize4=[]
                if s:
                    
                    if len(s.helpfull) >3:
                        seraialize5=StoreRatingAndReviewSerializer(s,many=True).data
                else:
                    seraialize5=[]
                if i.lastday==datetime.now():
                        blog=UserNotification.objects.filter(Blog=i.Blog_id).first()    
                        blog.delete()
                blog=News.objects.filter(id=i.Blog_id)
                serialize2=Serializer_News(blog,many=True).data
                if i.lastday==datetime.now():
                        blog=UserNotification.objects.filter(OrderStausUpdate=i.OrderStausUpdate).first()    
                        blog.delete()
                order=Order.objects.filter(OrderId=i.OrderStausUpdate_id).filter(created_by=request.user)
                serialize6=Serializer_Order(order,many=True).data
                response={"ProductReview":seraialize,"blog":serialize2,"ProductHelpfull":seraialize3,"StoreReview":seraialize4,"StoreHelpFull":seraialize5,"Order":serialize6}
                z.append(response)
            for c in z:
                if c not in q:
                    q.append(c)
            return Response(q)     
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                



class ClearNotification(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        try:
            ClearAll=request.data.get("ClearAll",None)
            Clear=request.data.get("Clear",None)
            if Clear:
                for i in Clear:
                    a=UserNotification.objects.filter(id=i).filter(user=request.user)
                    a.delete()
                    return Response("Notification Clear")
            if ClearAll:
                a=UserNotification.objects.all()
                a.delete()
                return Response("All Notification Clear")
            else:
                return Response("No New Notification")
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)