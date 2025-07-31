from django.contrib.auth import get_user_model
from django.db import models
from uuid import uuid4
from model_utils.managers import InheritanceManager

User = get_user_model()


class ChangeLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
    ]

    id = models.UUIDField(default=uuid4, primary_key=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    changed_fields = models.JSONField(null=True, blank=True)
    objects = InheritanceManager()
    target_model_name = models.CharField(
        max_length=30, blank=False, null=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} at {self.timestamp}"

