from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length = 150)
    price = models.FloatField()
    quantity = models.IntegerField()
    description = models.TextField()
    sell_price = models.IntegerField(null=True, blank=True)
    discount = models.IntegerField(blank=True, default=0)
    discounted_price = models.IntegerField(blank=True, default=0)
    minimum_order=models.IntegerField(blank=True,null=True)
    added_date= models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        default='default.jpg', upload_to='media/images', blank=True)
    @property
    def discount_in_percentage(self):
        return f"{self.discount} %"

    @property
    def discounted_price(self):
        return ((self.price*self.discount)/100)

    @property
    def sell_price(self):
        return ((self.price - self.discounted_price))

    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (200, 200)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def __str__(self):
        return str(self.name)

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(max_length = 150)
    email= models.EmailField(blank=True,null=True)
    phone= models.CharField(max_length = 150)
    quantity=models.IntegerField()
    postal_code= models.IntegerField()
    village=models.CharField(max_length = 150)
    district=models.CharField(max_length = 150,blank=True,null=True)
    division=models.CharField(max_length = 150,blank=True,null=True)
    
    def __str__(self):
        return str(self.product.name)