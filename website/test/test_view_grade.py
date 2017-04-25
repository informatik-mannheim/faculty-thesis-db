#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse

from datetime import date, datetime
from decimal import Decimal

import uuid

from website.models import *


setup_test_environment()


class ViewGradeTests(TestCase):

    def setUp(self):
        user = User(username="prof", password="pass", initials="PPP")
        user.save()

        self.student = Student(
            id=123456, first_name="Larry", last_name="Langzeitstudent")
        self.assessor = Assessor(
            first_name="Max", last_name="Mustermann", email="mm@example.com")
        self.supervisor = Supervisor(
            first_name="Peter", last_name="Professpr", id=user.username)

        self.supervisor.save()
        self.student.save()
        self.assessor.save()

        self.client = Client()
        self.client.force_login(user)

    def test_cannot_grade_non_existent_thesis(self):
        response = self.client.get(reverse('grade', args=[uuid.uuid4()]))

        self.assertEqual(404, response.status_code)

    def test_initial_grade_form(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=datetime(2018, 1, 30),
                        due_date=datetime(2018, 6, 30))

        thesis.save()

        response = self.client.get(
            reverse('grade', args=[thesis.surrogate_key]))

        initial_date = response.context["form"].initial["examination_date"]

        self.assertEqual(200, response.status_code)
        self.assertEqual(datetime.now().date(), initial_date)

    def test_can_grade_thesis_with_restriction_note(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=datetime(2018, 1, 30),
                        due_date=datetime(2018, 6, 30))

        thesis.save()

        post_data = {
            'restriction_note': True,
            'examination_date': date(2019, 3, 1),
            'grade': Decimal("1.2"),
            'handed_in_date': date(2019, 2, 1),

        }

        response = self.client.post(
            reverse('grade', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(302, response.status_code)

        thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

        self.assertEqual(Thesis.GRADED, thesis.status)
        self.assertEqual(Decimal("1.2"), thesis.grade)
        self.assertTrue(thesis.restriction_note)

    def test_can_grade_thesis_without_restriction_note(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=datetime(2018, 1, 30),
                        due_date=datetime(2018, 6, 30))

        thesis.save()

        post_data = {
            'restriction_note': False,
            'examination_date': date(2019, 3, 1),
            'grade': Decimal("1.2"),
            'handed_in_date': date(2019, 2, 1),

        }

        response = self.client.post(
            reverse('grade', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(302, response.status_code)

        thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

        self.assertEqual(Thesis.GRADED, thesis.status)
        self.assertEqual(Decimal("1.2"), thesis.grade)
        self.assertFalse(thesis.restriction_note)

    def test_can_not_grade_thesis_with_invalid_grade(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=datetime(2018, 1, 30),
                        due_date=datetime(2018, 6, 30))

        thesis.save()

        for grade in ["0.9", "0", "1.11", "4.3", "5.1"]:
            post_data = {
                'restriction_note': False,
                'examination_date': date(2019, 3, 1),
                'grade': Decimal(grade),
                'handed_in_date': date(2019, 2, 1),

            }

            response = self.client.post(
                reverse('grade', args=[thesis.surrogate_key]), post_data)

            self.assertEqual(200, response.status_code)
            self.assertFalse(response.context["form"].is_valid())
            self.assertIn('grade', response.context["form"].errors)

            thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

            self.assertEqual(Thesis.APPLIED, thesis.status)

    def test_can_not_grade_thesis_without_grade(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=datetime(2018, 1, 30),
                        due_date=datetime(2018, 6, 30))

        thesis.save()

        post_data = {
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

    def test_can_not_grade_thesis_without_examination_date(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=datetime(2018, 1, 30),
                        due_date=datetime(2018, 6, 30))

        thesis.save()

        post_data = {
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
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=datetime(2018, 1, 30),
                        due_date=datetime(2018, 6, 30))

        thesis.save()

        post_data = {
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
