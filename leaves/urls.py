from django.conf.urls import patterns, include, url

urlpatterns = patterns('leaves.views',
    url(r'^$', 'read_create'),
    url(r'^(?P<leave_id>\d+)$', 'read_update'),
)
