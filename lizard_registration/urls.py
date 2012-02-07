# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.contrib import admin

from lizard_ui.urls import debugmode_urlpatterns

admin.autodiscover()

urlpatterns = patterns(
    '',

    (r'^admin/', include(admin.site.urls)),
    url(r'^$', 'lizard_registration.views.users_table_view',
        name="users_table_view"),
    url(r'^activate_user/(?P<activation_key>\w+)/$',
        'lizard_registration.views.activate_user_account',
        name="activate_user_account"),
    url(r'^activation/done/$', 'lizard_registration.views.activation_done',
        name="activation_done"),
    url(r'^userform/$', 'lizard_registration.views.create_user_form',
        name="create_user_form"),
    url(r'^updateuser/(?P<user_id>\d+)/$',
        'lizard_registration.views.update_user_form',
        name="update_user_form"),
    )
urlpatterns += debugmode_urlpatterns()
