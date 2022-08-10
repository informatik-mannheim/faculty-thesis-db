#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase

from website.forms import StudentForm
from website.models import Student


class StudentFormTest(TestCase):
    databases = {'default', 'faculty'}

    def setUp(self):
        pass

    def test_invalid_if_nothing_provided(self):
        data = {}

        form = StudentForm(data)
        form.full_clean()

        self.assertFalse(form.is_valid())

        student = form.create_student()

        self.assertEqual(None, student)

    def test_valid_with_bachelor_program(self):
        data = {'id': 123456,
                'first_name': "Linus",
                'last_name': "Kanstein",
                'program': "IB"}

        form = StudentForm(data)
        form.full_clean()

        self.assertTrue(form.is_valid())

        student = form.create_student()

        self.assertEqual(data["id"], student.id)
        self.assertEqual(data["first_name"], student.first_name)
        self.assertEqual(data["last_name"], student.last_name)
        self.assertEqual(data["program"], student.program)

    def test_valid_with_master_program(self):
        data = {'id': 123456,
                'first_name': "Linus",
                'last_name': "Kanstein",
                'program': "IM"}

        form = StudentForm(data)
        form.full_clean()

        self.assertTrue(form.is_valid())

        student = form.create_student()

        self.assertEqual(data["id"], student.id)
        self.assertEqual(data["first_name"], student.first_name)
        self.assertEqual(data["last_name"], student.last_name)
        self.assertEqual(data["program"], student.program)

    def test_invalid_when_no_id_provided(self):
        data = {'first_name': "Linus",
                'last_name': "Kanstein",
                'program': "IB"}

        form = StudentForm(data)
        form.full_clean()

        self.assertFalse(form.is_valid())

        student = form.create_student()

        self.assertEqual(None, student)

    def test_invalid_when_no_first_name_provided(self):
        data = {'id': 123456,
                'last_name': "Kanstein",
                'program': "IB"}

        form = StudentForm(data)
        form.full_clean()

        self.assertFalse(form.is_valid())

        student = form.create_student()

        self.assertEqual(None, student)

    def test_invalid_when_no_last_name_provided(self):
        data = {'id': 123456,
                'first_name': "Linus",
                'program': "IB"}

        form = StudentForm(data)
        form.full_clean()

        self.assertFalse(form.is_valid())

        student = form.create_student()

        self.assertEqual(None, student)

    def test_invalid_if_no_program_provided(self):
        data = {'id': 123456,
                'first_name': "Linus",
                'last_name': "Kanstein"
                }

        form = StudentForm(data)
        form.full_clean()

        self.assertFalse(form.is_valid())

        student = form.create_student()

        self.assertEqual(None, student)

    def test_invalid_if_error_in_program(self):
        """program must have at least 2 chars and must end with either B (bachelor) or M (master)"""
        for program in ["IE", "B"]:
            data = {'id': 123456,
                    'first_name': "Linus",
                    'last_name': "Kanstein",
                    'program': program}

            form = StudentForm(data)
            form.full_clean()

            self.assertFalse(form.is_valid())
            self.assertIn('unvollständiger Studiengang', form.non_field_errors())

            student = form.create_student()

            self.assertEqual(None, student)

    def test_invalid_when_id_already_used_in_faculty(self):
        student = Student(id=123456, first_name="Peter", last_name="Petermann", program="IB")
        student.save(using='faculty')

        data = {'id': 123456,
                'first_name': "Linus",
                'last_name': "Kanstein",
                'program': "IB"}

        form = StudentForm(data)
        form.full_clean()

        self.assertFalse(form.is_valid())
        self.assertIn('Matrikelnummer bereits vorhanden', form.non_field_errors())

        student = form.create_student()

        self.assertEqual(None, student)

    def test_invalid_when_id_already_used_in_default(self):
        student = Student(id=123456, first_name="Peter", last_name="Petermann", program="IB")
        student.save(using='default')

        data = {'id': 123456,
                'first_name': "Linus",
                'last_name': "Kanstein",
                'program': "IB"}

        form = StudentForm(data)
        form.full_clean()

        self.assertFalse(form.is_valid())
        self.assertIn('Matrikelnummer bereits vorhanden', form.non_field_errors())

        student = form.create_student()

        self.assertEqual(None, student)
