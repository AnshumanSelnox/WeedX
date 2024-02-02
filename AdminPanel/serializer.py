import json
from rest_framework import serializers
from .models import *





class Serializer_Category(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        

class Serializer_SubCategory(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category_id.name')
    class Meta:
        model = SubCategory
        fields = '__all__'
        

class Serializer_Country(serializers.ModelSerializer):
    class Meta:
        model=Countries
        fields='__all__'
        
class Serializer_States(serializers.ModelSerializer):
    country_name = serializers.ReadOnlyField(source='Country_id.CountryName')
    class Meta:
        model=States
        fields='__all__'
        
class Serializer_Cities(serializers.ModelSerializer):
    state_name = serializers.ReadOnlyField(source='States_id.StateName')
    class Meta:
        model=Cities
        fields='__all__'
        
        
    

class Serializer_Brand(serializers.ModelSerializer):
    username=serializers.ReadOnlyField(source='created_by.username')
    class Meta:
        model=Brand
        fields='__all__'
        extra_kwargs = {'created_by': {'default': serializers.CurrentUserDefault()}} 


        
class Serializer_Salestax(serializers.ModelSerializer):
    class Meta:
        model=Salestaxes
        fields='__all__'
        
class Serializer_Esteemedtax(serializers.ModelSerializer):
    class Meta:
        model=Estemeedtaxes
        fields='__all__'        
        

     
        
class VerifyAccountSerializer(serializers.Serializer):
    email=serializers.EmailField()
    OTP=serializers.CharField()

class PasswordReseetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ( 'password', 'email')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email','status','Roles','is_superuser','MobilePhone')
          

class RegisterSerializer(serializers.ModelSerializer):
   

    class Meta:
        model=User
        fields=('username','email','password','user_type','Roles','is_superuser','MobilePhone')

    def create(self,validated_data):
        user=User.objects.create_superuser(validated_data['username'],validated_data['email'],validated_data['password'],user_type=validated_data['user_type'],is_superuser=validated_data["is_superuser"],MobilePhone=validated_data['MobilePhone'])
        return user
                     



class Serializer_Store(serializers.ModelSerializer):
    
    class Meta:
      model=Stores
      fields='__all__'
      extra_kwargs = {'created_by': {'default': serializers.CurrentUserDefault()}}             
    
    
       
class Serializer_NewsCategory(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = '__all__'
        extra_kwargs = {'created_by': {'default': serializers.CurrentUserDefault()}}     
        

class Serializer_NewsSubCategory(serializers.ModelSerializer):

    category_name = serializers.ReadOnlyField(source='category_id.name')
    class Meta:
        model = NewsSubCategory
        fields = '__all__'
        extra_kwargs = {'created_by': {'default': serializers.CurrentUserDefault()}}     
        
    
class Serializer_News(serializers.ModelSerializer):
    username=serializers.ReadOnlyField(source='created_by.username')
    category_name = serializers.ReadOnlyField(source='Category.name')
    subcategoy_name=serializers.ReadOnlyField(source='SubCategory.name')
    class Meta:
        model=News
        fields='__all__' 
        extra_kwargs = {'created_by': {'default': serializers.CurrentUserDefault()}} 
    
class Serializer_Net_Weight(serializers.ModelSerializer):
    class Meta:
        model=Net_Weight
        fields='__all__'
        
        
        
        
class ChangePasswordSerializer(serializers.Serializer):
    model = User
    email=serializers.EmailField()


from VendorPanel.auth import EmailBackend
from django.contrib.auth.hashers import check_password
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"},)
    def verify_password(self,password):
        return check_password(password,User.objects.get(uuid=self.uuid).password)

    def validate(self, attrs,request=None):
        
        username=attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        Admin = EmailBackend.authenticate(email=email,username=username,password=password,self=self,request=request)

        if not Admin:
            raise serializers.ValidationError('Invalid email or password')

        attrs['Admin'] = Admin
        return attrs

class ProductWeightSerializer(serializers.ModelSerializer):
    class Meta:
        model= ProductWeight
        fields=('Price','id')
  
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image')

class Serializer_Product(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='Sub_Category_id.category_id.name')
    category_id=serializers.ReadOnlyField(source='Sub_Category_id.category_id.id') 
    username=serializers.ReadOnlyField(source='created_by.username')
    images = ProductImageSerializer(many=True, read_only=True)
    Multiple_images=serializers.ListField(child=serializers.FileField(max_length=1000000, allow_empty_file = True, use_url = False),write_only = True)
    Prices=ProductWeightSerializer(many=True)
    Multiple_prices=serializers.ListField( write_only = True) #
    StoreName= serializers.ReadOnlyField(source='Store_id.Store_Name')
    StoreDelivery= serializers.ReadOnlyField(source='Store_id.Delivery')
    StorePickup= serializers.ReadOnlyField(source='Store_id.StoreFront')
    StoreCurbsidePickup= serializers.ReadOnlyField(source='Store_id.CurbSide_Pickup')
    SubcategoryName=serializers.ReadOnlyField(source='Sub_Category_id.name')
    StoreAddress= serializers.ReadOnlyField(source='Store_id.Store_Address') 	
    Brand_Name=serializers.ReadOnlyField(source='Brand_id.name') 	
    Store_Country=serializers.ReadOnlyField(source='Store_id.Country') 
    Store_State=serializers.ReadOnlyField(source='Store_id.State') 
    Store_City=serializers.ReadOnlyField(source='Store_id.City') 
    Store_Type=serializers.ReadOnlyField(source='Store_id.Store_Type') 
    
    class Meta:
        model = Product
        fields = ['Product_Name','SubcategoryName','category_name','StoreAddress','Multiple_prices','category_id','username','StoreName','StoreDelivery','StorePickup','StoreCurbsidePickup','id','Sub_Category_id' ,'Store_id','Product_Description', 'Prices','images','Multiple_images','SKU','UPC','lab_Result','strain','Alt_Text','Brand_id','rating','THC', 'CBD' ,'CBN','Status','Brand_Name','Store_Country','Store_State','Store_City','Store_Type','ProductCoupoun','CategoryCoupoun','TotalRating']
        extra_kwargs = {'created_by': {'default': serializers.CurrentUserDefault()}} 

    def create(self, validated_data):
        images_data = validated_data.pop('Multiple_images')
        price_data=validated_data.pop('Multiple_prices')
        product = Product.objects.create(**validated_data)
        for price_dat in price_data:
            d=json.loads(price_dat)
            ProductWeight.objects.create(product=product, Price=d)
        for image_data in images_data :
            ProductImage.objects.create(product=product, image=image_data)
        return product    
    def update(self, instance, validated_data):
        images_data = validated_data.pop('Multiple_images', [])
        self._create_images(instance, images_data)
        return super().update(instance, validated_data)

    def _create_images(self, product, images_data):
        for image_data in images_data:
            ProductImage.objects.create(product=product, image=image_data)

class UpdateProfile(serializers.ModelSerializer):
    class Meta:
        model=User
        fields='__all__'

class Serializer_HomePageBanner(serializers.ModelSerializer):
    class Meta:
        model=HomePageBanner
        fields='__all__'

class Serializer_Coupoun(serializers.ModelSerializer):
    username=serializers.ReadOnlyField(source='created_by.username')
    class Meta:
        model=Coupoun
        fields='__all__'
        extra_kwargs = {'created_by': {'default': serializers.CurrentUserDefault()}} 

class Serializer_USAData(serializers.ModelSerializer):
    file = models.FileField(blank=False, null=False,upload_to='CSV')
    class Meta:
        model=USACountry
        fields='__all__'

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    class Meta:
        fields = ('file',)

class Serializer_Law(serializers.ModelSerializer):
    class Meta:
        model=Law
        fields='__all__'

class Serializer_AboutUs(serializers.ModelSerializer):
    class Meta:
        model=AboutUs
        fields='__all__'

class Serializer_TermsAndCondition(serializers.ModelSerializer):
    class Meta:
        model=TermsandCondition
        fields='__all__'
        
class Serializer_PrivacyAndPolicies(serializers.ModelSerializer):
    class Meta:
        model=PrivacyandPolicies
        fields='__all__'

class Serializer_PromotionalBanners(serializers.ModelSerializer):
    class Meta:
        model=PromotionalBanners
        fields='__all__'

class Serializer_Subscribe(serializers.ModelSerializer):
    class Meta:
        model=Subscribe
        fields='__all__'

class Serializer_StaticImages(serializers.ModelSerializer):
    class Meta:
        model=StaticImages
        fields='__all__'



class Serializer_product(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields='__all__'




class Serializer_BookTheDemo(serializers.ModelSerializer):
    class Meta:
        model=BookTheDemo
        fields='__all__'
        
        
class Serializer_RolesandPermission(serializers.ModelSerializer):
    class Meta:
        model=CustomRole
        fields='__all__'