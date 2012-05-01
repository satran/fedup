from django.db import models
from django.contrib.auth.models import User
from root.models import Tag
import re
import datetime

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

    def save_from_re(self, task):
        # Using regular expression to pick the tags:#, user:@, list:$ 
        # and date dd/mm/yy
        tags = re.findall('\#\w+', task)
        users = re.findall('\@\w+', task)
        lists = re.findall('\$\w+', task)
        due_date = re.findall('\d{2}/\d{2}/\d{2}', task)

        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(name=tag.lstrip('#'))
            self.tag.add(tag_obj)
            task = task.replace(tag, '')

        for user in users:
            # I just continue if the user does not exist.
            try:
                user_obj = User.objects.get(username=user.lstrip('@'))
            except DoesNotExist:
                continue
            self.assigned_users.add(user_obj)
            task = task.replace(user, '')

        for task_list in lists:
            task_list_obj, _ = TaskList.objects.get_or_create(name=task_list.lstrip('$'))
            self.task_list = task_list_obj
            task = task.replace(task_list, '')

        # There must be only one due_date. So if the length of date > 0
        # we take the first date and store it as due_date
        if len(due_date) > 0:
            self.due_date = datetime.datetime.strptime(due_date[0], '%d/%m/%y')
            task = task.replace(due_date[0], '')

        # The dates, users, tags and lists are removed from the title.
        self.title = task
        self.save()
