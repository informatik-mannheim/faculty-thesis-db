from django.test import TestCase
from django.test.utils import setup_test_environment
from datetime import datetime

from website.models import *


setup_test_environment()


class ThesisModelTests(TestCase):

    def test_create_model(self):
        student = Student(first_name="Eva", last_name="Maier", id=123456)
        assessor = Assessor(first_name="Peter", last_name="Müller")
        supervisor = Supervisor(first_name="Thomas",
                                last_name="Smits", id="t.smits")

        assessor.save()
        supervisor.save()
        student.save()

        title = "Einsatz eines Flux-Kompensators für Zeitreisen" \
                " mit einer maximalen Höchstgeschwindigkeit von WARP 7"

        thesis = Thesis(student=student,
                        assessor=assessor,
                        supervisor=supervisor,
                        title=title,
                        begin_date=datetime.now().date(),
                        due_date=datetime(2019, 1, 30))

        thesis.save()

        self.assertEqual(1, Thesis.objects.count())
        self.assertEqual(supervisor, Thesis.objects.first().supervisor)
        self.assertEqual(assessor, Thesis.objects.first().assessor)
        self.assertEqual(student, Thesis.objects.first().student)
        self.assertEqual(title, Thesis.objects.first().title)

    def test_cascading_delete_assessor(self):
        student = Student(first_name="Eva", last_name="Maier", id=123456)
        assessor = Assessor(first_name="Peter", last_name="Müller")
        supervisor = Supervisor(first_name="Thomas",
                                last_name="Smits", id="t.smits")

        assessor.save()
        supervisor.save()
        student.save()

        title = "Einsatz eines Flux-Kompensators für Zeitreisen" \
                " mit einer maximalen Höchstgeschwindigkeit von WARP 7"

        thesis = Thesis(assessor=assessor,
                        supervisor=supervisor,
                        student=student,
                        title=title,
                        begin_date=datetime.now().date(),
                        due_date=datetime(2019, 1, 30))
        thesis.save()

        self.assertEqual(1, Thesis.objects.count())

        assessor.delete()

        self.assertEqual(0, Thesis.objects.count())

    def test_cascading_delete_supervisor(self):
        student = Student(first_name="Eva", last_name="Maier", id=123456)
        assessor = Assessor(first_name="Peter", last_name="Müller")
        supervisor = Supervisor(first_name="Thomas",
                                last_name="Smits", id="t.smits")

        assessor.save()
        supervisor.save()
        student.save()

        title = "Einsatz eines Flux-Kompensators für Zeitreisen" \
                " mit einer maximalen Höchstgeschwindigkeit von WARP 7"

        thesis = Thesis(student=student,
                        assessor=assessor,
                        supervisor=supervisor,
                        title=title,
                        begin_date=datetime.now().date(),
                        due_date=datetime(2019, 1, 30))
        thesis.save()

        self.assertEqual(1, Thesis.objects.count())

        supervisor.delete()

        self.assertEqual(0, Thesis.objects.count())
