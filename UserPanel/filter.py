from rest_framework import filters
from AdminPanel.models import *
from AdminPanel.serializer import *

from rest_framework import generics
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = Serializer_Product
    filter_backends = [filters.SearchFilter]
    search_fields = ['Product_Name']


class StoreListView(generics.ListAPIView):
    queryset = Stores.objects.all()
    serializer_class=Serializer_Store
    filter_backends=[filters.SearchFilter]
    search_fields=['Store_Name']