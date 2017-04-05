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

        title = "Einsatz eines Flux-Kompensators für Zeitreisen" \
                " mit einer maximalen Höchstgeschwindigkeit von WARP 7"

        thesis = Thesis(assessor=assessor, supervisor=supervisor, title=title)
        thesis.save()

        self.assertEqual(1, Thesis.objects.count())
        self.assertEqual(supervisor, Thesis.objects.first().supervisor)
        self.assertEqual(assessor, Thesis.objects.first().assessor)
        self.assertEqual(title, Thesis.objects.first().title)

    def test_cascading_delete_assessor(self):
        assessor = Assessor(first_name="Peter", last_name="Müller")
        supervisor = Supervisor(first_name="Thomas",
                                last_name="Smits", id="t.smits")

        assessor.save()
        supervisor.save()

        title = "Einsatz eines Flux-Kompensators für Zeitreisen" \
                " mit einer maximalen Höchstgeschwindigkeit von WARP 7"

        thesis = Thesis(assessor=assessor, supervisor=supervisor, title=title)
        thesis.save()

        self.assertEqual(1, Thesis.objects.count())

        assessor.delete()

        self.assertEqual(0, Thesis.objects.count())

    def test_cascading_delete_supervisor(self):
        assessor = Assessor(first_name="Peter", last_name="Müller")
        supervisor = Supervisor(first_name="Thomas",
                                last_name="Smits", id="t.smits")

        assessor.save()
        supervisor.save()

        title = "Einsatz eines Flux-Kompensators für Zeitreisen" \
                " mit einer maximalen Höchstgeschwindigkeit von WARP 7"

        thesis = Thesis(assessor=assessor, supervisor=supervisor, title=title)
        thesis.save()

        self.assertEqual(1, Thesis.objects.count())

        supervisor.delete()

        self.assertEqual(0, Thesis.objects.count())
