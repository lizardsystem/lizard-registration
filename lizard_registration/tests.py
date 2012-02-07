# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.test import TestCase
from lizard_registration.views import create_activation_key


class User(object):
    def __init__(self, username):
        self.username = username


class RegistrationTest(TestCase):
    def test_create_activation_key(self):
        """
        Expected not None and not empty string from
        create_activation_key(..) function.
        """
        user = User('test')
        key = create_activation_key(user)
        self.assertFalse(None, key)
        self.assertFalse("", key)


