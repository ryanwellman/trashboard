from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'trashboard.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'views.draw_container', name='draw_container'),
    url(r'^package/', 'views.Package', name='package'),
    url(r'^test$', 'views.draw_test', name='draw_test'),
    url(r'^json$', 'views.serve_json', name='serve_json'),
)
