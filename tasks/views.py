from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth.models import User
from tasks.models import Task, TaskList
from django.contrib.auth.decorators import login_required
from root.models import Tag
import datetime
import re

@login_required
def read_update(request, task_id=None):
    '''
    Gets/updates a given Task.
    '''
    if task_id is None:
        return HttpResponse('<h1>Not Found</h1>')

    task = Task.objects.get(id=task_id)

    if request.method == "GET":
        return render_to_response('tasks/task.html', 
                                    {'task': task}, 
                                    context_instance=RequestContext(request))

    elif request.method == "POST":
        completed = request.POST.get('completed', '')
        if completed == 'true':
            task.completed = True
        else:
            task.completed = False

        task.save()
        return HttpResponse('success')


@login_required
def read_create(request, filter_type=None, filter_id=None):
    '''
    Gets all the tasks given the filter_type. If filter_type is none it returns all 
    uncompleted Tasks. It also creates a Task.
    '''
    # Create Task
    if request.method == 'POST':
        task = request.POST.get('task')
        notes = request.POST.get('notes')
        if task:
            new_task = Task()
            new_task.title = task
            new_task.save()

            # Using regular expression to pick the tags:#, user:@, list:$ 
            # and date dd/mm/yy
            tags = re.findall('\#\w+', task)
            users = re.findall('\@\w+', task)
            lists = re.findall('\$\w+', task)
            due_date = re.findall('\d{2}/\d{2}/\d{2}', task)

            for tag in tags:
                tag_obj, _ = Tag.objects.get_or_create(name=tag.lstrip('#'))
                new_task.tag.add(tag_obj)
                task = task.replace(tag, '')

            for user in users:
                # I just continue if the user does not exist.
                try:
                    user_obj = User.objects.get(username=user.lstrip('@'))
                except DoesNotExist:
                    continue
                new_task.assigned_users.add(user_obj)
                task = task.replace(user, '')

            for task_list in lists:
                task_list_obj, _ = TaskList.objects.get_or_create(name=task_list.lstrip('$'))
                new_task.task_list = task_list_obj
                task = task.replace(task_list, '')

            # There must be only one due_date. So if the length of date > 0
            # we take the first date and store it as due_date
            if len(due_date) > 0:
                new_task.due_date = datetime.datetime.strptime(due_date[0], '%d/%m/%y')
                task = task.replace(due_date[0], '')

            # The dates, users, tags and lists are removed from the title.
            new_task.title = task
            new_task.notes = notes
            new_task.save()
            return HttpResponse('success')

    # Get Tasks
    else:
        tasks = Task.objects.order_by('-created')

        # GET has a parameted, completed, which is used to fetch all completed tasks.
        if request.GET.get('completed'):
            tasks = tasks.filter(completed=True)
        else:
            tasks = tasks.filter(completed=False)

        if filter_type == 'user':
            user = User.objects.get(id=filter_id)
            tasks = tasks.filter(assigned_users=user)

        elif filter_type == 'tag':
            tag = Tag.objects.get(id=filter_id)
            tasks = tasks.filter(tag=tag)

        elif filter_type == 'list':
            task_list = TaskList.objects.get(id=filter_id)
            tasks = tasks.filter(task_list=task_list)


        return render_to_response('tasks/index.html', 
                                    {'tasks': tasks}, 
                                    context_instance=RequestContext(request))

@login_required
def filter_date(request, year=None, month=None, day=None):
    tasks = Task.objects.filter(due_date__year=year, due_date__month=month, due_date__day=day).order_by('-created')
    return render_to_response('tasks/index.html', 
                                {'tasks': tasks}, 
                                context_instance=RequestContext(request))
