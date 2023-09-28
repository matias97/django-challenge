from rest_framework import viewsets
from django_filters import rest_framework as filters
from .models import Product
from .serializers import ProductSerializer
from .renderers import PlainJSONRenderer

class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    category = filters.CharFilter(field_name='category', lookup_expr='iexact')

    class Meta:
        model = Product
        fields = []

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    renderer_classes = [PlainJSONRenderer]

    def get_queryset(self):
        queryset = Product.objects.all()  # Retrieve all products initially

        # Apply filters based on query parameters
        name = self.request.query_params.get('name')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        category = self.request.query_params.get('category')

        if name:
            queryset = queryset.filter(name__icontains=name)

        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        if category:
            queryset = queryset.filter(category__iexact=category)

        return queryset
