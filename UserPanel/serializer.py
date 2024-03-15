
from rest_framework import serializers
from AdminPanel.models import *
from .models import *
from AdminPanel.serializer import *

class Serializer_FilterStore(serializers.ModelSerializer):
    name=serializers.CharField(source='Store_Name')
    class Meta:
      model=Stores
      fields=['name','id']

class Serializer_FilterBrand(serializers.ModelSerializer):

    class Meta:
      model=Brand
      fields=['name','id']

class RegisterUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('username', 'password','email')
   

  def create(self, validated_data):
    user = User.objects.create(
      username=validated_data['username'],
      email=validated_data['email'],
    )
    user.set_password(validated_data['password'])
    user.save()
    return user

class Serializer_AddtoCart(serializers.ModelSerializer):
  username=serializers.ReadOnlyField(source='created_by.username')
  StoreName=serializers.ReadOnlyField(source='Store_id.Store_Name')
  ProductName=serializers.ReadOnlyField(source='Product_id.Product_Name')
  Image=serializers.ImageField(source='Image_id.image')
  StoreDelivery= serializers.ReadOnlyField(source='Store_id.Delivery')
  StorePickup= serializers.ReadOnlyField(source='Store_id.StoreFront')
  StoreCurbsidePickup= serializers.ReadOnlyField(source='Store_id.CurbSide_Pickup')
  StoreAddress= serializers.ReadOnlyField(source='Store_id.Store_Address')
  StoreHours= serializers.ReadOnlyField(source='Store_id.Hours')
  StoreCurbSidePickupHours= serializers.ReadOnlyField(source='Store_id.CurbSidePickupHours')
  Brand_Name=serializers.ReadOnlyField(source='Brand_Id.name') 
  SubcategoryName=serializers.ReadOnlyField(source='Sub_Category_id.name') 
  class Meta:
    model=AddtoCart
    fields='__all__'
    extra_kwargs = {'created_by': {'default': serializers.CurrentUserDefault()}}       

class Serializer_Order(serializers.ModelSerializer):
  StoreName=serializers.ReadOnlyField(source='Store.Store_Name')
  SellerName=serializers.ReadOnlyField(source='Store.created_by.username')
  username=serializers.ReadOnlyField(source='created_by.username')
  email=serializers.ReadOnlyField(source='created_by.email')
  UserProfileImage=serializers.ReadOnlyField(source='created_by.image.url')
  class Meta:
    model=Order
    fields='__all__'
    extra_kwargs = {'created_by': {'default': serializers.CurrentUserDefault()}} 

from django.contrib.auth import authenticate   
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"},)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError('Invalid Email or Password !')

        attrs['Customer'] = user
        return attrs

class Serializer_Wishlist(serializers.ModelSerializer):
  username=serializers.ReadOnlyField(source='created_by.username')
  ProductName=serializers.ReadOnlyField(source='product.Product_Name')
  class Meta:
    model=Wishlist
    fields='__all__'
    extra_kwargs = {'created_by': {'default': serializers.CurrentUserDefault()}} 

class Serializer_SubCategoryName(serializers.ModelSerializer):
  category_name = serializers.CharField(source='category_id.name', read_only=True)
  class Meta:
    model=SubCategory
    fields='__all__'
    
class Serializer_CategoryName(serializers.ModelSerializer):
  subcategories=Serializer_SubCategory(many=True, read_only=True)
  class Meta:
    model=Category
    fields='__all__'

class CommentSerializer(serializers.ModelSerializer):
    username=serializers.ReadOnlyField(source='user.username')
    image=serializers.ReadOnlyField(source='user.image.url')
    class Meta:
        model = BlogComment 
        fields = '__all__'
        extra_kwargs = {'user': {'default': serializers.CurrentUserDefault()}}
        
class LikeSerializer(serializers.ModelSerializer):
    username=serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = BlogLike
        fields = '__all__'
        extra_kwargs = {'user': {'default': serializers.CurrentUserDefault()}}

class ReviewSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    username=serializers.ReadOnlyField(source='user.username')
    userImage=serializers.ReadOnlyField(source='user.image.url')
    Email=serializers.ReadOnlyField(source='user.email')
    ProductName=serializers.ReadOnlyField(source='product.Product_Name')
    ProductId=serializers.ReadOnlyField(source='product.id')
    StoreName=serializers.ReadOnlyField(source='product.Store_id.Store_Name')
    Reviewtype = serializers.ReadOnlyField(default='ProductReview')
    # ProductImages=serializers.JSONField()
    class Meta:
        model = Review
        fields = '__all__'
        extra_kwargs = {'user': {'default': serializers.CurrentUserDefault()}}

class UserProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ["email","id","username","Gender",'DateOfBirth','DeliveryAddress','MedicalCardNumber','MedicalCardExpire','MedicalCardState','EmailBoolean','NewsLetter','ReviewSuggestions','PushNotification','Recommendations','Savings','OrderupdatePushNotification','OrderupdateSMSNotifications','image','MobilePhone','PhotoId','googlelink','RemovedNotification']

class Serializer_BlankImage(serializers.ModelSerializer):
  class Meta:
    model=BlankImage
    fields='__all__'

class StoreReviewSerializer(serializers.ModelSerializer):
    username=serializers.ReadOnlyField(source='user.username')
    StoreName=serializers.ReadOnlyField(source='Store.Store_Name')
    Email=serializers.ReadOnlyField(source='user.email')
    Reviewtype = serializers.ReadOnlyField(default='StoreReview')
    # StoreImage=serializers.ReadOnlyField(source='Store.Store_Image')
    # userImage=serializers.ReadOnlyField(source='user.image')
    class Meta:
        model = StoreReview
        fields = '__all__'
        extra_kwargs = {'user': {'default': serializers.CurrentUserDefault()}}
        
class Serializer_BlogView(serializers.ModelSerializer):
  class Meta:
    model=BlogView
    fields='__all__'
    
class Serializer_RecentView(serializers.ModelSerializer):
  username=serializers.ReadOnlyField(source='user.username')
  ProductName=serializers.ReadOnlyField(source='product.Product_Name')
  class Meta:
    model=RecentView
    fields='__all__'
    extra_kwargs = {'user': {'default': serializers.CurrentUserDefault()}}

class Serializer_UserProfileOrderDetails(serializers.ModelSerializer):
  username=serializers.ReadOnlyField(source='user.username')
  class Meta:
    model=UserProfileOrderDetails
    fields='__all__'
 
class Serializer_SiteMap(serializers.ModelSerializer):
  class Meta:
    model=SiteMap
    fields='__all__'

class Serializer_test(serializers.ModelSerializer):
  class Meta:
    model=Test
    fields='__all__'
    
class Serializer_UserNotification(serializers.ModelSerializer):
  BlogTittle=serializers.ReadOnlyField(source='Blog.Title')
  class Meta:
    model=UserNotification
    fields='__all__'
    # extra_kwargs = {'user': {'default': serializers.CurrentUserDefault()}}