from django.test import TestCase
from django.test.utils import setup_test_environment

from website.models import *


setup_test_environment()


class ThesisModelTests(TestCase):

    def test_create_model(self):
        assessor = Assessor(first_name="Peter", last_name="Müller")
        supervisor = Supervisor(first_name="Thomas",
                                last_name="Smits", id="t.smits")

        assessor.save()
        supervisor.save()

        thesis = Thesis(assessor=assessor, supervisor=supervisor)
        thesis.save()

        self.assertEqual(1, Thesis.objects.count())
        self.assertEqual(Thesis.objects.first().supervisor, supervisor)
        self.assertEqual(Thesis.objects.first().assessor, assessor)
