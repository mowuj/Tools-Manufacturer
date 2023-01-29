from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=150)
    image=models.ImageField(upload_to='admins')
    phone=models.CharField(max_length=15)

    def __str__(self):
        return self.user.username

class Customer(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=150)
    address=models.CharField(max_length = 200,blank=True,null=True)
    joined=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Category(models.Model):
    title= models.CharField(max_length = 150)
    slug=models.SlugField(unique=True)
    def __str__(self):
        return self.title

class Product(models.Model):
    title=models.CharField(max_length=150)
    category=models.ForeignKey(Category, on_delete=models.CASCADE)   
    slug=models.SlugField(unique=True)
    image = models.ImageField(
        default='default.jpg', upload_to='media/images')
    marked_price=models.PositiveIntegerField()
    sell_price=models.PositiveIntegerField()
    description = models.TextField()
    warranty=models.CharField(max_length = 150,blank=True,null=True)
    return_policy=models.CharField(max_length = 150,blank=True,null=True)
    view_count=models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.title

class Cart(models.Model):
    customer=models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True,blank=True)
    total=models.PositiveIntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Cart: " + str(self.id)
class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    rate=models.PositiveIntegerField()
    quantity=models.PositiveIntegerField()
    subtotal=models.PositiveIntegerField()

    def __str__(self):
        return "Cart: " + str(self.cart.id) + "CartProduct: " + str(self.id)
ORDER_STATUS=(
    ("Order Received","Order Received"),
    ("Order Processing","Order Processing"),
    ("On the way","On the way"),
    ("Order Completed","Order Completed"),
    ("Order Canceled","Canceled"),
)
METHOD=(
    ("Cash On Delivery","Cash On Delivery"),
    ("Stripe","Stripe")
)
class Order(models.Model):
    cart=models.OneToOneField(Cart, on_delete=models.CASCADE)
    ordered_by= models.CharField(max_length = 250)
    shipping_address=models.CharField(max_length = 250)
    phone=models.CharField(max_length = 13)
    email = models.EmailField(null=True,blank=True)
    subtotal=models.PositiveIntegerField()
    discount=models.PositiveIntegerField()
    total=models.PositiveIntegerField()
    order_status=models.CharField(max_length = 250,choices=ORDER_STATUS)
    created_at=models.DateTimeField(auto_now_add=True)
    payment_method=models.CharField(max_length = 20,choices=METHOD,default="Cash On Delivery")
    payment_completed=models.BooleanField(default=False,null=True,blank=True)

    def __str__(self):
        return "Order: " + str(self.id)


#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length = 150)
#     price = models.FloatField()
#     quantity = models.IntegerField()
#     description = models.TextField()
#     sell_price = models.IntegerField(null=True, blank=True)
#     discount = models.IntegerField(blank=True, default=0)
#     discounted_price = models.IntegerField(blank=True, default=0)
#     minimum_order=models.IntegerField(blank=True,null=True)
#     added_date= models.DateTimeField(auto_now_add=True)
#     image = models.ImageField(
#         default='default.jpg', upload_to='media/images', blank=True)
#     @property
#     def discount_in_percentage(self):
#         return f"{self.discount} %"

#     @property
#     def discounted_price(self):
#         return ((self.price*self.discount)/100)

#     @property
#     def sell_price(self):
#         return ((self.price - self.discounted_price))

#     def save(self, *args, **kwargs):
#         super(Product, self).save(*args, **kwargs)
#         img = Image.open(self.image.path)
#         if img.height > 300 or img.width > 300:
#             output_size = (200, 200)
#             img.thumbnail(output_size)
#             img.save(self.image.path)

#     def __str__(self):
#         return str(self.name)

