from django.test.utils import setup_test_environment
from django.urls import reverse

from datetime import date
from decimal import Decimal

from website.models import *
from website.test.test import LoggedInTestCase, ThesisStub

setup_test_environment()


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

    def test_no_operations_possible_for_graded_thesis(self):
        thesis = ThesisStub.applied(self.supervisor)
        thesis.save()
        thesis.assign_grade(Decimal("1.3"), date(2020, 3, 1))

        response = self.client.get(reverse('overview'))

        self.assertNotIn('class="icon-link"', str(response.content))
