from django.test import TestCase
from django.test.utils import setup_test_environment
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, date

from website.models import *
from decimal import Decimal


setup_test_environment()


class ThesisModelTests(TestCase):

    def setUp(self):
        """
        Create dependencies to reduce redundancy in tests
        """
        self.student = Student(first_name="Eva", last_name="Maier", id=123456)
        self.assessor = Assessor(first_name="Peter", last_name="Müller")
        self.supervisor = Supervisor(first_name="Thomas",
                                     last_name="Smits", id="t.smits")

        self.assessor.save()
        self.supervisor.save()
        self.student.save()

    def test_create_model(self):
        title = "Einsatz eines Flux-Kompensators für Zeitreisen" \
                " mit einer maximalen Höchstgeschwindigkeit von WARP 7"

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title=title,
                        begin_date=datetime.now().date(),
                        due_date=datetime(2019, 1, 30),
                        external=True,
                        external_where="John Deere")

        thesis.save()

        self.assertEqual(1, Thesis.objects.count())
        self.assertEqual(self.supervisor, Thesis.objects.first().supervisor)
        self.assertEqual(self.assessor, Thesis.objects.first().assessor)
        self.assertEqual(self.student, Thesis.objects.first().student)
        self.assertEqual(title, Thesis.objects.first().title)
        self.assertEqual("John Deere", Thesis.objects.first().external_where)
        self.assertEqual(True, Thesis.objects.first().external)

    def test_cascading_delete_assessor(self):
        """If assessor is deleted, the assessor field on the thesis
        should be set to null
        """
        title = "Einsatz eines Flux-Kompensators für Zeitreisen" \
                " mit einer maximalen Höchstgeschwindigkeit von WARP 7"

        thesis = Thesis(assessor=self.assessor,
                        supervisor=self.supervisor,
                        student=self.student,
                        title=title,
                        begin_date=datetime.now().date(),
                        due_date=datetime(2019, 1, 30))
        thesis.save()

        self.assertEqual(1, Thesis.objects.count())

        self.assessor.delete()

        self.assertEqual(1, Thesis.objects.count())
        self.assertEqual(None, Thesis.objects.first().assessor)

    def test_cascading_delete_supervisor(self):
        title = "Einsatz eines Flux-Kompensators für Zeitreisen" \
                " mit einer maximalen Höchstgeschwindigkeit von WARP 7"

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title=title,
                        begin_date=datetime.now().date(),
                        due_date=datetime(2019, 1, 30))
        thesis.save()

        self.assertEqual(1, Thesis.objects.count())

        self.supervisor.delete()

        self.assertEqual(0, Thesis.objects.count())

    def test_default_status_is_applied(self):
        """A new thesis should have its default status set to Applied ('AP')"""
        title = "Any title"

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title=title,
                        begin_date=datetime.now().date(),
                        due_date=datetime(2019, 1, 30))
        thesis.save()

        self.assertEqual(Thesis.objects.first().status, Thesis.APPLIED)

    def test_returns_theses_for_supervisor(self):
        """ThesisManager should return all theses for given supervisor
        ordered by due date ascending
        """

        title = "Any title"

        middle = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title=title,
                        begin_date=datetime.now().date(),
                        due_date=datetime(2018, 1, 30))

        newest = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title=title,
                        begin_date=datetime.now().date(),
                        due_date=datetime(2019, 1, 30))

        oldest = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title=title,
                        begin_date=datetime.now().date(),
                        due_date=datetime(2017, 1, 30))

        supervisor = Supervisor(first_name="Peter",
                                last_name="Müller",
                                id="p.mueller")

        supervisor.save()

        other_supervisor = Thesis(student=self.student,
                                  assessor=self.assessor,
                                  supervisor=supervisor,
                                  title=title,
                                  begin_date=datetime.now().date(),
                                  due_date=datetime(2017, 1, 30))

        middle.save()
        newest.save()
        oldest.save()
        other_supervisor.save()

        theses = Thesis.objects.for_supervisor(self.supervisor.id)

        self.assertEqual(3, theses.count())
        self.assertTrue(oldest, theses[0])
        self.assertTrue(middle, theses[1])
        self.assertTrue(newest, theses[2])
        self.assertTrue(other_supervisor not in theses)

    def test_can_have_no_assessor(self):
        """ThesisManager should return all theses for given supervisor
        ordered by due date ascending
        """
        title = "Smart thesis title"

        thesis = Thesis(student=self.student,
                        assessor=None,
                        supervisor=self.supervisor,
                        title=title,
                        begin_date=datetime.now().date(),
                        due_date=datetime(2018, 1, 30))

        thesis.save()

        self.assertEqual(None, thesis.assessor)

    def test_can_grade_a_thesis_with_best_grade(self):
        title = "My thesis"
        grade = 1.0
        examination_date = date(2018, 2, 15)

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title=title,
                        status=Thesis.APPLIED,
                        begin_date=datetime(2017, 11, 30).date(),
                        due_date=datetime(2018, 1, 30).date())

        thesis.save()

        self.assertEqual(thesis.status, Thesis.APPLIED)

        result = thesis.assign_grade(grade, examination_date)

        thesis = Thesis.objects.first()

        self.assertEqual(thesis.status, Thesis.GRADED)
        self.assertEqual(float(thesis.grade), grade)
        self.assertTrue(result)
        self.assertEqual(examination_date, thesis.examination_date)

    def test_can_grade_a_thesis_with_average_grade(self):
        title = "My thesis"
        grade = Decimal("2.3")
        examination_date = date(2018, 2, 15)

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title=title,
                        status=Thesis.APPLIED,
                        begin_date=timezone.now().date(),
                        due_date=datetime(2018, 1, 30))

        thesis.save()

        self.assertEqual(thesis.status, Thesis.APPLIED)

        result = thesis.assign_grade(grade, examination_date)

        thesis = Thesis.objects.first()

        self.assertEqual(thesis.status, Thesis.GRADED)
        self.assertEqual(thesis.grade, grade)
        self.assertTrue(result)
        self.assertEqual(examination_date, thesis.examination_date)

    def test_can_grade_a_thesis_with_worst_grade(self):
        title = "My thesis"
        grade = Decimal("5.0")
        examination_date = date(2018, 2, 15)

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title=title,
                        status=Thesis.APPLIED,
                        begin_date=timezone.now().date(),
                        due_date=datetime(2018, 1, 30))

        thesis.save()

        self.assertEqual(thesis.status, Thesis.APPLIED)

        result = thesis.assign_grade(grade, examination_date)

        thesis = Thesis.objects.first()

        self.assertEqual(thesis.status, Thesis.GRADED)
        self.assertEqual(thesis.grade, grade)
        self.assertTrue(result)
        self.assertEqual(examination_date, thesis.examination_date)

    def test_can_not_grade_a_thesis_with_grade_above_best(self):
        title = "My thesis"
        grade = Decimal("0.9")
        examination_date = date(2018, 3, 29)

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title=title,
                        status=Thesis.APPLIED,
                        begin_date=datetime.now().date(),
                        due_date=datetime(2018, 1, 30))

        thesis.save()

        self.assertEqual(thesis.status, Thesis.APPLIED)
        with self.assertRaises(ValidationError):
            result = thesis.assign_grade(grade, examination_date)

            thesis = Thesis.objects.first()

            self.assertEqual(thesis.status, Thesis.APPLIED)
            self.assertFalse(result)

    def test_can_not_grade_a_thesis_with_invalid_grade(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=datetime.now().date(),
                        due_date=datetime(2018, 1, 30))

        thesis.save()

        self.assertEqual(thesis.status, Thesis.APPLIED)

        grades = ["-1000", "0.0", "0.5", "0.9", "0.99",
                  "0.999", "1.01", "5.1", "10", "100", "1000"]

        examination_date = date(2018, 3, 29)

        for grade in grades:
            with self.assertRaises(ValidationError):
                result = thesis.assign_grade(Decimal(grade), examination_date)

                thesis = Thesis.objects.first()

                self.assertEqual(thesis.status, Thesis.APPLIED)
                self.assertEqual(thesis.grade, None)
                self.assertFalse(result)

    def test_can_not_grade_a_graded_thesis_again(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=datetime.now().date(),
                        due_date=datetime(2018, 1, 30))

        thesis.save()

        self.assertEqual(thesis.grade, None)

        grade = Decimal("1.1")
        examination_date = date(2018, 3, 29)

        result = thesis.assign_grade(grade, examination_date)

        self.assertEqual(Thesis.objects.first().grade, grade)
        self.assertEqual(Thesis.objects.first().status, Thesis.GRADED)
        self.assertTrue(result)

        result = thesis.assign_grade(Decimal("5.0"), examination_date)

        self.assertEqual(Thesis.objects.first().grade, grade)
        self.assertEqual(Thesis.objects.first().status, Thesis.GRADED)
        self.assertFalse(result)

    def test_can_prolong_a_thesis(self):
        prolongation_date = datetime(2019, 1, 1).date()

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=datetime(2018, 1, 30),
                        due_date=datetime(2018, 6, 30))

        thesis.save()

        self.assertEqual(Thesis.objects.first().prolongation_date, None)

        result = thesis.prolong(prolongation_date, "aus gutem Grund", 4)

        thesis = Thesis.objects.first()

        self.assertEqual(prolongation_date, thesis.prolongation_date)
        self.assertEqual(Thesis.PROLONGED, thesis.status)
        self.assertTrue(result)

    def test_can_prolong_a_thesis_twice(self):
        first_prolongation = datetime(2019, 1, 1).date()
        second_prolongation = datetime(2019, 3, 1).date()

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=datetime(2018, 1, 30),
                        due_date=datetime(2018, 6, 30))

        thesis.save()

        self.assertEqual(Thesis.objects.first().prolongation_date, None)

        result = thesis.prolong(first_prolongation, "aus gutem Grund", 4)

        thesis = Thesis.objects.first()

        self.assertEqual(first_prolongation, thesis.prolongation_date)
        self.assertEqual(Thesis.PROLONGED, thesis.status)
        self.assertTrue(result)

        result = thesis.prolong(second_prolongation, "aus gutem Grund", 4)

        self.assertEqual(second_prolongation, thesis.prolongation_date)
        self.assertEqual(Thesis.PROLONGED, thesis.status)
        self.assertTrue(result)

    def test_can_not_prolong_a_handed_in_thesis(self):
        prolongation_date = datetime(2019, 1, 1).date()

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.HANDED_IN,
                        begin_date=datetime(2018, 1, 30),
                        due_date=datetime(2018, 6, 30))

        thesis.save()

        self.assertEqual(Thesis.objects.first().prolongation_date, None)

        result = thesis.prolong(prolongation_date, "aus gutem Grund", 4)

        thesis = Thesis.objects.first()

        self.assertEqual(None, thesis.prolongation_date)
        self.assertEqual(Thesis.HANDED_IN, thesis.status)
        self.assertFalse(result)

    def test_can_not_prolong_a_graded_thesis(self):
        prolongation_date = datetime(2019, 1, 1).date()

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.GRADED,
                        begin_date=datetime(2018, 1, 30),
                        due_date=datetime(2018, 6, 30))

        thesis.save()

        self.assertEqual(Thesis.objects.first().prolongation_date, None)

        result = thesis.prolong(prolongation_date, "aus gutem Grund", 4)

        thesis = Thesis.objects.first()

        self.assertEqual(None, thesis.prolongation_date)
        self.assertEqual(Thesis.GRADED, thesis.status)
        self.assertFalse(result)

    def test_can_not_prolong_thesis_with_invalid_date(self):
        prolongation_date = "NULL"

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=datetime(2018, 1, 30),
                        due_date=datetime(2018, 6, 30))

        thesis.save()

        self.assertEqual(Thesis.objects.first().prolongation_date, None)

        with self.assertRaises(ValidationError):
            thesis.prolong(prolongation_date, "aus gutem Grund", 4)

    def test_can_not_prolong_thesis_with_date_before_due_date(self):
        prolongation_date = datetime(2018, 6, 29).date()

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=datetime(2018, 1, 30),
                        due_date=datetime(2018, 6, 30))

        thesis.save()

        self.assertEqual(Thesis.objects.first().prolongation_date, None)

        with self.assertRaises(ValidationError):
            thesis.prolong(prolongation_date, "aus gutem Grund", 4)

    def test_can_not_prolong_thesis_with_date_equal_due_date(self):
        prolongation_date = datetime(2018, 6, 30).date()

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=datetime(2018, 1, 30),
                        due_date=datetime(2018, 6, 30))

        thesis.save()

        self.assertEqual(Thesis.objects.first().prolongation_date, None)

        with self.assertRaises(ValidationError):
            thesis.prolong(prolongation_date, "aus gutem Grund", 4)

    def test_thesis_is_not_late_if_graded_on_due_date(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        handed_in_date=date(2018, 6, 30))

        self.assertFalse(thesis.is_late())

    def test_thesis_is_not_late_if_handed_in_before_due_date(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        handed_in_date=date(2018, 6, 25))

        self.assertFalse(thesis.is_late())

    def test_thesis_is_late_if_handed_in_before_after_due_date(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        handed_in_date=date(2018, 7, 1))

        self.assertTrue(thesis.is_late())

    def test_thesis_is_not_late_if_handed_in_on_prolongation_date(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        handed_in_date=date(2018, 6, 30))

        self.assertFalse(thesis.is_late())

    def test_thesis_is_not_late_if_handed_in_before_prolongation_date(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=datetime(2018, 1, 30).date(),
                        due_date=datetime(2018, 6, 30).date(),
                        prolongation_date=datetime(2018, 9, 30).date(),
                        handed_in_date=datetime(2018, 9, 29).date())

        self.assertFalse(thesis.is_late())

    def test_thesis_is_late_if_handed_in_after_prolongation_date(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        status=Thesis.APPLIED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        prolongation_date=date(2018, 9, 30),
                        handed_in_date=date(2018, 10, 1))

        self.assertTrue(thesis.is_late())
