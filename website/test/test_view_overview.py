from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.contrib.auth.models import User
from django.urls import reverse

from datetime import datetime

from website.models import *


setup_test_environment()


class ViewOverviewTests(TestCase):

    def setUp(self):
        """Force login for an arbitrary user as the overview is protected"""
        user = User(username="t.smits", password="pass")
        user.save()

        self.client = Client()
        self.client.force_login(user)

        self.student = Student(first_name="Eva", last_name="Maier", id=123456)
        self.assessor = Assessor(first_name="Peter", last_name="Müller")
        self.supervisor = Supervisor(first_name="Thomas",
                                     last_name="Smits", id=user.username)

        self.assessor.save()
        self.supervisor.save()
        self.student.save()

    def test_overview_for_supervisor(self):
        """Overview should display all theses for logged in supervisor"""
        title = "Any title"

        Thesis(student=self.student,
               assessor=self.assessor,
               supervisor=self.supervisor,
               title=title,
               begin_date=datetime.now().date(),
               due_date=datetime(2018, 1, 30),
               status=Thesis.PROLONGED).save()

        Thesis(student=self.student,
               assessor=self.assessor,
               supervisor=self.supervisor,
               title=title,
               begin_date=datetime.now().date(),
               due_date=datetime(2019, 1, 30),
               status=Thesis.APPLIED).save()

        Thesis(student=self.student,
               assessor=self.assessor,
               supervisor=self.supervisor,
               title=title,
               begin_date=datetime.now().date(),
               due_date=datetime(2017, 1, 30),
               status=Thesis.GRADED).save()

        supervisor = Supervisor(first_name="Peter",
                                last_name="Müller",
                                id="p.mueller")

        supervisor.save()

        not_visible = Thesis(student=self.student,
                             assessor=self.assessor,
                             supervisor=supervisor,
                             title=title,
                             begin_date=datetime.now().date(),
                             due_date=datetime(2017, 1, 30))

        not_visible.save()

        response = self.client.get(reverse('overview'))

        self.assertEqual(200, response.status_code)

        self.assertEqual(3, len(response.context["theses"]))
        self.assertTrue(not_visible not in response.context["theses"])
