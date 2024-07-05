from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

User = get_user_model()


class QnA(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file_upload = models.FileField(upload_to="qna/files/", blank=True, null=True)

    def __str__(self):
        return self.title

# Signal handlers

@receiver(pre_save, sender=QnA)
def delete_old_qna_file(sender, instance, **kwargs):
    if instance.pk:
        old_instance = QnA.objects.get(pk=instance.pk)
        if old_instance.file_upload and old_instance.file_upload != instance.file_upload:
            old_instance.file_upload.delete(save=False)

@receiver(post_delete, sender=QnA)
def delete_qna_file_on_delete(sender, instance, **kwargs):
    if instance.file_upload:
        instance.file_upload.delete(save=False)