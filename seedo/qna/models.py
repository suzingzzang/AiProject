from django.contrib.auth import get_user_model
from django.db import models

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
