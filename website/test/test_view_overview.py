from website.models import User
from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse

from website.models import *
from website.test.data import ThesisSet

setup_test_environment()


class ViewOverviewTests(TestCase):

    def setUp(self):
        """Force login for an arbitrary user as the overview is protected"""
        self.user = User(username="t.smits", password="pass")
        self.user.save()

        self.client = Client()

        self.student = Student(first_name="Eva", last_name="Maier", id=123456)
        self.assessor = Assessor(first_name="Peter", last_name="Müller")
        self.supervisor = Supervisor(first_name="Thomas",
                                     last_name="Smits", id=self.user.username)

        self.assessor.save()
        self.supervisor.save()
        self.student.save()

    def test_overview_for_supervisor(self):
        """Overview should display all theses for logged in supervisor"""
        self.client.force_login(self.user)
        ThesisSet.small(self.supervisor)

        response = self.client.get(reverse('overview'))

        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.context["theses"]))

    def test_supervisor_does_not_see_theses_of_other_supervisors(self):
        self.client.force_login(self.user)
        ThesisSet.small(self.supervisor)

        other_supervisor = Supervisor(first_name="Peter",
                                      last_name="Müller",
                                      id="p.mueller")

        other_supervisor.save()

        not_visible = ThesisSet.single(other_supervisor)

        response = self.client.get(reverse('overview'))

        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.context["theses"]))
        self.assertTrue(not_visible not in response.context["theses"])

    def test_theses_should_be_sorted_by_due_date(self):
        self.client.force_login(self.user)

        theses = ThesisSet.small(self.supervisor)
        expected_order = sorted(theses, key=lambda thesis: thesis.due_date)

        response = self.client.get(reverse('overview'))

        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.context["theses"]))

        self.assertEqual(expected_order, list(response.context["theses"]))
