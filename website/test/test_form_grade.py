#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.utils import setup_test_environment

from datetime import datetime
from decimal import Decimal

from website.forms import GradeForm


setup_test_environment()


class GradeFormTests(TestCase):

    def setUp(self):
        pass

    def test_initials(self):
        form = GradeForm()
        self.assertEqual(False, form.fields["restriction_note"].initial)
        self.assertEqual(None, form.fields["grade"].initial)
        self.assertEqual(None, form.fields["examination_date"].initial)

    def test_validate_grade(self):
        valid_grades = ["1.0", "1.1", "1.2", "2.0", "2.5",
                        "3.0", "3.9", "4.0", "5.0"]

        for grade in valid_grades:
            data = {
                'grade': Decimal(grade),
                'restriction_note': True,
                'examination_date': datetime(2017, 3, 1).date(),
                'handed_in_date': datetime(2017, 2, 1).date()
            }

            form = GradeForm(data)
            form.full_clean()

            self.assertTrue(form.is_valid())

    def test_validate_invalid_grades(self):
        invalid_grades = ["0.9", "1.01", "2.001", "4.1",
                          "4.5", "4.9", "5.1", "6", "10"]

        for grade in invalid_grades:
            data = {
                'grade': Decimal(grade),
                'restriction_note': True,
                'examination_date': datetime(2017, 1, 1).date(),
                'handed_in_date': datetime(2017, 2, 1).date()
            }

            form = GradeForm(data)
            form.full_clean()

            self.assertFalse(form.is_valid())
