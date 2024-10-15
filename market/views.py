from drf_yasg import openapi
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.db.models import Q
from exceptions.error_messages import ErrorCodes
from exceptions.exception import CustomAPIException
from .serializers import (
    ProductSerializer, CategorySerializer, SubCategorySerializer,
    AuthorSerializer, ReviewSerializer, OrderSerializer,
    OrderItemSerializer, CartSerializer,CartItemSerializer, 
    ProductFilterSerializer, ProductPartialUpdateSerializer)
from .permissions import is_super_admin, is_authenticated_user
from .models import (Category, Product, SubCategory, 
    Review, Author, Order, OrderItem, Cart, CartItem)
from drf_yasg.utils import swagger_auto_schema


class CategoryApiView(ViewSet):
    @swagger_auto_schema(
        operation_summary='List of categories',
        operation_description='List of categories', responses={
            200: openapi.Response(description='List of categories', examples={
                'application/json': [{
                    'id': openapi.TYPE_INTEGER,
                    'name': openapi.TYPE_STRING,
                    'description': openapi.TYPE_STRING,
                }]

            }),
        },
        tags=['Category']
    )
    @is_super_admin
    def list(self, request):
        categories = Category.objects.all()
        return Response(
            data={'result': CategorySerializer(categories, many=True, context={'request': request}).data, 'ok': True},
            status=status.HTTP_200_OK)
    
    # need create/ update/ retrieve


class SubCategoryApiView(ViewSet):
    @swagger_auto_schema(
        operation_summary='List of subcategories',
        operation_description='List of subcategories', responses={
            200: openapi.Response(description='List of subcategories', examples={
                'application/json': [{
                    'id': openapi.TYPE_INTEGER,
                    'name': openapi.TYPE_STRING,
                    'description': openapi.TYPE_STRING,
                    'category_id': openapi.TYPE_INTEGER,
                }]
            })
        },
        tags=['SubCategory']
    )
    @is_super_admin
    def list(self, request):
        subcategories = SubCategory.objects.all()
        return Response(
            data={'result': SubCategorySerializer(subcategories, many=True, context={'request': request}).data,
                  'ok': True}, status=status.HTTP_200_OK)


class ProductApiView(ViewSet):
    @swagger_auto_schema(
        operation_summary='List of products',
        operation_description='List of products', responses={
            200: openapi.Response(description='List of products', examples={
                'application/json': [{
                    'id': openapi.TYPE_INTEGER,
                    'name': openapi.TYPE_STRING,
                    'description': openapi.TYPE_STRING,
                    'category_id': openapi.TYPE_INTEGER,
                    'price': openapi.TYPE_INTEGER,
                    'subcategory_id': openapi.TYPE_INTEGER,
                    'picture': openapi.TYPE_STRING,
                    'stock_quantity': openapi.TYPE_INTEGER,
                    'author': openapi.TYPE_STRING,
                }]
            })
        },
        tags=['Product']
    )
    @is_authenticated_user
    def list(self, request):
        products = Product.objects.all()
        return Response(
            data={'result': ProductSerializer(products, many=True, context={'request': request}).data, 'ok': True},
            status=status.HTTP_200_OK)
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name='max_price', in_=openapi.IN_QUERY, description='Maximum price of product', type=openapi.TYPE_NUMBER),
            openapi.Parameter(name='min_price', in_=openapi.IN_QUERY, description='Minimum price of product', type=openapi.TYPE_NUMBER),
            openapi.Parameter(name='category_id', in_=openapi.IN_QUERY, description='Category id', type=openapi.TYPE_INTEGER),
            openapi.Parameter(name='subcategory_id', in_=openapi.IN_QUERY, description='Subcategory id', type=openapi.TYPE_INTEGER),
        ],
        operation_summary='Filtered products',
        operation_description='Filtered products by price and categories',
        responses={200: ProductSerializer(many=True)},
        tags=['Product']
    )
    @is_authenticated_user
    def filter_product(self, request):
        serializer_params = ProductFilterSerializer(request.query_params, context={'request': request})
        if not serializer_params.is_valid():
            raise CustomAPIException(ErrorCodes.NOT_FOUND, serializer_params.errors)
        max_price = serializer_params.validated_data.get('max_price')
        min_price = serializer_params.validated_data.get('min_price')
        category_id = serializer_params.validated_data.get('category_id')
        subcategory_id = serializer_params.validated_data.get('subcategory_id')
        filter_ = Q()
        if category_id:
            filter_ &= Q(category_id=category_id)
        if subcategory_id:
            filter_ &= Q(subcategory_id=subcategory_id)
        if max_price:
            filter_ &= Q(price__gte=max_price)
        if min_price:
            filter_ &= Q(price__lte=min_price)
        products = Product.objects.filter(filter_)
        return Response(
            data={'result': ProductSerializer(products, many=True, context={'request': request}).data,
                  'ok': True}, status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary='Create product',
        operation_description='Create product',
        responses={200: ProductSerializer()},
        request_body=ProductSerializer,
        tags=['Product']
    )
    @is_super_admin
    def create(self, request):
        serializer = ProductSerializer(data=request.data)
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.NOT_FOUND, serializer.errors)
        serializer.save()
        return Response(data={'result': serializer.data, 'ok': True}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary='Update product',
        operation_description='Update product',
        responses={200: ProductPartialUpdateSerializer()},
        request_body=ProductSerializer,
        tags=['Product']
    )
    @is_super_admin
    def partial_update(self, request, pk):
        product = Product.objects.filter(id=pk).first()
        if not product:
            raise CustomAPIException(ErrorCodes.NOT_FOUND)
        serializer = ProductPartialUpdateSerializer(product, data=request.data, partial=True)
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.NOT_FOUND, serializer.errors)
        


