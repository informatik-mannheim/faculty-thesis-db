#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.urls import reverse

from website.models import Thesis
from website.test.test import LoggedInTestCase, ThesisStub

import uuid
from datetime import timedelta, date


class ViewProlongationTests(LoggedInTestCase):

    def test_404_on_invalid_key(self):
        response = self.client.get(reverse('prolong', args=[uuid.uuid4()]))

        self.assertEqual(404, response.status_code)

    def test_empty_form(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.save()

        response = self.client.get(
            reverse('prolong', args=[thesis.surrogate_key]))

        self.assertEqual(200, response.status_code)

    def test_valid_prolongation(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.begin_date = date(2018, 1, 1)
        thesis.due_date = date(2018, 3, 30)

        thesis.save()

        post_data = {
            'prolongation_date': thesis.due_date + timedelta(30),
            'due_date': thesis.due_date,
            'reason': 'I was sick',
            'weeks': 4
        }

        response = self.client.post(
            reverse('prolong', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(302, response.status_code)

        thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

        self.assertEqual(Thesis.PROLONGED, thesis.status)

    def test_error_no_reason(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.begin_date = date(2018, 1, 1)
        thesis.due_date = date(2018, 3, 30)

        thesis.save()

        post_data = {
            'prolongation_date': thesis.due_date + timedelta(30),
            'due_date': thesis.due_date,
            'reason': '',
            'weeks': 4
        }

        response = self.client.post(
            reverse('prolong', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(200, response.status_code)
        self.assertIn('reason', response.context["form"].errors)

        thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

        self.assertEqual(Thesis.APPLIED, thesis.status)

    def test_error_no_weeks(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.begin_date = date(2018, 1, 1)
        thesis.due_date = date(2018, 3, 30)

        thesis.save()

        post_data = {
            'prolongation_date': thesis.due_date + timedelta(30),
            'due_date': thesis.due_date,
            'reason': 'A perfectly valid reason',
            'weeks': 0
        }

        response = self.client.post(
            reverse('prolong', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(200, response.status_code)
        self.assertIn('weeks', response.context["form"].errors)

        thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

        self.assertEqual(Thesis.APPLIED, thesis.status)

    def test_error_prolongation_date_equal_due_date(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.begin_date = date(2018, 1, 1)
        thesis.due_date = date(2018, 3, 30)

        thesis.save()

        post_data = {
            'prolongation_date': thesis.due_date,
            'due_date': thesis.due_date,
            'reason': 'A perfectly valid reason',
            'weeks': 0
        }

        response = self.client.post(
            reverse('prolong', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(200, response.status_code)
        self.assertIn('prolongation_date', response.context["form"].errors)

        thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

        self.assertEqual(Thesis.APPLIED, thesis.status)

    def test_error_prolongation_date_before_due_date(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.begin_date = date(2018, 1, 1)
        thesis.due_date = date(2018, 3, 30)

        thesis.save()

        post_data = {
            'prolongation_date': thesis.due_date - timedelta(30),
            'due_date': thesis.due_date,
            'reason': 'A perfectly valid reason',
            'weeks': 0
        }

        response = self.client.post(
            reverse('prolong', args=[thesis.surrogate_key]), post_data)

        self.assertEqual(200, response.status_code)
        self.assertIn('prolongation_date', response.context["form"].errors)

        thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)

        self.assertEqual(Thesis.APPLIED, thesis.status)

    def test_sets_prolongation_date_as_due_date(self):
        thesis = ThesisStub.applied(self.supervisor)

        thesis.begin_date = date(2018, 1, 1)
        thesis.due_date = date(2018, 3, 30)
        first_prolongation = date(2018, 4, 30)

        thesis.save()

        thesis.prolong(first_prolongation, 'because', 4)

        response = self.client.get(
            reverse('prolong', args=[thesis.surrogate_key]))

        initial_due_date = response.context["form"].initial["due_date"]
        initial_prolongation = response.context[
            "form"].initial["prolongation_date"]

        self.assertEqual(200, response.status_code)
        self.assertEqual(first_prolongation, initial_due_date)
        self.assertEqual(first_prolongation + timedelta(30),
                         initial_prolongation)
