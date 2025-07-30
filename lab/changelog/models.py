from django.contrib.auth import get_user_model
from django.db import models
from uuid import uuid4
from django.contrib.contenttypes.models import ContentType

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
    # This should be a Foreign Key to ObjectType but we'll keep it a string to avoid one db call
    object_type = models.CharField(max_length=50, null=False, blank=False) 

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} at {self.timestamp}"
    
    @property
    def object_changelog(self):
        return getattr(self, self.object_type)
