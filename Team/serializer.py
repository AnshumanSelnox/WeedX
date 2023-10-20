from rest_framework import serializers
from AdminPanel.models import *


class RegisterUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('user_type','username', 'password','email','image','Name','MobilePhone','status')
   

  def create(self, validated_data):
    user = User.objects.create(
      username=validated_data['username'],
      email=validated_data['email'],
      image=validated_data['image'],
      Name=validated_data['Name'],
      MobilePhone=validated_data['MobilePhone'],
      user_type=validated_data['user_type']
    )
    user.set_password(validated_data['password'])
    user.save()
    return user
