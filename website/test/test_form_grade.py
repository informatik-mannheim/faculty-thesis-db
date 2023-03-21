#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.test import TestCase

from datetime import date
from decimal import Decimal

from website.models import Thesis, Assessor
from website.forms import GradeForm


class GradeFormTests(TestCase):

    def setUp(self):
        self.assessor = Assessor(first_name="Peter", last_name="Müller")
        self.assessor.save()

    def test_initilization(self):
        thesis = Thesis(title="Some title",
                        assessor=self.assessor,
                        status=Thesis.PROLONGED,
                        restriction_note=True,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30))

        form = GradeForm.initialize_from(thesis)

        self.assertEqual(thesis.restriction_note, form["restriction_note"].value())
        self.assertEqual(thesis.due_date, form["examination_date"].value())
        self.assertEqual(thesis.due_date, form["handed_in_date"].value())
        self.assertEqual(None, form["grade"].value())
        self.assertEqual(None, form["assessor_grade"].value())

    def test_initialization_with_grades(self):
        thesis = Thesis(title="Some title",
                        assessor=self.assessor,
                        status=Thesis.PROLONGED,
                        restriction_note=True,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        grade=1.0,
                        assessor_grade=1.0)

        form = GradeForm.initialize_from(thesis)

        self.assertEqual(1.0, form["grade"].value())
        self.assertEqual(1.0, form["assessor_grade"].value())

    def test_validate_grade(self):
        valid_grades = ["1.0", "1.1", "1.2", "2.0", "2.5",
                        "3.0", "3.9", "4.0", "5.0"]

        for grade in valid_grades:
            data = {
                'assessor': self.assessor,
                'grade': Decimal(grade),
                'assessor_grade': Decimal(grade),
                'restriction_note': True,
                'examination_date': date(2017, 3, 1),
                'handed_in_date': date(2017, 2, 1)
            }

            form = GradeForm(data)
            form.full_clean()

            self.assertTrue(form.is_valid())

    def test_validate_invalid_grades(self):
        invalid_grades = ["0.9", "1.01", "2.001", "4.1",
                          "4.5", "4.9", "5.1", "6", "10"]

        for grade in invalid_grades:
            data = {
                'assessor': self.assessor,
                'grade': Decimal(grade),
                'assessor_grade': 1.0,
                'restriction_note': True,
                'examination_date': date(2017, 1, 1),
                'handed_in_date': date(2017, 2, 1)
            }

            form = GradeForm(data)
            form.full_clean()

            self.assertFalse(form.is_valid())
            self.assertIn('grade', form.errors)

    def test_validate_invalid_assessor_grades(self):
        invalid_grades = ["0.9", "1.01", "2.001", "4.1",
                          "4.5", "4.9", "5.1", "6", "10"]

        for grade in invalid_grades:
            data = {
                'assessor': self.assessor,
                'grade': 1.0,
                'assessor_grade': Decimal(grade),
                'restriction_note': True,
                'examination_date': date(2017, 1, 1),
                'handed_in_date': date(2017, 2, 1)
            }

            form = GradeForm(data)
            form.full_clean()

            self.assertFalse(form.is_valid())
            self.assertIn('assessor_grade', form.errors)
