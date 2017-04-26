#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.utils import setup_test_environment

from datetime import datetime, date, timedelta

from website.forms import ProlongationForm
from website.models import Thesis


setup_test_environment()


class FormProlongationTests(TestCase):

    def test_sets_prolongation_date_as_due_date(self):
        """Should set due_date to either due_date or prolongation_date,
        depending on whether the thesis has been prolonged"""
        thesis = Thesis(
            begin_date=date(2018, 1, 1),
            due_date=date(2018, 3, 30),
            prolongation_date=date(2018, 4, 30),
            status=Thesis.PROLONGED)

        form = ProlongationForm.initialize_from(thesis)

        self.assertEqual(thesis.prolongation_date, form.initial["due_date"])
        self.assertEqual(thesis.prolongation_date + timedelta(30),
                         form.initial["prolongation_date"])

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
