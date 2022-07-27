#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.urls import reverse

from datetime import date
from decimal import Decimal
import uuid

from website.test.test import LoggedInTestCase, ThesisStub
from website.models import *


class ViewGradeTests(LoggedInTestCase):

    def test_cannot_grade_non_existent_thesis(self):
        response = self.client.get(reverse('grade', args=[uuid.uuid4()]))

        self.assertEqual(404, response.status_code)

    def test_initial_grade_form(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.save()

        response = self.client.get(
            reverse('grade', args=[thesis.surrogate_key]))
        initial_date = response.context["form"].initial["examination_date"]

        self.assertEqual(200, response.status_code)
        self.assertEqual(thesis.due_date, initial_date)

    def test_can_grade_thesis_with_restriction_note(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.save()

        post_data = {
            'assessor': thesis.assessor,
            'restriction_note': True,
            'examination_date': date(2019, 3, 1),
            'grade': Decimal("1.2"),
            'assessor_grade': Decimal("1.5"),
            'handed_in_date': date(2019, 2, 1)
        }

        response = self.client.post(
            reverse('grade', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(302, response.status_code)

        thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

        self.assertEqual(Thesis.GRADED, thesis.status)
        self.assertEqual(Decimal("1.2"), thesis.grade)
        self.assertEqual(Decimal("1.5"), thesis.assessor_grade)
        self.assertTrue(thesis.restriction_note)

    def test_can_grade_thesis_without_restriction_note(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.save()

        post_data = {
            'assessor': thesis.assessor,
            'restriction_note': False,
            'examination_date': date(2019, 3, 1),
            'grade': Decimal("1.2"),
            'assessor_grade': Decimal("1.5"),
            'handed_in_date': date(2019, 2, 1),
        }

        response = self.client.post(
            reverse('grade', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(302, response.status_code)

        thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

        self.assertEqual(Thesis.GRADED, thesis.status)
        self.assertEqual(Decimal("1.2"), thesis.grade)
        self.assertEqual(Decimal("1.5"), thesis.assessor_grade)
        self.assertFalse(thesis.restriction_note)

    def test_can_not_grade_thesis_with_invalid_grade(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.save()

        for grade in ["0.9", "4.1", "4.9", "5.1", "5.11"]:
            post_data = {
                'assessor': thesis.assessor,
                'restriction_note': False,
                'examination_date': date(2019, 3, 1),
                'grade': Decimal(grade),
                'assessor_grade': Decimal("1.0"),
                'handed_in_date': date(2019, 2, 1),

            }

            response = self.client.post(
                reverse('grade', args=[thesis.surrogate_key]), post_data)

            self.assertEqual(200, response.status_code)
            self.assertFalse(response.context["form"].is_valid())
            self.assertIn('grade', response.context["form"].errors)

            thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

            self.assertEqual(Thesis.APPLIED, thesis.status)

    def test_can_not_grade_thesis_with_invalid_assessor_grade(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.save()

        for assessor_grade in ["0.9", "4.1", "4.9", "5.1", "5.11"]:
            post_data = {
                'assessor': thesis.assessor,
                'restriction_note': False,
                'examination_date': date(2019, 3, 1),
                'grade': Decimal("1.0"),
                'assessor_grade': Decimal(assessor_grade),
                'handed_in_date': date(2019, 2, 1),

            }

            response = self.client.post(
                reverse('grade', args=[thesis.surrogate_key]), post_data)

            self.assertEqual(200, response.status_code)
            self.assertFalse(response.context["form"].is_valid())
            self.assertIn('assessor_grade', response.context["form"].errors)

            thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

            self.assertEqual(Thesis.APPLIED, thesis.status)

    def test_can_not_grade_thesis_without_grade(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.save()

        post_data = {
            'assessor': thesis.assessor,
            'restriction_note': False,
            'examination_date': date(2019, 3, 1),
            'handed_in_date': date(2019, 2, 1),
        }

        response = self.client.post(
            reverse('grade', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn('grade', response.context["form"].errors)

        thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

        self.assertEqual(Thesis.APPLIED, thesis.status)

    def test_cannpt_grade_assessor_grade_without_assessor(self):
        thesis = ThesisStub.applied(self.supervisor)
        thesis.assessor = None

        thesis.save()

        post_data = {
            'assessor': '',
            'restriction_note': False,
            'examination_date': date(2019, 3, 1),
            'grade': Decimal("1.2"),
            'assessor_grade': Decimal("1.2"),
            'handed_in_date': date(2019, 2, 1),
        }

        response = self.client.post(
            reverse('grade', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(302, response.status_code)

        thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

        self.assertEqual(Thesis.GRADED, thesis.status)
        self.assertEqual(Decimal("1.2"), thesis.grade)
        self.assertEqual(None, thesis.assessor_grade)
        self.assertEqual(None, thesis.assessor)
        self.assertFalse(thesis.restriction_note)

    def test_cannot_omit_assessor_grade_with_assessor(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.save()

        post_data = {
            'assessor': thesis.assessor,
            'restriction_note': False,
            'examination_date': date(2019, 3, 1),
            'handed_in_date': date(2019, 2, 1),
            'grade': Decimal('1.2'),
        }

        response = self.client.post(
            reverse('grade', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn('assessor_grade', response.context["form"].errors)

        thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

        self.assertEqual(Thesis.APPLIED, thesis.status)

    def test_can_not_grade_thesis_without_examination_date(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.save()

        post_data = {
            'assessor': thesis.assessor,
            'restriction_note': False,
            'grade': Decimal("1.2"),
            'handed_in_date': date(2019, 2, 1),
        }

        response = self.client.post(
            reverse('grade', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn('examination_date', response.context["form"].errors)

        thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

        self.assertEqual(Thesis.APPLIED, thesis.status)

    def test_can_not_grade_thesis_without_handed_in_date(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.save()

        post_data = {
            'assessor': thesis.assessor,
            'restriction_note': False,
            'grade': Decimal("1.2"),
            'examination_date': date(2019, 2, 1),
        }

        response = self.client.post(
            reverse('grade', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["form"].is_valid())
        self.assertIn('handed_in_date', response.context["form"].errors)

        thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

        self.assertEqual(Thesis.APPLIED, thesis.status)
