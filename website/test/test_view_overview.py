from django.urls import reverse
from django.test import TestCase, Client

from datetime import date
from decimal import Decimal

from website.models import *
from website.test.test import LoggedInTestCase, ThesisStub


class ViewOverviewTests(LoggedInTestCase):

    def test_overview_for_supervisor(self):
        """Overview should display all theses for logged in supervisor"""
        ThesisStub.small(self.supervisor)

        response = self.client.get(reverse('overview'))

        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.context["theses"]))

    def test_supervisor_does_not_see_theses_of_other_supervisors(self):
        ThesisStub.small(self.supervisor)

        other_supervisor = Supervisor(first_name="Peter",
                                      last_name="Müller",
                                      id="p.mueller")

        other_supervisor.save()

        not_visible = ThesisStub.applied(other_supervisor)

        response = self.client.get(reverse('overview'))

        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.context["theses"]))
        self.assertTrue(not_visible not in response.context["theses"])
        self.assertIn('class="icon-link"', str(response.content))

    def test_overview_for_secretary(self):
        """Overview should display all theses for secretaries"""
        self.user.is_secretary = True
        self.user.save()

        other_supervisor = Supervisor(first_name="Peter",
                                      last_name="Müller",
                                      id="p.mueller")

        other_supervisor.save()

        ThesisStub.small(other_supervisor)

        response = self.client.get(reverse('overview'))

        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.context["theses"]))

    def test_overview_for_head(self):
        """Overview should display all theses for head of examination board"""
        self.user.is_head = True
        self.user.save()

        other_supervisor = Supervisor(first_name="Peter",
                                      last_name="Müller",
                                      id="p.mueller")

        other_supervisor.save()

        ThesisStub.small(other_supervisor)

        response = self.client.get(reverse('overview'))

        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.context["theses"]))

    def test_search_due_date(self):
        thesis = ThesisStub.applied(self.supervisor)
        thesis.save()

        response = self.client.post(reverse('overview'), {"due_date": date(2018, 1, 30), "status": "", "title": "",
                                                          "student": "", "assessor": "", "sort": ""})

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.context["theses"]))

    def test_search_status(self):
        thesis = ThesisStub.applied(self.supervisor)
        thesis.save()

        for value in ["1", "2", "3"]:
            response = self.client.post(reverse('overview'), {"due_date": "", "status": value, "title": "",
                                                              "student": "", "assessor": "", "sort": ""})

            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.context["theses"]))

        for value in ["", "0"]:
            response = self.client.post(reverse('overview'), {"due_date": "", "status": value, "title": "",
                                                              "student": "", "assessor": "", "sort": ""})

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.context["theses"]))

    def test_search_student_id(self):
        thesis = ThesisStub.applied(self.supervisor)
        thesis.save()

        for id in range(0, 4):
            response = self.client.post(reverse('overview'), {"due_date": "", "status": "", "title": "",
                                                              "student": id, "assessor": "", "sort": ""})

            self.assertEqual(200, response.status_code)
            self.assertEqual(0, len(response.context["theses"]))

        for id in {"9", "98", "987", "9876", "98765", "987654"}:
            response = self.client.post(reverse('overview'), {"due_date": "", "status": "", "title": "",
                                                              "student": id, "assessor": "", "sort": ""})

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.context["theses"]))

    def test_search_student_name(self):
        thesis = ThesisStub.applied(self.supervisor)
        thesis.save()

        for name in ["L", "L L", "Larry", "Langzeitstudent", "Larry Langzeitstudent"]:
            response = self.client.post(reverse('overview'), {"due_date": "", "status": "", "title": "",
                                                              "student": name, "assessor": "", "sort": ""})

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.context["theses"]))


    def test_search_thesis_name(self):
        thesis = ThesisStub.applied(self.supervisor)
        thesis.save()

        for title in ["Eine", "Thesis", "Eine einzelne Thesis"]:
            response = self.client.post(reverse('overview'), {"due_date": "", "status": "", "title": title,
                                                              "student": "", "assessor": "", "sort": ""})

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.context["theses"]))


    def test_search_assessor_name(self):
        thesis = ThesisStub.applied(self.supervisor)
        thesis.save()

        for name in ["H", "H S", "Hansi", "Schmidt", "Hansi Schmidt"]:
            response = self.client.post(reverse('overview'), {"due_date": "", "status": "", "title": "",
                                                              "student": "", "assessor": name, "sort": ""})

            self.assertEqual(200, response.status_code)
            self.assertEqual(1, len(response.context["theses"]))
