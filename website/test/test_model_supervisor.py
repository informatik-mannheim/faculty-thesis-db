#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.utils import setup_test_environment

from website.models import *


setup_test_environment()


class MockUser(object):

    def __init__(self):
        self.username = "p.maier"
        self.first_name = "Peter"
        self.last_name = "Maier"


class SupervisorModelTests(TestCase):

    def setUp(self):
        pass

    def test_creation_from_user_without_initials(self):
        user = MockUser()
        supervisor = Supervisor.from_user(user)

        self.assertEqual(user.username, supervisor.id)
        self.assertEqual(user.first_name, supervisor.first_name)
        self.assertEqual(user.last_name, supervisor.last_name)
        self.assertEqual("", supervisor.initials)

    def test_creation_from_user_with_initials(self):
        user = MockUser()
        user.initials = "ABC"
        supervisor = Supervisor.from_user(user)

        self.assertEqual(user.username, supervisor.id)
        self.assertEqual(user.first_name, supervisor.first_name)
        self.assertEqual(user.last_name, supervisor.last_name)
        self.assertEqual(user.initials, supervisor.initials)
