from django.db import models
from .choices import *
from ckeditor.fields import RichTextField
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from AdminPanel.choices import *


class UserManager(BaseUserManager):
    def create_user(self, username,email, password=None, **kwargs):
        if not email:
            raise ValueError('Email is required')
        # username=self.model(username)
        
        email = self.normalize_email(email)
        admin = self.model(username=username,email=email,**kwargs)
        
        admin.set_password(password)
        admin.save()
        return admin

    def create_superuser(self, username,email, password=None, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        return self.create_user(username,email, password, **kwargs)

class User(AbstractBaseUser):
    USER_CHOICES = (
        ('Admin', 'Admin'),
        ('Vendor', 'Vendor'),
        ('Customer','Customer'),
        ('Co-Owner','Co-Owner'),
        ('Content Manager Editor','Content Manager Editor'),
        ('vendor managent','vendor managent'),
        ('store managment','store managment')
    )

    user_type = models.CharField(choices=USER_CHOICES,default='Admin',max_length=30)
    image=models.ImageField(null=True,default='media/BlankImage.jpg',blank=True,upload_to='media/UserProfile')
    googlelink=models.URLField(null=True)
    Name=models.CharField(max_length=999,null=True)
    username= models.CharField(max_length=100,blank=True,null=True,unique=True)
    email = models.EmailField(unique=True)
    MobilePhone=models.CharField(max_length=20,null=True)
    password=models.CharField(max_length=50)
    DeliveryAddress=models.CharField(max_length=5000,null=True)
    MedicalCardNumber=models.CharField(max_length=50,null=True)
    MedicalCardExpire=models.DateField(null=True)
    MedicalCardState=models.CharField(max_length=100,null=True)
    EmailBoolean=models.BooleanField(default=False)
    NewsLetter=models.BooleanField(default=False)
    ReviewSuggestions=models.BooleanField(default=False)
    PushNotification=models.BooleanField(default=False)
    Recommendations=models.BooleanField(default=False)
    Savings=models.BooleanField(default=False)
    OrderupdatePushNotification=models.BooleanField(default=False)
    OrderupdateSMSNotifications=models.BooleanField(default=False)
    DateOfBirth= models.CharField(max_length=100,blank=True,null=True,default=None)
    otp=models.IntegerField(null=True,default=None)
    PhotoId=models.ImageField(null=True,default=None,blank=True,upload_to='media/PhotoId')
    Gender=models.CharField(choices=Gender,max_length=50,default=None,null=True,blank=True)
    status=models.CharField(choices=Status,default="Active",max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser=models.BooleanField(default=False)
    # created = models.DateField(auto_now_add=True,null=True)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email","password"]

    objects = UserManager()

    def __str__(self):
        return self.email


class Category(models.Model):               #category table
    name=models.CharField(max_length=500,unique=True)
    categoryImages=models.ImageField(upload_to='media/Category',null=True)
    Status=models.CharField(max_length=20,default=1,choices=Status)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    Meta_title=models.CharField(max_length=60,default=None,blank=False,null=True)
    Meta_Description=models.CharField(max_length=160,default=None,blank=False,null=True)
    Url_slug=models.CharField(max_length=2048,default=None,blank=True,null=True)
    
    def __str__(self):
        return self.name

class SubCategory(models.Model):            #Subcategory table
    name=models.CharField(max_length=500,unique=True)
    category_id=models.ForeignKey(Category,on_delete=models.CASCADE,default=1,related_name='subcategories')
    Status=models.CharField(max_length=20,default=1,choices=Status)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    Meta_title=models.CharField(max_length=60,default=None,blank=False,null=True)
    Meta_Description=models.CharField(max_length=160,default=None,blank=False,null=True)
    Url_slug=models.CharField(max_length=2048,default=None,blank=True,null=True)
    SubCategoryImage=models.ImageField(null=True,upload_to='media/SubCategory')

    def __str__(self):
        return self.name

    
class Countries(models.Model):                      #Country Table
    CountryName=models.CharField(max_length=100,unique=True)
    CountryFlag=models.ImageField(upload_to='media/Country',null=True)
    Status=models.CharField(max_length=20,default=1,choices=Status)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.CountryName
    
    
class States(models.Model):                         #State Table
    StateName=models.CharField(max_length=100,unique=True)
    StateFlagFlag=models.ImageField(upload_to='media/State',null=True)
    Country_id=models.ForeignKey(Countries, on_delete=models.CASCADE,default=1)
    Status=models.CharField(max_length=20,default=1,choices=Status)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.StateName
    
class Cities(models.Model):                         #City Table
    CityName=models.CharField(max_length=100,unique=True)
    CityFlag=models.ImageField(upload_to='media/City ',null=True)
    States_id=models.ForeignKey(States,on_delete=models.CASCADE,default=1)
    Status=models.CharField(max_length=20,default=1,choices=Status)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.CityName
    

class Stores(models.Model):
    Country=models.CharField(null=True,max_length=500)
    State=models.CharField(null=True,max_length=500)
    City=models.CharField(null=True,max_length=500)
    MinimumOrderPrice=models.JSONField(null=True)
    Locations=models.JSONField(null=True)
    Hours=models.JSONField(null=True)
    SetbyMin=models.JSONField(null=True)
    searchboxlocation=models.JSONField(null=True)
    SetbyDays=models.JSONField(null=True)
    FaceBook=models.URLField(null=True)
    Instagram=models.URLField(null=True)
    Twitter=models.URLField(null=True)
    VideoLink=models.URLField(null=True)
    # StoreEmail=models.EmailField(null=True)
    DeliveryInformation=models.CharField(max_length=9999999,null=True,blank=True)
    Store_Name=models.CharField(max_length=100,null=True)
    Legal_Store_Name=models.CharField(max_length=1000,null=True)
    Store_Address=models.CharField(max_length=1000,null=True)
    Store_Type=models.CharField(max_length=50,choices=StoreType,default=None,null=True)
    Stores_Description=RichTextField(default=None,blank=True,null=True)
    Store_Image=models.ImageField(upload_to='media/Brand',default=None,blank=True,null=True)
    Stores_Website=models.URLField(max_length=200,blank=True,default=None,null=True)
    Stores_MobileNo=models.CharField(max_length=15,unique=True)
    LicenceNo=models.CharField(max_length=50,default=None,unique=True,blank=True,null=True)
    License_Type=models.CharField(max_length=23,default="None",choices=LicenseType,null=True)
    Expiration=models.CharField(max_length=100,default=None,blank=True,null=True)
    Licence_Doc = models.FileField(upload_to="media/LicenceDocument",null= True,blank=True)
    Status=models.CharField(max_length=20,default="Hide",choices=Status)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    Meta_title=models.CharField(max_length=60,default=None,blank=False,null=True)
    Meta_Description=models.CharField(max_length=160,default=None,blank=False,null=True)
    Url_slug=models.CharField(max_length=2048,default=None,blank=True,null=True)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    rating=models.IntegerField(default=None,null=True)
    Order_Type=models.CharField(max_length=50,choices=OrderType,default="Delivery")
    Dogs_allowed=models.BooleanField(default=False,null=True)
    Has_gender_neutral_toilets=models.BooleanField(default=False,null=True)
    High_chairs_available=models.BooleanField(default=False,null=True)
    Has_toilets=models.BooleanField(default=False,null=True)
    Minimum_21_years_or_older=models.BooleanField(default=False,null=True)
    Recreational=models.BooleanField(default=False,null=True)
    Medical=models.BooleanField(default=False,null=True)
    Cash_on_Delivery=models.BooleanField(default=False,null=True)
    Security_Staff=models.BooleanField(default=False,null=True)
    CarParking=models.BooleanField(default=False,null=True)
    Wi_Fi=models.BooleanField(default=False,null=True)
    lat=models.FloatField(null=True)
    lng=models.FloatField(null=True)
    StoreFront=models.BooleanField(default=False,null=True)
    Delivery=models.BooleanField(default=False,null=True)
    CurbSide_Pickup=models.BooleanField(default=False,null=True)
    Has_bar_on_site=models.BooleanField(default=False,null=True)
    # CurbSideAddress=models.CharField(max_length=999999,null=True)
    CurbSidePickupHours=models.JSONField(null=True)
    CurbSideCity=models.CharField(max_length=999999,null=True)
    CurbSideState=models.CharField(max_length=999999,null=True)
    CurbSideZipCode=models.CharField(max_length=999999,null=True)
    CurbsideLatAndLong=models.JSONField(null=True)
    TotalRating=models.IntegerField(default=0)
    # DeliveryHours=models.JSONField(null=True)

    def __str__(self):
        return self.Store_Name

class Brand(models.Model):                  #Brand
    name=models.CharField(max_length=50,default=None,unique=True)
    Brand_description=RichTextField(default=None)
    Brand_Logo=models.ImageField(upload_to='media/Brand',default=None,null=True)
    Status=models.CharField(max_length=20,default=1,choices=Status)
    Link=models.URLField(max_length=200,blank=True,default=None)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    Meta_title=models.CharField(max_length=60,default=None,blank=True,null=True)
    Meta_Description=models.CharField(max_length=160,default=None,blank=True,null=True)
    Url_slug=models.CharField(max_length=2048,default=None,blank=True,null=True)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    rating=models.IntegerField(default=None,null=True)
    def __str__(self):
        return self.name
    
class Salestaxes(models.Model):                    #Salestax
    tax_value=models.IntegerField(default=0)
    State=models.ForeignKey(States,on_delete=models.CASCADE)
    tax_type=models.CharField(max_length=20,unique=True)
    Status=models.CharField(max_length=20,default=1,choices=Status)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.tax_type
    
class Estemeedtaxes(models.Model):                    #Esteemedtax
    tax_value=models.IntegerField(default=0)
    State=models.ForeignKey(States,on_delete=models.CASCADE)
    tax_type=models.CharField(max_length=20,unique=True)
    Status=models.CharField(max_length=20,default=1,choices=Status)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.tax_type    

class Net_Weight(models.Model):                 #Net Weight
    Weight=models.CharField(max_length=50,default=None)
    Weight_Price=models.IntegerField(default=0)
    Status=models.CharField(max_length=20,default=1,choices=Status)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    #created_by=models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.Weight

class Product(models.Model):                #Product
    id=models.AutoField(primary_key=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    Product_Name=models.CharField(max_length=100)   
    Product_Description=RichTextField(default=None,blank=True,null=True) 
    SKU=models.CharField(max_length=100,default=None,blank=True,null=True)
    Sub_Category_id=models.ForeignKey(SubCategory,on_delete=models.CASCADE,default=None)
    strain=models.CharField(max_length=50,choices=StrainTypes,default=None)
    UPC=models.CharField(max_length=100,blank=True,null=True,default=None)
    Brand_id=models.ForeignKey(Brand,on_delete=models.CASCADE,blank=True,null=True )
    THC=models.IntegerField(default=0,blank=True)
    CBD=models.IntegerField(default=0,blank=True)
    CBN=models.IntegerField(default=0,blank=True)
    lab_Result=models.CharField(max_length=50,choices=LabResult)
    tag=models.CharField(max_length=50,default=None,blank=True,null=True)
    Store_id=models.ForeignKey(Stores,on_delete=models.CASCADE,default=None)
    Meta_title=models.CharField(max_length=60,default=None,blank=False,null=True)
    Meta_Description=models.CharField(max_length=160,default=None,blank=False,null=True)
    Url_slug=models.CharField(max_length=2048,default=None,blank=True,null=True)
    Alt_Text=models.CharField(max_length=50,default=None,blank=False,null=True)
    Link=models.URLField(max_length=200,blank=True,default=None,null=True)
    Status=models.CharField(max_length=20,default="Active",choices=Status)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    rating=models.IntegerField(default=None,null=True)
    WishList=models.BooleanField(default=False)
    # Coupoun=models.JSONField(default=list,null=True)

 
    def __str__(self):
        return self.Product_Name

class ProductWeight(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,null=True,related_name='Prices')
    Price=models.JSONField()


class NewsCategory(models.Model):               #category table  
    name=models.CharField(max_length=500,unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    Meta_title=models.CharField(max_length=60,default=None,blank=False,null=True)
    Meta_Description=models.CharField(max_length=160,default=None,blank=False,null=True)
    Url_slug=models.CharField(max_length=2048,default=None,blank=True,null=True)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class NewsSubCategory(models.Model):            #Subcategory table
    name=models.CharField(max_length=500,unique=True)
    category_id=models.ForeignKey(NewsCategory,on_delete=models.CASCADE,default=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    Meta_title=models.CharField(max_length=60,default=None,blank=False,null=True)
    Meta_Description=models.CharField(max_length=160,default=None,blank=False,null=True)
    Url_slug=models.CharField(max_length=2048,default=None,blank=True,null=True)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    
 

        
    


class News(models.Model):
    Category_id=models.ForeignKey(NewsCategory,on_delete=models.CASCADE,default=1)
    SubCategory_id=models.ForeignKey(NewsSubCategory,on_delete=models.CASCADE,blank=True,default=None,null=True)
    Title=models.CharField(max_length=100,default=None)
    Description=RichTextField(null=True)
    Image=models.ImageField(upload_to='media/Products',default=None,blank=True,null=True)
    Alt_Text=models.CharField(max_length=50,default=None,blank=False)
    Meta_title=models.CharField(max_length=60,default=None,blank=False,null=True)
    Meta_Description=models.CharField(max_length=160,default=None,blank=False,null=True)
    Url_slug=models.CharField(max_length=2048,default=None,blank=True,null=True)
    Publish_Date=models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    ViewCount=models.IntegerField(default=0) 

    def __str__(self):
        return self.Title
    
    def save(self, *args, **kwargs):
        self.ViewCount = self.ViewCount + 1
        super().save(*args, **kwargs)




class ExportFile(models.Model):
    File=models.FileField(upload_to="excel")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)



class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/product_images')



class HomePageBanner(models.Model):
    Banner=models.ImageField(upload_to='media/Banner')
    mobile=models.ImageField(upload_to='media/MobileBanner')




class Coupoun(models.Model):
    discountType=(('Amount off Products','Amount off Products'),('Amount off Order','Amount off Order'),('Buy X get Y','Buy X get Y'),('Free Shipping','Free Shipping'))
    choice=(('Percentage','Percentage'),('Amount','Amount'))
    DiscountCode=models.CharField(max_length=100,default=None,null=True,unique=True)
    AutomaticDiscount=models.CharField(max_length=100,default=None,null=True,unique=True)
    PercentageAmount=models.IntegerField(null=True)
    ValueAmount=models.IntegerField(null=True)
    status=models.CharField(max_length=500,choices=Status)   
    product=models.ManyToManyField(Product,blank=True)  
    category=models.ManyToManyField(Category,blank=True)
    NoMinimumRequirements=models.BooleanField(null=True)
    MinimumPurchaseAmount=models.IntegerField(null=True)
    MinimumQuantityofItem=models.IntegerField(null=True)
    AllCustomer=models.JSONField(default=list,null=True)
    SpecificCustomer=models.JSONField(null=True)
    Specific_customer_segments=models.JSONField(null=True)
    LimitNumberOfTime=models.IntegerField(null=True)
    LimitToOneUsePerCustomer=models.BooleanField(null=True)
    CombinationProduct=models.BooleanField(null=True)
    CombinationDiscount=models.BooleanField(null=True)
    CustomerBuys=models.JSONField(null=True)
    CustomerGets=models.JSONField(null=True)
    MaximumUsesPerOrder=models.IntegerField(null=True)
    DiscountType=models.CharField(choices=discountType,max_length=10000,null=True,blank=True)
    free=models.BooleanField(null=True)
    ProLocationOnly=models.BooleanField(null=True)
    CustomerSpends=models.JSONField(null=True)
    AllLocation=models.BooleanField(null=True)
    SelectedLocation=models.JSONField(null=True)
    ShippingRate=models.IntegerField(null=True)
    StartDate=models.DateField(null=True)
    StartTime=models.TimeField(null=True)
    EndDate=models.DateField(null=True)
    EndTime=models.TimeField(null=True)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE,null=True)



class USACountry(models.Model):
    
    zip=models.CharField(max_length=100,null=True)
    lat=models.CharField(max_length=100,null=True)
    lng=models.CharField(max_length=100,null=True) 
    city=models.CharField(max_length=100,null=True) 
    state_id=models.CharField(max_length=100,null=True) 
    state_name=models.CharField(max_length=100,null=True) 
    zcta=models.CharField(max_length=100,null=True) 
    parent_zcta=models.CharField(max_length=100,null=True) 
    population=models.CharField(max_length=100,null=True) 
    density=models.CharField(max_length=100,null=True) 
    county_fips=models.CharField(max_length=100,null=True) 
    county_name=models.CharField(max_length=100,null=True) 
    county_weights=models.CharField(max_length=100,null=True) 
    county_names_all=models.CharField(max_length=100,null=True) 
    county_fips_all=models.CharField(max_length=100,null=True) 
    imprecise=models.CharField(max_length=100,null=True) 
    military=models.CharField(max_length=100,null=True) 
    timezone=models.CharField(max_length=100,null=True) 


class Law(models.Model):
    Country=models.ForeignKey(Countries,on_delete=models.CASCADE)
    State=models.ForeignKey(States,on_delete=models.CASCADE)
    City=models.ForeignKey(Cities,on_delete=models.CASCADE)
    content=RichTextField()


class AboutUs(models.Model):
    Content=RichTextField()
    FeaturedImage=models.ImageField(upload_to='media/AboutUs',null=True)

class TermsandCondition (models.Model):
    Content=RichTextField()

class PrivacyandPolicies(models.Model):
    Content=RichTextField()


class PromotionalBanners(models.Model):
    Country=models.CharField(max_length=100,null=True)
    State=models.CharField(max_length=100,null=True)
    Banner=models.ImageField(upload_to='media/PromotionalBanner',null=True)
    Title=models.CharField(max_length=999,default="",null=True)
    Link=models.URLField(null=True)
    mobile=models.ImageField(upload_to='media/MobilePromotionalBanner')



class Subscribe(models.Model):
    email=models.EmailField(unique=True)
    
    
class StaticImages(models.Model):
    Logo=models.ImageField(upload_to='media/Logo')
    AboutUs1=models.ImageField(upload_to='media/AboutUs1')
    AboutUs2=models.ImageField(upload_to='media/AboutUs2')
    AboutUs3=models.ImageField(upload_to='media/AboutUs3')
    AboutUs4=models.ImageField(upload_to='media/AboutUs4')
    ShareImage=models.ImageField(upload_to='media/ShareImage')
    Fourhundredfour=models.ImageField(upload_to='media/Fourhundredfour')
    Fourhundredthree=models.ImageField(upload_to='media/Fourhundredthree')
    Fivehundredthree=models.ImageField(upload_to='media/Fivehundredthree')
    blogbanner=models.ImageField(upload_to='media/blogbanner')
    Indica=models.ImageField(upload_to='media/Strain')
    Hybrid=models.ImageField(upload_to='media/Strain')
    Sativa=models.ImageField(upload_to='media/Strain')
    CBD=models.ImageField(upload_to='media/Strain')