from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# Create your models here.


class Condition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    condition_date = models.DateField(auto_now_add=True)
    condition_time = models.TimeField(auto_now_add=True)
    condition_image_path = models.TextField(null=False)
    condition_location = models.TextField(null=False)


class Accident(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accident_date = models.DateField(auto_now_add=True)
    accident_time = models.TimeField(auto_now_add=True)
    accident_image_path = models.TextField(null=False)
    accident_location = models.TextField(null=False)
