from django.db import models
from django.contrib.auth.models import User

class Goal(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    assigned_user = models.ForeignKey(User)
    summary = models.TextField()
