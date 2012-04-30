from django.conf.urls import patterns, include, url
from django.conf import settings
import tasks.urls
from django.contrib import admin
import root.views
import leaves.urls


admin.autodiscover()

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),

    # Django commenting system
    (r'^comments/', include('django.contrib.comments.urls')),

    # Login and logout
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'registration/logout.html'}),


    url(r'^tasks/', include(tasks.urls)),
    url(r'^leaves/', include(leaves.urls)),
    url(r'^$', root.views.index),
)

# Static files to be displayed for deployment server
urlpatterns += patterns('',
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
                    'document_root': settings.STATIC_ROOT,
                    'show_indexes': True
    })
)
