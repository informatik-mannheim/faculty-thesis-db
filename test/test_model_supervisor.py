#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.test import TestCase

from website.models import *


class MockUser(object):

    def __init__(self):
        self.username = "p.maier"
        self.first_name = "Peter"
        self.last_name = "Maier"


class SupervisorModelTests(TestCase):

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

    def test_get_list_of_supervisors(self):
        """Fetch supervisors from LDAP and check that they were populated correctly.
        Assumption is that there will always be at least one professor.
        """
        supervisors = Supervisor.objects.fetch_supervisors_from_ldap()

        self.assertTrue(len(supervisors) > 0)

        sample = supervisors[0]

        self.assertTrue(len(sample.first_name) > 0)
        self.assertTrue(len(sample.last_name) > 0)
        self.assertEqual(3, len(sample.initials))
