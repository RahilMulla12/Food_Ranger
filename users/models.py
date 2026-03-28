from pickle import TRUE
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models


class User(AbstractUser):
    is_customer = models.BooleanField(default=True)
    is_restaurant_owner = models.BooleanField(default=False)
    is_rider = models.BooleanField(default=False)

    phone = models.CharField(max_length=20, unique=True)
    location = models.PointField(null=True)

    USERNAME_FIELD = "phone"          
    REQUIRED_FIELDS = ["username"]    


    