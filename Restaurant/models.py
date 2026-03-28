from django.contrib.gis.db import models
from users.models import User


class Restaurant(models.Model):
    owner = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name='restaurant'
)
    name = models.CharField(max_length=50)
    address = models.TextField()  
    location = models.PointField()
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='food_items'
    )
    name = models.CharField(max_length=100)
    Food_image = models.ImageField(upload_to="food_images/", null=True, blank=True)
    price = models.PositiveIntegerField()  
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"
    
