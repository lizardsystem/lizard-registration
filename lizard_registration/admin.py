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


class UserProfileAdmin(admin.ModelAdmin):
    """"""
    list_display = (
        'user',
        'organisation')
    list_filter = ('organisation',)


class OrganisationAdmin(admin.ModelAdmin):
    """"""
    model = Organisation


class IPrangeLoginAdmin(admin.ModelAdmin):
    list_display = ['ipadres', 'user']
    filter = ['user']
    search = ['ipadres']


admin.site.register(IPrangeLogin, IPrangeLoginAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Organisation, OrganisationAdmin)
