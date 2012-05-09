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
        task_text = request.POST.get('task', '')
        notes = request.POST.get('notes', '')
        if task_text:
            task.notes = notes
            task.save_from_re(task_text)

        completed = request.POST.get('completed', '')
        if completed == 'true':
            task.completed = True
            task.completed_date = datetime.datetime.now()
        elif completed == 'false':
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
            new_task.notes = notes
            new_task.save_from_re(task)
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
