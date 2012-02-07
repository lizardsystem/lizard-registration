# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.contrib.auth import login, authenticate



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
                    auto_login(request)
    """
    from lizard_registration.models import IPrangeLogin

    matches = IPrangeLogin.objects.filter(ipadres=request.META.get('REMOTE_ADDR','?'))

    if matches.count() == 0:
        parts = request.META.get('REMOTE_ADDR','?').split('.')
        ip_range = '.'.join(parts[0:3]) + '.0'
        matches = IPrangeLogin.objects.filter(ipadres=ip_range)
    if matches.count() > 0:
        match = matches[0]
        #todo: change password part of this function
        user = authenticate(username=match.user.username, password='kikker123')
        login(request, user)
        return user

    return None



