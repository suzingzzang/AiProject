from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Navigation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_location = models.TextField()
    end_location = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.start_location} to {self.end_location}"
