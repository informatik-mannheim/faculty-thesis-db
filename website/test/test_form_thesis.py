#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.utils import setup_test_environment

from datetime import date

from website.models import *
from website.forms import ThesisApplicationForm
from website.test.test import ThesisStub

setup_test_environment()


class FormThesisApplicationTests(TestCase):

    def test_validate_valid_form(self):
        """Minimum required data for a valid thesis is title,
        begin date and due date"""
        data = {
            'title': 'A title',
            'begin_date': date(2017, 1, 1),
            'due_date': date(2017, 3, 1)
        }

        form = ThesisApplicationForm(data)

        form.full_clean()

        self.assertTrue(form.is_valid())

    def testdue_date_must_be_after_begin_date(self):
        """Due date can not before begin date"""
        data = {
            'begin_date': date(2017, 1, 1),
            'due_date': date(2017, 3, 1)
        }

        form = ThesisApplicationForm(data)

        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_must_contain_begin_and_due_date(self):
        """Due date can not before begin date"""
        data = {
            'title': 'OK title'
        }

        form = ThesisApplicationForm(data)

        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)
        self.assertIn('begin_date', form.errors)

    def test_create_thesis_from_form(self):
        assessor = Assessor(
            first_name="Peter",
            last_name="Maier",
            email="m@example.com")

        supervisor = Supervisor(
            first_name="Max",
            last_name="Mustermann",
            id="mmuster")

        student = Student(
            id=123456,
            first_name="Larry",
            last_name="Langzeitstudent")

        data = {
            'begin_date': date(2020, 1, 1),
            'due_date': date(2020, 3, 1),
            'title': 'Some title',
            'external': True,
            'external_where': 'John Deere',
            'student_email': 'l.langzeit@example.com'

        }

        form = ThesisApplicationForm(data)

        created_thesis = form.create_thesis(assessor, supervisor, student)

        self.assertEqual(created_thesis.title, data["title"])
        self.assertEqual(created_thesis.begin_date, data["begin_date"])
        self.assertEqual(created_thesis.due_date, data["due_date"])
        self.assertEqual(created_thesis.assessor, assessor)
        self.assertEqual(created_thesis.supervisor, supervisor)
        self.assertEqual(created_thesis.student, student)
        self.assertEqual(created_thesis.external, data["external"])
        self.assertEqual(created_thesis.external_where, data["external_where"])
        self.assertEqual(created_thesis.student_contact, data["student_email"])

    def test_create_thesis_from_form_fill_missing_values_with_defaults(self):
        """Should set defaults for missing student_email,
        external, external_where, assessor"""
        supervisor = Supervisor(
            first_name="Max",
            last_name="Mustermann",
            id="mmuster")

        student = Student(
            id=123456,
            first_name="Larry",
            last_name="Langzeitstudent")

        data = {
            'begin_date': date(2020, 1, 1),
            'due_date': date(2020, 3, 1),
            'title': 'Some title',
        }

        form = ThesisApplicationForm(data)

        created_thesis = form.create_thesis(None, supervisor, student)

        self.assertEqual(created_thesis.title, data["title"])
        self.assertEqual(created_thesis.begin_date, data["begin_date"])
        self.assertEqual(created_thesis.due_date, data["due_date"])
        self.assertEqual(created_thesis.assessor, None)
        self.assertEqual(created_thesis.supervisor, supervisor)
        self.assertEqual(created_thesis.student, student)
        self.assertEqual(created_thesis.external, False)
        self.assertEqual(created_thesis.external_where, '')
        self.assertEqual(created_thesis.student_contact, student.email)

    def test_change_thesis(self):
        supervisor = Supervisor(
            first_name="Max",
            last_name="Mustermann",
            id="mmuster")

        supervisor.save()

        thesis = ThesisStub.applied(supervisor)
        thesis.save()

        data = {
            'begin_date': date(2021, 1, 1),
            'due_date': date(2021, 3, 1),
            'title': 'xxxrxxx',
            'external': not thesis.external,
            'external_where': '',
            'student_email': 'l.langzeit@example.com'
        }

        form = ThesisApplicationForm(data)
        form.full_clean()

        changed_thesis = form.change_thesis(thesis, assessor=None)

        self.assertEqual(changed_thesis.title, data["title"])
        self.assertEqual(changed_thesis.begin_date, data["begin_date"])
        self.assertEqual(changed_thesis.due_date, data["due_date"])
        self.assertEqual(changed_thesis.assessor, None)
        self.assertEqual(changed_thesis.supervisor, thesis.supervisor)
        self.assertEqual(changed_thesis.external, data["external"])
        self.assertEqual(changed_thesis.external_where, data["external_where"])
        self.assertEqual(changed_thesis.student_contact, data["student_email"])
