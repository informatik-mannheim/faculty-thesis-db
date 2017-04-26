#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.utils import setup_test_environment

from datetime import datetime
from website.forms import ProlongationForm


setup_test_environment()


class FormProlongationTests(TestCase):

    def test_validate_prolongation_date_before_due_date(self):
        """Prolongation date must be > due_date"""
        data = {
            'prolongation_date': datetime(2020, 2, 1),
            'due_date': datetime(2020, 3, 1),
            'reason': 'I got a reason',
            'weeks': 4,

        }

        self.assertFalse(ProlongationForm(data).is_valid())

    def test_validate_prolongation_date_on_due_date(self):
        """Prolongation date must be > due_date"""
        data = {
            'prolongation_date': datetime(2020, 3, 1),
            'due_date': datetime(2020, 3, 1),
            'reason': 'I got a reason',
            'weeks': 4,

        }

        form = ProlongationForm(data)

        self.assertFalse(form.is_valid())
        self.assertIn('prolongation_date', form.errors)

    def test_validate_empty_reason(self):
        """A prolongation reason must be provided"""
        data = {
            'prolongation_date': datetime(2020, 4, 1),
            'due_date': datetime(2020, 3, 1),
            'reason': '',
            'weeks': 4,

        }

        form = ProlongationForm(data)

        self.assertFalse(form.is_valid())
        self.assertIn('reason', form.errors)

    def test_validate_no_weeks(self):
        """Weeks must be within range 1 - 99"""
        data = {
            'prolongation_date': datetime(2020, 4, 1),
            'due_date': datetime(2020, 3, 1),
            'reason': 'A very good reason',
            'weeks': 0,

        }

        form = ProlongationForm(data)

        self.assertFalse(form.is_valid())
        self.assertIn('weeks', form.errors)

    def test_validate_too_many_weeks(self):
        """Weeks must be within range 1 - 99"""
        data = {
            'prolongation_date': datetime(2020, 4, 1),
            'due_date': datetime(2020, 3, 1),
            'reason': 'A very good reason',
            'weeks': 100,

        }

        form = ProlongationForm(data)

        self.assertFalse(form.is_valid())
        self.assertIn('weeks', form.errors)
