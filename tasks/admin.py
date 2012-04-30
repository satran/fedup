from django.contrib import admin
from tasks.models import Task, TaskList

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'due_date', 'completed')
    
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskList)
