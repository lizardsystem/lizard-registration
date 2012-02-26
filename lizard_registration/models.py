# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# from django.db import models

# Create your models here.

from django.db import models

from django.contrib.auth.models import User


class Organisation(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=256,
                                    blank=True, null=True)

    def __unicode__(self):
        return self.name


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    organisation = models.ForeignKey(Organisation)

    def __unicode__(self):
        return "%s %s" % (self.user.username,
                          self.organisation.name)


class UserContextStore(models.Model):
    """
        Store for context for users
    """
    user = models.OneToOneField(
        User
    )
    context = models.TextField(null=True, blank=True,
                           help_text='store for context')



class SessionContextStore(models.Model):
    """
        Store for context for users with a IPrange (these are shared accounts). Store them with the session id
    """
    user = models.ForeignKey(
        User
    )
    session_key = models.CharField(max_length=40, unique=True,
                                     blank=True, null=True)
    context = models.TextField(null=True, blank=True,
                                help_text='store for context')


class IPrangeLogin(models.Model):
    """
    IP addresses and IP ranges used for the automatic login function
    """
    user = models.ForeignKey(
        User
    )

    ipadres = models.IPAddressField()

    created_on = models.DateField(auto_now=True)

    class Meta:
        ordering = ['user', 'ipadres']

    def __unicode__(self):
        return u'%s: %s' % (self.ipadres, self.user.get_full_name())
