from django.test import TestCase
from rest_framework.test import APIRequestFactory
factory = APIRequestFactory()
request = factory.post('/notes/', {'title': 'new idea'})
# Create your tests here.
