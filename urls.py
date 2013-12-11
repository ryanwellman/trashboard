from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django import template
from django.conf import settings

admin.autodiscover()

template.add_to_builtins('django.contrib.staticfiles.templatetags.staticfiles')

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'trashboard.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/?', include(admin.site.urls)),
    url(r'^(?P<agreement_id>\d+)$', 'views.draw_container', name='draw_container'),
    url(r'^$', 'views.draw_container', name='draw_container2'),
    url(r'^package/?', 'views.Packages', name='package'),
    url(r'^purchase/?', 'views.Purchase', name='purchase'),
    url(r'^initial_info/', 'views.InitialInfo', name='initial_info'),
    url(r'^test/?$', 'views.draw_test', name='draw_test'),
    url(r'^json/?$', 'views.serve_json', name='serve_json'),
    url(r'^json2/(?P<agreement_id>\d+)$', 'views.dyn_json', name='dyn_json2'),
    url(r'^json2/?$', 'views.dyn_json', name='dyn_json'),
    url(r'^json3/?$', 'views.test_json', name='test_json'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