class ReviewApiView(ViewSet):
    @swagger_auto_schema(
        operation_summary='List of reviews',
        operation_description='List of reviews', responses={
            200: openapi.Response(description='List of reviews', examples={
                'application/json': [{
                    'id': openapi.TYPE_INTEGER,
                    'name': openapi.TYPE_STRING,
                    'description': openapi.TYPE_STRING,
                    'author_id': openapi.TYPE_INTEGER,
                    'product_id': openapi.TYPE_INTEGER,
                }]
            })
        },
        tags=['Review']
    )
    def list(self, request):
        reviews = Review.objects.all()
        return Response(
            data={'result': ReviewSerializer(reviews, many=True).data, 'ok': True}, status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary='Review create',
        operation_description='Review create',
        request_body=ReviewSerializer,
        responses={201: ReviewSerializer()},
        tags=['Review']
    )
    @is_authenticated_user
    def create(self, request):
        data = request.data
        data.update({'user': request.user.id})
        serializer = ReviewSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED, serializer.errors)
        serializer.save()
        return Response(data={'result': serializer.data, 'ok': True}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary='Review update',
        operation_description='Review update',
        request_body=ReviewSerializer,
        responses={200: ReviewSerializer()},
        tags=['Review']
    )
    @is_authenticated_user
    def update(self, request, pk):
        data = request.data
        data.update({'user': request.user.id})
        review = Review.objects.filter(id=pk, user_id=request.user.id).first()
        if not review:
            raise CustomAPIException(ErrorCodes.NOT_FOUND)
        serializer = ReviewSerializer(review, data=data, partial=True)
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED, serializer.errors)
        serializer.save()
        return Response(data={'result': serializer.data, 'ok': True}, status=status.HTTP_200_OK)



class AuthorApiView(ViewSet):
    @swagger_auto_schema(
        operation_summary='List of authors',
        operation_description='List of authors', responses={
            200: openapi.Response(description='List of authors', examples={
                'application/json': [{
                    'id': openapi.TYPE_INTEGER,
                    'name': openapi.TYPE_STRING,
                    'first_name': openapi.TYPE_STRING,
                    'last_name': openapi.TYPE_STRING,
                    'biography': openapi.TYPE_STRING,
                }]
            })
        },
        tags=['Author']
    )
    @is_super_admin
    def list(self, request):
        authors = Author.objects.all()
        return Response(
            data={'result': AuthorSerializer(authors, many=True).data, 'ok': True}, status=status.HTTP_200_OK
        )
    
    # need create/ update


class OrderApiView(ViewSet):
    @swagger_auto_schema(
        operation_summary='List of orders for Admins',
        operation_description='List of orders for Admins', responses={
            200: openapi.Response(description='List of orders for Admins', examples={
                'application/json': [{
                    'id': openapi.TYPE_INTEGER,
                    'user_id': openapi.TYPE_INTEGER,
                    'total_price': openapi.TYPE_NUMBER,
                    'status': openapi.TYPE_STRING,
                }]
            })
        },
        tags=['Order']
    )
    @is_super_admin
    def list(self, request):
        orders = Order.objects.all()
        return Response(
            data={'result': OrderSerializer(orders, many=True).data, 'ok': True}, status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary='List of orders for Users',
        operation_description='List of orders for Users', responses={
            200: openapi.Response(description='List of orders for Users', examples={
                'application/json': [{
                    'id': openapi.TYPE_INTEGER,
                    'user_id': openapi.TYPE_INTEGER,
                    'total_price': openapi.TYPE_NUMBER,
                    'status': openapi.TYPE_STRING,
                }]
            })
        },
        tags=['Order']
    )
    @is_authenticated_user
    def customers_list(self, request):
        orders = Order.objects.filter(user_id=request.user.id)
        return Response(
            data={'result': OrderSerializer(orders, many=True).data, 'ok': True}, status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary='Order create',
        operation_description='Order create',
        request_body = OrderSerializer,
        responses={201: OrderSerializer()},
        tags=['Order']
    )
    @is_authenticated_user
    def create(self, request):
        data = request.data
        data['user'] = request.user.id
        serializer = OrderSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED, serializer.errors)
        serializer.save()
        return Response(data={'result': serializer.data, 'ok': True}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary='Order update',
        operation_description='Order update',
        request_body = OrderSerializer,
        responses={201: OrderSerializer()},
        tags=['Order']
    )
    @is_authenticated_user
    def update(self, request, pk):
        data = request.data
        data.update({'user': request.user.id})
        order = Order.objects.filter(id=pk, user_id=request.user.id).first()
        if not order:
            raise CustomAPIException(ErrorCodes.INVALID_INPUT)
        serializer = OrderSerializer(order, data=data, context={'request': request})
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.VALIDATION_FAILED, serializer.errors)
        serializer.save()
        return Response(data={'result': serializer.data, 'ok': True}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Order detail',
        operation_description='Order detail of user',
        responses={201: OrderSerializer()},
        tags=['Order']

    )
    @is_authenticated_user
    def get_order(self, request, pk):
        order = Order.objects.filter(id=pk, user_id=request.user.id).first()
        if not order:
            raise CustomAPIException(ErrorCodes.INVALID_INPUT)
        return Response(data={'result': OrderSerializer(order).data, 'ok': True}, status=status.HTTP_200_OK)



