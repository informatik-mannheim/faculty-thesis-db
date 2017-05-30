#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import FileResponse
from django.urls import reverse

from datetime import datetime

from website.models import *
from website.test.test import ThesisStub, LoggedInTestCase


class ViewPdfTests(LoggedInTestCase):

    def test_generates_application_pdf(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", id="mmuster")

        thesis = ThesisStub.applied(supervisor)

        supervisor.save()
        thesis.save()

        response = self.client.get(
            reverse('application_pdf', args=[thesis.surrogate_key]))

        expected_filename = "{0}_{1}_{2}.pdf".format(
            datetime.now().strftime("%Y%m%d"), 'ausgabe', thesis.student.id)

        self.assertEqual(200, response.status_code)
        self.assertEqual(FileResponse, type(response))
        self.assertEqual('application/pdf',
                         response._headers['content-type'][1])
        self.assertIn(expected_filename, response._headers[
                      'content-disposition'][1])

    def test_generates_prolongation_pdf(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", id="mmuster")

        thesis = ThesisStub.applied(supervisor)

        supervisor.save()
        thesis.save()

        response = self.client.get(
            reverse('prolongation_pdf', args=[thesis.surrogate_key]))

        expected_filename = "{0}_{1}_{2}.pdf".format(
            datetime.now().strftime("%Y%m%d"),
            'verlaengerung',
            thesis.student.id)

        self.assertEqual(200, response.status_code)
        self.assertEqual(FileResponse, type(response))
        self.assertEqual('application/pdf',
                         response._headers['content-type'][1])
        self.assertIn(expected_filename, response._headers[
                      'content-disposition'][1])

    def test_generates_grading_pdf(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", id="mmuster")

        thesis = ThesisStub.applied(supervisor)

        supervisor.save()
        thesis.save()

        response = self.client.get(
            reverse('grading_pdf', args=[thesis.surrogate_key]))

        expected_filename = "{0}_{1}_{2}.pdf".format(
            datetime.now().strftime("%Y%m%d"), 'bewertung', thesis.student.id)

        self.assertEqual(200, response.status_code)
        self.assertEqual(FileResponse, type(response))
        self.assertEqual('application/pdf',
                         response._headers['content-type'][1])
        self.assertIn(expected_filename, response._headers[
                      'content-disposition'][1])
