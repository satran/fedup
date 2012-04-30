from django.conf.urls import patterns, include, url

urlpatterns = patterns('tasks.views',
    url(r'^$', 'read_create'),
    url(r'^(?P<task_id>\d+)$', 'read_update'),
    url(r'^(?P<filter_type>\w+)/(?P<filter_id>\d+)/$', 'read_create'),
    url(r'^date/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)$', 'filter_date'),
)