class OrderItemApiView(ViewSet):
    @swagger_auto_schema(
        operation_summary='Orders list for admins',
        operation_description='Orders list for admins', responses={
            200: openapi.Response(description='Orders list for admins', examples={
                'application/json': [{
                    'id': openapi.TYPE_INTEGER,
                    'price': openapi.TYPE_NUMBER,
                    'quantity': openapi.TYPE_INTEGER,
                    'product_id': openapi.TYPE_INTEGER,
                }]
            })
        }
    )
    @is_super_admin
    def list(self, request):
        order_items = OrderItem.objects.all()
        return Response(data={'result': OrderItemSerializer(order_items, many=True).data, 'ok': True}, status=status.HTTP_200_OK)
    


class CartApiView(ViewSet):
    @swagger_auto_schema(
        operation_summary='Carts list',
        operation_description='Carts list', responses={
            200: openapi.Response(description='Carts list', examples={
                'application/json': [{
                    'id': openapi.TYPE_INTEGER,
                    'user_id': openapi.TYPE_INTEGER,
                }]
            })
        }
    )
    @is_super_admin
    def list(self, request):
        carts = Cart.objects.all()
        return Response(data={'result': CartSerializer(carts).data, 'ok': True}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Users cart list',
        operation_description='Users cart list', responses={
            200: openapi.Response(description='Users cart list', examples={
                'application/json': [{
                    'id': openapi.TYPE_INTEGER,
                    'user_id': openapi.TYPE_INTEGER,
                }]
            })
        }
    )
    @is_authenticated_user
    def users_list(self, request):
        carts = Cart.objects.filter(user_id=request.user.id)
        return Response(data={'result': CartSerializer(carts, many=True).data, 'ok': True}, status=status.HTTP_200_OK)
    


class CartItemApiView(ViewSet):
    @swagger_auto_schema(
        operation_summary='CartItems list',
        operation_description='CartItems list', responses={
            200: openapi.Response(description='CartItems list', examples={
                'application/json': [{
                    'id': openapi.TYPE_INTEGER,
                    'quantity': openapi.TYPE_INTEGER,
                    'product_id': openapi.TYPE_INTEGER,
                    'cart_id': openapi.TYPE_INTEGER,
                }]
            })
        }
    )
    @is_super_admin
    def list(self, request):
        cart_items = CartItem.objects.all()
        return Response(data={'result': CartItemSerializer(cart_items, many=True).data, 'ok': True}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='User\'s CartItem list',
        operation_description = 'User\'s CartItem list', responses={
        200: openapi.Response(description='User\'s CartItem list', examples={
            'application/json': [{
                'id': openapi.TYPE_INTEGER,
                'quantity': openapi.TYPE_INTEGER,
                'product_id': openapi.TYPE_INTEGER,
                'cart_id': openapi.TYPE_INTEGER,
            }]
        })
    }
    )
    @is_authenticated_user
    def users_list(self, request):
        cart_items = CartItem.objects.filter(user_id=request.user.id)
        return Response(data={'result': CartItemSerializer(cart_items, many=True).data, 'ok': True}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary='Cart Item create',
        operation_description='Cart Item create',
        request_body = CartItemSerializer,
        responses={201: CartItemSerializer()},
        tags = ['CartItem']
    )
    @is_authenticated_user
    def create(self, request):
        data = request.data
        data['user_id'] = request.user.id
        serializer = CartItemSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            raise CustomAPIException(ErrorCodes.INVALID_INPUT, serializer.errors)
        serializer.save()
        return Response(data={'result': serializer.data, 'ok': True}, status=status.HTTP_201_CREATED)
