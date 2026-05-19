# Create your models here.

from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Session(models.Model):
    id = models.AutoField(primary_key=True) 
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    score = models.FloatField()

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"Session {self.uuid} - {self.user.username}"
