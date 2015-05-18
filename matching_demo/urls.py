from django.conf.urls import patterns, include, url
from django.contrib import admin

import matcher.views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'matching_demo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', matcher.views.map),
    url(r'^segments', matcher.views.segments, name='segments_json'),
    url(r'^admin/', include(admin.site.urls)),
)
