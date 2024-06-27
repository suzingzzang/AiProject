from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class UserRequest(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requested_requests")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Request from {self.requester.email} to {self.recipient.email}"
