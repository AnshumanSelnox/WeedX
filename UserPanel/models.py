from django.db import models
from AdminPanel.models import *

class AddtoCart(models.Model):
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    Cart_Quantity=models.BigIntegerField(default=1)
    Product_id=models.ForeignKey(Product,on_delete=models.CASCADE,null=True)
    Store_id=models.ForeignKey(Stores,on_delete=models.CASCADE)
    Image_id=models.ForeignKey(ProductImage,on_delete=models.CASCADE,null=True)
    Price=models.JSONField()
    TotalPrice=models.IntegerField(null=True)
    Brand_Id=models.ForeignKey(Brand,on_delete=models.CASCADE,null=True)
    category=models.CharField(max_length=100,null=True)
    Sub_Category_id=models.ForeignKey(SubCategory,on_delete=models.CASCADE,null=True)
    
    def get_total(self):
        return round(float(self.Price["SalePrice"]) * float(self.Cart_Quantity))

    def save(self, *args, **kwargs):
        self.TotalPrice = self.get_total()
        super().save(*args, **kwargs)



class Order(models.Model):
    DeliveryTime=models.JSONField(null=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    OrderId=models.AutoField(default=1000,primary_key=True)
    IdCard=models.ImageField(upload_to='media/IdCard')
    FirstName=models.CharField(max_length=100)
    LastName=models.CharField(max_length=100)
    DateOfBirth=models.CharField(max_length=500)
    MobileNo=models.CharField(max_length=50)
    MedicalMarijuanaNumber=models.CharField(max_length=20)
    Order_Status=models.CharField(choices=OrderStatus,max_length=100,default="Pending")
    subtotal = models.DecimalField(max_digits=5000, decimal_places=2, default=0.00)
    Address=models.CharField(max_length=5000,null=True,blank=True)
    Store=models.ForeignKey(Stores,on_delete=models.CASCADE)
    Product=models.JSONField(null=True)
    OrderDate=models.DateField(auto_now=True)
    Order_Type=models.CharField(choices=OrderType,max_length=100,default="Delivery")

class Wishlist(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,null=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

 

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    Title=models.CharField(max_length=500,default=None,null=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
     
class BlogComment(models.Model):
    Blog = models.ForeignKey(News, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class BlogLike(models.Model):
    Blog = models.ForeignKey(News, on_delete=models.CASCADE)
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    like=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class BlankImage(models.Model):
    Image=models.ImageField(upload_to='media/BlankImage',null=True)


class StoreRatingAndReview(models.Model):
    StoreRating=models.IntegerField()
    StoreReview=models.TextField(null=True)
    Store=models.ForeignKey(Stores,on_delete=models.CASCADE)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE)
    
class BlogView(models.Model):
    blog=models.ForeignKey(News,on_delete=models.CASCADE,null=True)
    ViewCount=models.IntegerField(null=True) 
    def get_total(self):
        return round(int(self.ViewCount["ViewCount"]) +1)

    def save(self, *args, **kwargs):
        self.ViewCount = self.get_total()
        super().save(*args, **kwargs)  
        
        
class RecentView(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    
    
    
class UserProfileOrderDetails(models.Model):
    IdCard=models.ImageField(upload_to='media/IdCard')
    FirstName=models.CharField(max_length=100)
    LastName=models.CharField(max_length=100)
    DateOfBirth=models.CharField(max_length=500)
    MobileNo=models.CharField(max_length=50)
    MedicalMarijuanaNumber=models.CharField(max_length=20)
    email=models.EmailField()
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    
    
class SiteMap(models.Model):
    Xml=models.JSONField()

# class 