from django.db import models


# Create your models here.
class Recording(models.Model):
    video = models.FileField(upload_to="videos/")
    sensor_log = models.FileField(upload_to="logs/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recording {self.id} at {self.created_at}"
