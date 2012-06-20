# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt
# -*- coding: utf-8 -*-
"""
vss admin provides interface to:
- create a user profile
- define a organisation
"""
from django.contrib import admin
from lizard_registration.models import UserProfile
from lizard_registration.models import Organisation
from lizard_registration.models import IPrangeLogin
from lizard_registration.models import SessionContextStore
from lizard_registration.models import UserContextStore

class UserProfileAdmin(admin.ModelAdmin):
    """"""
    list_display = (
        'user',
        'organisation')
    list_filter = ('organisation',)


class OrganisationAdmin(admin.ModelAdmin):
    """"""
    model = Organisation

class SessionContextStoreAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'session_key')

class UserContextStoreAdmin(admin.ModelAdmin):
    list_display = (
        'user',)

class IPrangeLoginAdmin(admin.ModelAdmin):
    list_display = ['ipadres', 'user', 'password']
    filter = ['user']
    search = ['ipadres']

admin.site.register(UserContextStore, UserContextStoreAdmin)
admin.site.register(SessionContextStore, SessionContextStoreAdmin)
admin.site.register(IPrangeLogin, IPrangeLoginAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Organisation, OrganisationAdmin)
