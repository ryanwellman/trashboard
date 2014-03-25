from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django import template
from django.conf import settings
from agreement.agreement_edit_controller import AgreementEditController
admin.autodiscover()

template.add_to_builtins('django.contrib.staticfiles.templatetags.staticfiles')

urlpatterns = patterns('',
    # Examples:
    url(r'^login/$', 'org.views.login', name='login'),
    url(r'^logout/$', 'org.views.logout', name='logout'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/?', include(admin.site.urls)),
    url(r'create/$', 'views.create_and_redirect', name='create_and_redirect'),
    url(r'^(?P<agreement_id>\d+)$', AgreementEditController.as_controller(), name='draw_container'),
    url(r'^json/(?P<agreement_id>\d+)$', 'views.dyn_json', name='dyn_json2'),
    url(r'^json/?$', 'views.dyn_json', name='dyn_json'),
    url(r'credit_review/$', 'agreement.views.CreditReview', name='credit_review'),
    url(r'^$', 'views.Index', name='index'),
    url(r'bypass/$', 'agreement.views.BypassUpfrontAuthorization', name='bypass'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
