import textwrap
from django.db import models
from base_model.base_m import BaseModel
from users.models import User

PAYMENT_METHOD_CHOICES = (
    (1, 'CASH_ON_DELIVERY'),
    (2, 'CREDIT_CARD'),
)

PAYMENT_STATUS_CHOICES = (
    (1, 'PENDING'),
    (2, 'COMPLETED'),
    (3, 'FAILED'),
    (4, 'REFUNDED'),
)

ORDER_STATUS_CHOICES = (
    (1, 'CREATED'),
    (2, 'SHIPPED'),
    (3, 'DELIVERED'),
    (4, 'PAID'),
)


class Category(BaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name


class SubCategory(BaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='sub_categories', null=True,
                                 blank=True)

    def __str__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    biography = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Product(BaseModel):
    name = models.CharField(max_length=255)
    picture = models.ImageField(upload_to="product_pictures", default="default.jpg", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='category_products',
                                 blank=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True,
                                     related_name='sub_category_products', blank=True)
    price = models.FloatField()
    description = models.TextField()
    stock_quantity = models.IntegerField(default=1)
    author = models.ManyToManyField(Author, blank=True, related_name='author_products')

    def __str__(self):
        return self.name


class Review(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='user_reviews', blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='reviews', blank=True)
    comment = models.TextField()
    rating = models.IntegerField()

    def __str__(self):
        return textwrap.shorten(self.comment, width=150, placeholder="...")


class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.FloatField()
    status = models.IntegerField(choices=ORDER_STATUS_CHOICES, default=1)

    def __str__(self):
        return f"{self.user.first_name}'s order at {self.created_at}"


class OrderItem(BaseModel):
    price = models.FloatField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} {self.quantity} {self.price}"


class Cart(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name}'s cart"


class CartItem(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} {self.quantity}"


class Payment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='user_payments', blank=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.FloatField()
    status = models.IntegerField(choices=PAYMENT_STATUS_CHOICES, default=1)
    method = models.IntegerField(choices=PAYMENT_METHOD_CHOICES, default=1)
    gateway_response = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.order.user.first_name}'s payment with {self.amount}"
