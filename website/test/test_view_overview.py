from django.test.utils import setup_test_environment
from django.urls import reverse

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
