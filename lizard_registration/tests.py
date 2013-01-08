# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.test import TestCase
from lizard_registration.views import create_activation_key
from lizard_registration import utils

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

class TestGetRemoteIp(TestCase):
    def test_returns_remote_ip(self):
        remote_ip = utils.get_remote_ip({
                'REMOTE_ADDR': '127.0.0.1'})
        self.assertEquals(remote_ip, '127.0.0.1')

    def test_last_external_ip_from_list(self):
        remote_ip = utils.get_remote_ip({
                'HTTP_X_FORWARDED_FOR':
                    "12.123.21.11, 126.100.100.100, 10.100.20.10"})
        self.assertEquals(remote_ip, '126.100.100.100')
