# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

# Create your views here.
import logging
import random
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor
from django.utils.http import base36_to_int
from django.utils.http import int_to_base36
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from registration.models import RegistrationProfile
from lizard_registration.manager_forms import CreateUserForm
from lizard_registration.manager_forms import UpdateUserForm
from lizard_registration.manager_forms import UserSetPasswordForm
from lizard_registration.models import UserProfile


SHA1_RE = re.compile('^[a-f0-9]{40}$')

logger = logging.getLogger(__name__)

DEFAULT_USER_GROUP = "raadpleger"

def activation_done(request,
                    template_name='registration/activation_complete.html',
                    current_app=None, extra_context=None):
    return render_to_response('registration/activation_complete.html')


@csrf_exempt
def activate_user_account(request, activation_key=None):
    """
    Activates user throuth is_active=True using activation_key.

    Provide a form for entering a new password and
    checks the hash in hidden fields.

    """
    kwargs = {'token': '', 'uid_base': ''}

    if request.method == 'POST':
        try:
            uid_int = base36_to_int(request.POST.get('uid_base'))
            user = User.objects.get(id=uid_int)
        except (ValueError, User.DoesNotExist):
            logger.debug('UNKNOWN uid %s on activate_user_account.')
            raise Http404
        token = request.POST.get('token')
        if default_token_generator.check_token(user, token) == False:
            logger.debug('UNKNOWN token %s on activate_user_account.')
            raise Http404
        form = UserSetPasswordForm(user, request.POST, **kwargs)
        if form.is_valid():
            form.save()
            return render_to_response('registration/activation_complete.html')
        else:
            kwargs['token'] = default_token_generator.make_token(user)
            kwargs['uid_base'] = int_to_base36(user.id)
    else:
        user = activate_user(activation_key)
        if user:
            kwargs['token'] = default_token_generator.make_token(user)
            kwargs['uid_base'] = int_to_base36(user.id)
        else:
            logger.debug('UNKNOWN activation_key %s on activate_user_account.',
                         activation_key)
            raise Http404

    template_name = 'registration/password_reset_confirm.html'
    context = {'form': UserSetPasswordForm(None, **kwargs)}
    return render_to_response(template_name, context)


def merge_user_groups(user):
    """Merge manager's group with memeber's group."""
    member_groups = list(user.user_group_memberships.exclude(
            name__endswith=DEFAULT_USER_GROUP).values_list('id', flat=True))
    manager_groups = list(user.managed_user_groups.exclude(
            name__endswith=DEFAULT_USER_GROUP).values_list('id', flat=True))
    for group in manager_groups:
        if group not in member_groups:
            member_groups.append(group)
    return member_groups


def user_data(user_id):
    """Returns user data."""
    user = User.objects.get(id=user_id)
    user_profile = UserProfile.objects.get(user__id=user.id)
    user_groups = merge_user_groups(user)
    data = {'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_active': user.is_active,
            'organisation': user_profile.organisation.name,
            'groups': list(user_groups)}
    return data


def deactivate_registrationprofile(user):
    """
    Sets activation_key in RegistrationProfile of user
    on 'DEACTIVATE'.
    """
    registration_profiles = RegistrationProfile.objects.filter(user=user)
    if registration_profiles.exists():
        registration_profile = registration_profiles[0]
        registration_profile.activation_key = 'DEACTIVATED'
        registration_profile.save()


def has_helpdesk_group(user):
    """Return true is the user is a member of helpdesk usergroup."""
    helpdesk_groups = user.user_group_memberships.filter(name__endswith='helpdesk')
    if helpdesk_groups.exists():
        return True
    return False


def update_user(form, user_id):
    """Update user, registration profile and user groups memeberships."""
    user = User.objects.get(id=user_id)
    user.username = form.cleaned_data['username']
    user.first_name = form.cleaned_data['first_name']
    user.last_name = form.cleaned_data['last_name']
    user.email = form.cleaned_data['email']
    user.is_active = form.cleaned_data['is_active']

    if form.cleaned_data['is_active'] == False:
        deactivate_registrationprofile(user)

    user.managed_user_groups.clear()
    user.user_group_memberships.clear()
    user.user_group_memberships = form.cleaned_data['groups']
    user.save()
    if has_helpdesk_group(user):
        user.managed_user_groups = form.cleaned_data['groups']
        user.save()


def raadpleger_group(manager):
    """Return user_group 'raadpleger'. The group has to be 
    assigned to every new user."""
    group = manager.managed_user_groups.filter(
            name__endswith=DEFAULT_USER_GROUP)
    if group.exists():
        return group


def create_user(form, manager):
    """
    Creates user account including user profile,
    user groups.
    """
    user = User(
        username=form.cleaned_data['username'],
        first_name=form.cleaned_data['first_name'],
        last_name=form.cleaned_data['last_name'],
        email=form.cleaned_data['email'])
    user.save()
    user.user_group_memberships = form.cleaned_data['groups']
    user.user_group_memberships = raadpleger_group(manager)
    user.save()
    if has_helpdesk_group(user):
        user.managed_user_groups = form.cleaned_data['groups']
        user.managed_user_groups = raadpleger_group(manager)
        user.save()
    manager_profile = UserProfile.objects.get(user=manager)
    user_profile = UserProfile(
        user=user,
        organisation=manager_profile.organisation)
    user_profile.save()
    return user


