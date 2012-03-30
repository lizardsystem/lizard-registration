# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin

from lizard_registration.api.views import ContextView

admin.autodiscover()

NAME_PREFIX = 'lizard_registration_api_'

urlpatterns = patterns(
    '',
    url(r'^context/$',
        ContextView.as_view(),
        name=NAME_PREFIX + 'context'),
)
