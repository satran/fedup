from django.shortcuts import render_to_response
from django.template import RequestContext
from tasks.models import Task, TaskList
from root.models import Tag
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from leaves.models import Leave

@login_required
def index(request):
    tasks = Task.objects.filter(assigned_users=request.user, completed=False).order_by('-created')[:5]
    leaves = Leave.objects.filter(user=request.user).order_by('-from_date')[:5]


    return render_to_response('root/index.html', {'tasks': tasks, 'leaves': leaves}, context_instance=RequestContext(request))
