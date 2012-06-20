# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Permission
from django.db.models.query_utils import Q


def db_table_exists(table, cursor=None):
    """
    Check existence of table.

    from https://gist.github.com/527113/
    """
    try:
        if not cursor:
            from django.db import connection
            cursor = connection.cursor()
        if not cursor:
            raise Exception
        table_names = connection.introspection.get_table_list(cursor)
    except:
        raise Exception("unable to determine if the table '%s' exists" % table)
    else:
        return table in table_names


def auto_login(request):
    """
        automatically login user when coming from specified ipadresses
        defined adresses with a .0 at the end will be used for the complete range

        add this function to the pages with login buttons, for example:

                if not request.user.is_authenticated():
                    try:
                        auto_login(request)
                    except AttributeError:
                        pass

        if login fails, you get a AttributeError at /portal/
        'AnonymousUser' object has no attribute 'backend'
    """

    # TODO: EEKS WHY HERE?!
    from lizard_registration.models import IPrangeLogin

    matches = IPrangeLogin.objects.filter(ipadres=request.META.get('REMOTE_ADDR','?'))

    if matches.count() == 0:
        parts = request.META.get('REMOTE_ADDR','?').split('.')
        ip_range = '.'.join(parts[0:3]) + '.0'
        matches = IPrangeLogin.objects.filter(ipadres=ip_range)
    if matches.count() > 0:
        match = matches[0]
        #todo: change password part of this function
        # Needed for the 'backend' property, see
        # https://docs.djangoproject.com/en/dev/topics/auth/
        user = authenticate(username=match.user.username, password=match.password)
        login(request, user)
        return user

    return None


def get_user_permissions_overall(user, content_type_name=None, as_list= False):
    """
        get overall permissions, including links through lizard_security

        user: django.contrib.auth.models.User object
        content_type_name: (optional) extra filter option
        as_list: (optional, default False) return list with tuples with codename and name
    """
    permissions = Permission.objects.filter(Q(user=user)|Q(group__user=user)|Q(group__permissionmapper__user_group__members=user))

    if content_type_name:
        permissions = permissions.filter(content_type__name=content_type_name)

    permissions = permissions.distinct()

    if as_list:
        return [(p.codename, p.name) for p in permissions]
    else:
        return permissions


