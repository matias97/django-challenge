from django.test import RequestFactory, TestCase, SimpleTestCase
from django.urls import reverse, resolve
from rest_framework.test import APIRequestFactory
from rest_framework.renderers import JSONRenderer
from myapp.models import Product
from myapp.serializers import ProductSerializer
from myapp.views import ProductViewSet
from myapp.renderers import PlainJSONRenderer
from unittest.mock import Mock
from decimal import Decimal
import json

class TestPlainJSONRenderer(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.renderer = PlainJSONRenderer()
        self.context = {'request': self.factory.get('/')}

    def test_render_plain_json(self):
        data = {'key': 'value'}
        rendered_data = self.renderer.render(data, 'application/json', self.context)
        expected_json = json.dumps(data)

        rendered_data_dict = json.loads(rendered_data)
        expected_data_dict = json.loads(expected_json)
        self.assertEqual(rendered_data_dict, expected_data_dict)

    def test_render_with_renderer_context(self):
        data = {'key': 'value'}
        mock_renderer_context = Mock()
        mock_renderer_context.accepted_media_type = 'application/json'
        rendered_data = self.renderer.render(data, 'application/json', mock_renderer_context)
        expected_json = json.dumps(data)

        rendered_data_dict = json.loads(rendered_data)
        expected_data_dict = json.loads(expected_json)
        self.assertEqual(rendered_data_dict, expected_data_dict)

    def test_render_with_custom_media_type(self):
        data = {'key': 'value'}
        rendered_data = self.renderer.render(data, 'custom/media-type', self.context)
        expected_json = json.dumps(data)

        rendered_data_dict = json.loads(rendered_data)
        expected_data_dict = json.loads(expected_json)
        self.assertEqual(rendered_data_dict, expected_data_dict)

class TestUrls(SimpleTestCase):
    def test_product_list_url_resolves(self):
        url = reverse('product-list')
        self.assertEqual(resolve(url).func.cls, ProductViewSet)

class ProductViewSetTestCase(TestCase):
    def setUp(self):
        # Create test products
        self.product1 = Product.objects.create(
            name="Product 1",
            description="Description 1",
            price=10.0,
            quantity=5,
            category="Electronics"
        )

        self.product2 = Product.objects.create(
            name="Product 2",
            description="Description 2",
            price=20.0,
            quantity=10,
            category="Clothing"
        )

        self.product3 = Product.objects.create(
            name="Product 3",
            description="Description 3",
            price=30.0,
            quantity=15,
            category="Food"
        )

        self.factory = RequestFactory()

    def test_filter_by_name(self):
        # Test filtering by product name
        view = ProductViewSet.as_view({'get': 'list'})
        request = self.factory.get('/products/', {'name': 'Product 1'})
        response = view(request)
        serializer = ProductSerializer([self.product1], many=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def test_filter_by_price_range(self):
        # Test filtering by price range
        view = ProductViewSet.as_view({'get': 'list'})
        request = self.factory.get('/products/', {'min_price': 15.0, 'max_price': 25.0})
        response = view(request)
        serializer = ProductSerializer([self.product2], many=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def test_filter_by_category(self):
        # Test filtering by category
        view = ProductViewSet.as_view({'get': 'list'})
        request = self.factory.get('/products/', {'category': 'Food'})
        response = view(request)
        serializer = ProductSerializer([self.product3], many=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def test_no_filters(self):
        # Test no filters applied, should return all products
        view = ProductViewSet.as_view({'get': 'list'})
        request = self.factory.get('/products/')
        response = view(request)
        serializer = ProductSerializer([self.product1, self.product2, self.product3], many=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

class ProductSerializerTestCase(TestCase):
    def test_serializer_valid_data(self):
        """Test if the serializer handles valid data correctly."""
        valid_data = {
            'name': 'Sample Product',
            'description': 'This is a sample product.',
            'price': Decimal(9.99).quantize(Decimal('0.00')),
            'quantity': 10,
            'category': 'Electronics',
        }
        serializer = ProductSerializer(data=valid_data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})

    def test_serializer_invalid_data(self):
        """Test if the serializer handles invalid data correctly."""
        invalid_data = {
            'name': '',  # Missing required field
            'description': 'This is a sample product.',
            'price': '9.99', # Invalid decimal
            'quantity': 'invalid',  # Invalid integer
            'category': 'InvalidCategory',  # Invalid category
        }
        serializer = ProductSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
        self.assertIn('quantity', serializer.errors)
        self.assertIn('category', serializer.errors)

class ProductModelTestCase(TestCase):
    def setUp(self):
        # Create a sample Product object for testing
        self.product = Product(
            name="Sample Product",
            description="This is a sample product.",
            price=9.99,
            quantity=10,
            category="Electronics"
        )

    def test_product_creation(self):
        """Test if a Product can be created."""
        self.product.save()  # Save the Product object to the database
        saved_product = Product.objects.get(pk=self.product.pk)

        self.assertEqual(saved_product.name, "Sample Product")
        self.assertEqual(saved_product.description, "This is a sample product.")
        self.assertEqual(saved_product.price, Decimal(9.99).quantize(Decimal('0.00')))
        self.assertEqual(saved_product.quantity, 10)
        self.assertEqual(saved_product.category, "Electronics")

    def test_product_str_method(self):
        """Test the __str__ method of the Product model."""
        self.assertEqual(str(self.product), "Sample Product")

    def test_category_choices(self):
        """Test the category choices for the Product model."""
        for choice in Product.CATEGORY_CHOICES:
            self.assertIn(choice[0], ["Electronics", "Clothing", "Food"])
