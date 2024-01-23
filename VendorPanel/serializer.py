from rest_framework import serializers
from .models import *
from AdminPanel.choices import *
from AdminPanel.models import *
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

        attrs['Vendor'] = user
        return attrs

class LoginSerializer1(serializers.Serializer):
    email = serializers.EmailField()

#Serializer to Get User Details using Django Token Authentication
class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ["id","username","Gender",'DateOfBirth','otp']
    
#Serializer to Register User
class RegisterSerializer1(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('username', 'password','email','Gender','DateOfBirth')
   

  def create(self, validated_data):
    user = User.objects.create(
      username=validated_data['username'],
      email=validated_data['email'],
      Gender=validated_data['Gender'],
      DateOfBirth=validated_data['DateOfBirth']
    )
    user.set_password(validated_data['password'])
    user.save()
    return user


from AdminPanel.serializer import *

class Serializer_CategoryinProduct(serializers.ModelSerializer):
  name = serializers.ReadOnlyField(source='Sub_Category_id.category_id.name')
  category_Image=serializers.ImageField(source='Sub_Category_id.category_id.categoryImages')
  id=serializers.ReadOnlyField(source='Sub_Category_id.category_id.id')
  class Meta:
    model=Product
    fields = ['name','category_Image','id']
    
class Serializer_ProductonlyId(serializers.ModelSerializer):
  class Meta:
    model=Product
    fields=('id',)