def create_activation_key(user):
    salt = sha_constructor(str(random.random())).hexdigest()[:5]
    username = user.username
    if isinstance(username, unicode):
        username = username.encode('utf-8')
    return sha_constructor(salt + username).hexdigest()


def send_activation_email(user, registration_profile, domain):
    ctx_dict = {'activation_key': registration_profile.activation_key,
                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                'domain': domain,
                'user_full_name': user.get_full_name,
                'username': user.username}
    subject = render_to_string('registration/activation_email_subject.txt',
                               ctx_dict)
    subject = ''.join(subject.splitlines())
    message = render_to_string('registration/activation_email.txt',
                               ctx_dict)
    user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)


def create_inactive_user(form, manager, domain):
    """Create an inactive user and send an activation email."""
    new_user = create_user(form, manager)
    new_user.is_active = False
    new_user.save()
    registration_profile = RegistrationProfile.objects.create_profile(new_user)
    send_activation_email(new_user, registration_profile, domain)
create_inactive_user = transaction.commit_on_success(create_inactive_user)


def remove_registration_profile(user):
    """Removes RegistrationProfile of the user."""
    profiles = RegistrationProfile.objects.filter(user=user)
    if profiles.exists():
        profiles.delete()


def activate_user(activation_key):
        """
        Validate an activation key and activate the corresponding
        ``User`` if valid.
        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                with transaction.commit_on_success():
                    profile = RegistrationProfile.objects.get(
                        activation_key=activation_key)
                    user = profile.user
                    user.is_active = True
                    user.save()
                    profile.activation_key = RegistrationProfile.ACTIVATED
                    profile.save()
                return user
            except RegistrationProfile.DoesNotExist:
                logger.error(
                    "On activate_user, activation key %s does not exist",
                    activation_key)
                return False
            except Exception as ex:
                logger.error(','.join(map(str, ex.args)))
                return False


def reactivate_user(user_id, domain):
    """
    Removes user's registration profile.
    Creates a new registration profile
    Sends a activation email.
    """
    try:
        with transaction.commit_on_success():
            user = User.objects.get(id=user_id)
            remove_registration_profile(user)
            registration_profile = RegistrationProfile.objects.create_profile(
                user)
            send_activation_email(user, registration_profile, domain)
    except Exception as ex:
            logger.error(','.join(map(str, ex.args)))


def is_manager(user):
    """Return true if the user has usergroups."""
    managed_groups = user.managed_user_groups.all()
    if len(managed_groups) > 0:
        return True
    return False


@csrf_exempt
def update_user_form(request, user_id=None):
    """Provides a form to change user account."""
    manager = User.objects.get(username=request.user)
    groups_queryset = manager.managed_user_groups.exclude(
        name__endswith=DEFAULT_USER_GROUP)
    kwargs = {'groups_queryset': groups_queryset, 'user_id': user_id}
    if not is_manager(manager):
        return render_to_response('403.html')

    if request.method == 'POST' and request.POST.get("action") == "Cancel":
        return HttpResponseRedirect('/manager/')

    if request.method == 'POST':
        form = UpdateUserForm(request.POST, **kwargs)
        if form.is_valid():
            if request.POST.get("action") == "Send activation email":
                domain = request.META.get('HTTP_HOST', 'unknown')
                reactivate_user(user_id, domain)
            else:
                update_user(form, user_id)
            return HttpResponseRedirect('/manager/')
    else:

        data = user_data(user_id)
        form = UpdateUserForm(data, **kwargs)
    return render_to_response('update_user_form.html',
                              {'form': form})


@csrf_exempt
def create_user_form(request):
    """Provides a form to create user"""

    manager = User.objects.get(username=request.user)
    groups_queryset = manager.managed_user_groups.exclude(
        name__endswith=DEFAULT_USER_GROUP)
    kwargs = {'groups_queryset': groups_queryset}
    if not is_manager(manager):
        return render_to_response('403.html')

    if request.method == 'POST' and request.POST.get("action") == "Cancel":
        return HttpResponseRedirect('/manager/')

    if request.method == 'POST':
        form = CreateUserForm(request.POST, **kwargs)
        if form.is_valid():
            domain = request.META.get('HTTP_HOST', 'unknown')
            create_inactive_user(form, manager, domain)
            return HttpResponseRedirect('/manager/')
    else:
        form = CreateUserForm(**kwargs)

    return render_to_response('create_user_form.html',
                              {'form': form})


@csrf_exempt
def users_table_view(request):
    """Provides users related to organisation of current manager."""
    users = User.objects.filter(username=request.user)
    manager = None
    if users.exists():
        manager = users[0]
    else:
        return HttpResponseRedirect('http://%s' % request.META.get('HTTP_HOST',
                                                                  'unknown'))

    if not is_manager(manager):
        return render_to_response('403.html')

    try:
        userprofile = UserProfile.objects.get(user=manager)
    except UserProfile.DoesNotExist as ex:
        return render_to_response('registration/error.html',
                                  {'type': 'Configuration Error',
                                   'component': 'UserProfile',
                                   'message': ','.join(map(str, ex.args)),
                                   'username': manager.username})

    managed_groups = manager.managed_user_groups.all()
    managed_users = []
    if managed_groups.exists():
        managed_users = UserProfile.objects.filter(
            organisation=userprofile.organisation)
        managed_users = list(managed_users.exclude(user__is_superuser=True))
    return render_to_response('users_table_view.html',
                              {'managed_users': managed_users})
