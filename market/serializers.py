from rest_framework import serializers

from market.models import Product, Category, SubCategory, Author, Review, Order, OrderItem, Cart, CartItem, Payment
from exceptions.error_messages import ErrorCodes
from exceptions.exception import CustomAPIException

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'description', 'category']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'description', 'stock_quantity']
        
        
class ProductPartialUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    price = serializers.IntegerField(required=False)
    stock_quantity = serializers.IntegerField(required=False)
    category_id = serializers.IntegerField(required=False)
    subcategory_id = serializers.IntegerField(required=False)
    
    def validate(self, data):
        if data.get('category') is not None and data.get('category') < 1:
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED,
                                     message="category id must be positive integer")
        if data.get('subcategory') is not None and data.get('subcategory') < 1:
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED,
                                     message="subcategory id must be positive integer")
        return data
    


class ProductFilterSerializer(serializers.Serializer):
    max_price = serializers.IntegerField(required=False)
    min_price = serializers.IntegerField(required=False)
    category_id = serializers.IntegerField(required=False)
    subcategory_id = serializers.IntegerField(required=False)

    def validate(self, data):
        if data.get('max_price') and data.get('min_price') and data.get('min_price') > data.get('max_price'):
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED,
                                     message='min_price must be less than max_price')
        if data.get('category') is not None and data.get('category') < 1:
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED,
                                     message="category id must be positive integer")
        if data.get('subcategory') is not None and data.get('subcategory') < 1:
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED,
                                     message="subcategory id must be positive integer")
        return data


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'biography']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rating', 'comment']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'order', 'quantity', 'price']


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'cart', 'quantity']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'order', 'amount', 'status', 'method', 'gateway_response']