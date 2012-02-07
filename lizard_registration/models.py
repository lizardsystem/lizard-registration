# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# from django.db import models

# Create your models here.

from django.db import models

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from lizard_registration.utils import db_table_exists


if db_table_exists('django_content_type'):
    content_type = ContentType.objects.get(app_label='auth', model='user')
else:
    content_type = None

if content_type:
    perms = [
        ['is_analyst', 'Is analyst'],
        ['is_veldmedewerker', 'Is veldmedewerker'],
        ['is_beleidsmaker', 'Is beleidsmaker'],
        ['is_funct_beheerder', 'Is functioneel beheerder'],
        ['is_helpdesk', 'Is helpdesk medewerker'],
        ['is_internegebruiker', 'Is interne gebruiker'],
        ['is_gereg_user', 'Is geregistreerde gebruiker'],
        ['is_extern_user', 'Is externe gebruiker'],
        ['is_appl_beheerder', 'Is applicatie beheerder'],
        ['is_centr_func_beheerder', 'Is centrale functioneel beheerder'],
    ]

    for perm in perms:
        Permission.objects.get_or_create(codename=perm[0],
                                         name=perm[1],
                                         content_type=content_type)


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
