from django.test import TestCase, Client
from django.urls import reverse

import uuid

from website.models import *
from website.test.test import ThesisStub, LoggedInTestCase


class ApprovalViewTests(LoggedInTestCase):

    def test_normal_user_can_not_see_approvals_index(self):
        response = self.client.get(reverse('index'))

        self.assertEqual(302, response.status_code)
        self.assertIn("/login/", response.url)

    def test_normal_user_can_not_approve_thesis(self):
        response = self.client.get(reverse('reject', args=[uuid.uuid4()]))

        self.assertEqual(302, response.status_code)
        self.assertIn("/login/", response.url)

    def test_normal_user_can_not_reject_thesis(self):
        response = self.client.get(reverse('approve', args=[uuid.uuid4()]))

        self.assertEqual(302, response.status_code)
        self.assertIn("/login/", response.url)


class ApprovalTests(TestCase):

    def setUp(self):
        user = User(username="prof", password="pass",
                    initials="PPP", is_excom=True)
        user.save()

        self.client = Client()
        self.client.force_login(user)

        supervisor = Supervisor(
            id="t.prof", first_name="Test", last_name="Prof", initials="TPF")
        supervisor.save()

        self.thesis = ThesisStub.applied(supervisor)
        self.thesis.save()

    def test_can_see_non_approved_theses(self):
        response = self.client.get("/approvals/")

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.context["theses"]))
        self.assertEqual(self.thesis, response.context["theses"][0])

    def test_can_approve_thesis(self):
        response = self.client.get(
            "/approvals/approve/{0}".format(self.thesis.surrogate_key),
            follow=True)

        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context["theses"]))

    def test_can_reject_thesis(self):
        reason = "Ein Grund"

        response = self.client.get(
            "/approvals/reject/{0}".format(self.thesis.surrogate_key))

        self.assertEqual(200, response.status_code)

        response = self.client.post(
            "/approvals/reject/{0}".format(self.thesis.surrogate_key),
            {"reason": reason},
            follow=True
        )

        thesis = Thesis.objects.first()

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.context["theses"]))
        self.assertTrue(thesis.is_rejected())
        self.assertEqual(reason, thesis.excom_reject_reason)
