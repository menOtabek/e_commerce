from django.urls import path
from .views import CategoryApiView, SubCategoryApiView, ProductApiView, ReviewApiView, AuthorApiView, OrderApiView
urlpatterns = [
    path('category/', CategoryApiView.as_view({'get': 'list'}), name='category'),
    path('subcategory/', SubCategoryApiView.as_view({'get': 'list'}), name='subcategory'),
    path('product/', ProductApiView.as_view({'get': 'list'}), name='product'),
    path('product_filter/', ProductApiView.as_view({'get': 'filter_product'}), name='product_filter'),
    path('review/', ReviewApiView.as_view({'get': 'list', 'post':'create'}), name='review'),
    path('review/<int:pk>/', ReviewApiView.as_view({'put': 'update'})),
    path('author/', AuthorApiView.as_view({'get': 'list'}), name='author'),
    path('order/', OrderApiView.as_view({'get': 'customers_list', 'post':'create'}), name='order'),
    path('orders_admin/', OrderApiView.as_view({'get': 'list'}), name='orders_admin'),
    path('order/<int:pk>/', OrderApiView.as_view({'patch':'update', 'get':'get_order'}), name='order_detail'),
]