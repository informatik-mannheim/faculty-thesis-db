#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.test import TestCase

from website.forms import SupervisorsForm
from website.models import Supervisor


class SupervisorsFormTests(TestCase):

    def test_form_contains_all_supervisors_from_ldap(self):
        form = SupervisorsForm()

        supervisor_choices = form.fields['supervisors'].choices

        all_supervisors = Supervisor.objects.fetch_supervisors_from_ldap()
        all_supervisors = [supervisor.id for supervisor in all_supervisors]

        for supervisor in supervisor_choices:
            self.assertIn(supervisor[0], all_supervisors)

    def test_form_validation_success(self):
        initial_form = SupervisorsForm()
        supervisor = initial_form.fields['supervisors'].choices[0]

        form = SupervisorsForm({"supervisors": supervisor[0]})

        self.assertTrue(form.is_valid())

    def test_form_validation_failure(self):
        form = SupervisorsForm({"supervisors": "not.existant"})

        self.assertFalse(form.is_valid())
