from django.db import models
from django.contrib.auth.models import User
from root.models import Tag

class TaskList(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Task(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    assigned_users = models.ManyToManyField(User, related_name='assigned_users', null=True, blank=True)
    title = models.CharField(max_length=300)
    notes = models.TextField(null=True, blank=True)
    tag = models.ManyToManyField(Tag, null=True, blank=True)
    task_list = models.ForeignKey(TaskList, null=True, blank=True)
    completed = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.title
