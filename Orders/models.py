from django.db import models
from django.conf import settings
from Restaurant.models import Restaurant,FoodItem


class Orders(models.Model):

    STATUS = [
        ('PLACED', 'Placed'),
        ('ACCEPTED', 'Accepted'),
        ('PREPARING', 'Preparing'),
        ('OUT_OF_DELIVERY', 'Out of Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELED','Canceled')
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)
    total_price = models.FloatField()

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    status = models.CharField(max_length=30, choices=STATUS, default='PLACED')
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"Order {self.id} - {self.customer.username}"


class MyCart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    Food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()
  
  
    def total_price(self):
      return self.price * self.quantity
  
    def __str__(self):
        return f"{self.user.username} -_{self.Food_item}" 
    
    
