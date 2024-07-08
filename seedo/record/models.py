from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

User = get_user_model()

# Create your models here.


class Condition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    condition_date = models.DateField(auto_now_add=True)
    condition_time = models.TimeField(auto_now_add=True)
    condition_image = models.ImageField(upload_to="record/images/")
    condition_location = models.TextField(null=False)


class Accident(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accident_date = models.DateField(auto_now_add=True)
    accident_time = models.TimeField(auto_now_add=True)
    accident_video = models.FileField(upload_to="record/videos/")
    accident_location = models.TextField(null=False)


# Signal handlers


@receiver(pre_save, sender=Condition)
def delete_old_condition_image(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Condition.objects.get(pk=instance.pk)
        if old_instance.condition_image and old_instance.condition_image != instance.condition_image:
            old_instance.condition_image.delete(save=False)


@receiver(post_delete, sender=Condition)
def delete_condition_image_on_delete(sender, instance, **kwargs):
    if instance.condition_image:
        instance.condition_image.delete(save=False)


@receiver(pre_save, sender=Accident)
def delete_old_accident_video(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Accident.objects.get(pk=instance.pk)
        if old_instance.accident_video and old_instance.accident_video != instance.accident_video:
            old_instance.accident_video.delete(save=False)


@receiver(post_delete, sender=Accident)
def delete_accident_video_on_delete(sender, instance, **kwargs):
    if instance.accident_video:
        instance.accident_video.delete(save=False)
