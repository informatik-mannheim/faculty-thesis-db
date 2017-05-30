#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase

from website.forms import AssessorForm


class AssessorFormTests(TestCase):

    def setUp(self):
        pass

    def test_valid_if_everything_provided(self):
        data = {'first_name': "Horst",
                'last_name': "Schneider",
                'email': "test@example.com"}

        form = AssessorForm(data)
        form.full_clean()

        self.assertTrue(form.is_valid())

        assessor = form.cleaned_data["assessor"]

        self.assertEqual(data["first_name"], assessor.first_name)
        self.assertEqual(data["last_name"], assessor.last_name)
        self.assertEqual(data["email"], assessor.email)

    def test_valid_if_nothing_provided(self):
        data = {}

        form = AssessorForm(data)
        form.full_clean()

        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data["assessor"])

    def test_invalid_if_only_first_name_provided(self):
        data = {'first_name': "Horst"}

        form = AssessorForm(data)
        form.full_clean()

        self.assertFalse(form.is_valid())
        self.assertIn('Zweitkorrektor unvollständig', form.non_field_errors())
        self.assertTrue('assessor' not in form.cleaned_data)

    def test_invalid_if_only_last_name_provided(self):
        data = {'last_name': "Schneider"}

        form = AssessorForm(data)
        form.full_clean()

        self.assertFalse(form.is_valid())
        self.assertIn('Zweitkorrektor unvollständig', form.non_field_errors())
        self.assertTrue('assessor' not in form.cleaned_data)

    def test_invalid_if_only_email_provided(self):
        data = {'email': "test@example.com"}

        form = AssessorForm(data)
        form.full_clean()

        self.assertFalse(form.is_valid())
        self.assertIn('Zweitkorrektor unvollständig', form.non_field_errors())
        self.assertTrue('assessor' not in form.cleaned_data)
