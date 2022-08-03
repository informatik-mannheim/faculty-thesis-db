from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date

from website.models import *
from decimal import Decimal


class ThesisModelTests(TestCase):

    def setUp(self):
        """
        Create dependencies to reduce redundancy in tests
        """
        self.student = Student(first_name="Eva", last_name="Maier", id=123456, program="IB")
        self.assessor = Assessor(first_name="Peter", last_name="Müller")
        self.supervisor = Supervisor(first_name="Thomas", last_name="Smits", id="t.smits")

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
                        thesis_program=self.student.program,
                        begin_date=date(2017, 11, 30),
                        due_date=date(2018, 1, 30),
                        external=True,
                        external_where="John Deere")

        thesis.save()

        self.assertEqual(1, Thesis.objects.count())
        self.assertEqual(self.supervisor, Thesis.objects.first().supervisor)
        self.assertEqual(self.assessor, Thesis.objects.first().assessor)
        self.assertEqual(self.student, Thesis.objects.first().student)
        self.assertEqual(title, Thesis.objects.first().title)
        self.assertEqual("IB", Thesis.objects.first().thesis_program)
        self.assertEqual("John Deere", Thesis.objects.first().external_where)
        self.assertTrue(Thesis.objects.first().external)

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
                        thesis_program=self.student.program,
                        begin_date=date(2019, 1, 30),
                        due_date=date(2019, 3, 30))
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
                        thesis_program=self.student.program,
                        begin_date=date(2019, 1, 30),
                        due_date=date(2019, 3, 30))
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
                        thesis_program=self.student.program,
                        begin_date=date(2019, 1, 30),
                        due_date=date(2019, 3, 30))
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
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30))

        newest = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title=title,
                        thesis_program=self.student.program,
                        begin_date=date(2019, 1, 30),
                        due_date=date(2019, 3, 30))

        oldest = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title=title,
                        thesis_program=self.student.program,
                        begin_date=date(2017, 1, 30),
                        due_date=date(2017, 3, 30))

        supervisor = Supervisor(first_name="Peter",
                                last_name="Müller",
                                id="p.mueller")

        supervisor.save()

        other_supervisor = Thesis(student=self.student,
                                  assessor=self.assessor,
                                  supervisor=supervisor,
                                  title=title,
                                  thesis_program=self.student.program,
                                  begin_date=date(2017, 1, 30),
                                  due_date=date(2017, 3, 30))

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
        """
        Thesis can be created without an Assessor
        """
        title = "Smart thesis title"

        thesis = Thesis(student=self.student,
                        assessor=None,
                        supervisor=self.supervisor,
                        title=title,
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30))

        thesis.save()

        self.assertEqual(None, thesis.assessor)

    def test_garde_highest_value(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        begin_date=date(2017, 11, 30),
                        due_date=date(2018, 1, 30))

        thesis.save()

        grade = 1.0
        examination_date = date(2018, 2, 15)

        result = thesis.assign_grade(grade, grade, examination_date)
        thesis = Thesis.objects.first()

        self.assertEqual(thesis.status, Thesis.GRADED)
        self.assertEqual(float(thesis.grade), grade)
        self.assertEqual(float(thesis.assessor_grade), grade)
        self.assertTrue(result)
        self.assertEqual(examination_date, thesis.examination_date)

    def test_grade_lowest_value(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30))

        thesis.save()

        grade = 5.0
        examination_date = date(2018, 2, 15)

        result = thesis.assign_grade(grade, grade, examination_date)
        thesis = Thesis.objects.first()

        self.assertEqual(thesis.status, Thesis.GRADED)
        self.assertEqual(thesis.grade, grade)
        self.assertEqual(thesis.assessor_grade, grade)
        self.assertTrue(result)
        self.assertEqual(examination_date, thesis.examination_date)

    def test_invalid_grades(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30))

        thesis.save()

        grades = [-1, 0.9, 5.1, 2.22]
        examination_date = date(2018, 2, 15)

        for grade in grades:
            with self.assertRaises(ValidationError):
                result = thesis.assign_grade(Decimal(grade), Decimal(grade), examination_date)

                thesis = Thesis.objects.first()

                self.assertEqual(thesis.status, Thesis.APPLIED)
                self.assertEqual(thesis.grade, None)
                self.assertEqual(thesis.assessor_grade, None)
                self.assertFalse(result)

    def test_no_assessor_grade_when_no_assessor(self):
        thesis = Thesis(student=self.student,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30))

        thesis.save()

        grade = 5.0
        examination_date = date(2018, 2, 15)

        result = thesis.assign_grade(grade, grade, examination_date)
        thesis = Thesis.objects.first()

        self.assertEqual(thesis.status, Thesis.GRADED)
        self.assertEqual(thesis.grade, grade)
        self.assertEqual(thesis.assessor_grade, None)
        self.assertTrue(result)
        self.assertEqual(examination_date, thesis.examination_date)

    def test_can_change_a_graded_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30))

        thesis.save()

        grade = Decimal("1.1")
        grade2 = Decimal("5.0")
        examination_date = date(2018, 2, 15)
        examination_date2 = date(2018, 2, 16)

        result = thesis.assign_grade(grade, grade, examination_date)
        result = thesis.assign_grade(grade2, grade2, examination_date2)

        thesis = Thesis.objects.first()

        self.assertEqual(thesis.grade, grade2)
        self.assertEqual(thesis.examination_date, examination_date2)
        self.assertEqual(thesis.status, Thesis.GRADED)
        self.assertTrue(result)

    def test_can_prolong_a_thesis(self):
        prolongation_date = date(2019, 1, 1)

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30))

        thesis.save()

        result = thesis.prolong(prolongation_date, "aus gutem Grund", 4)

        thesis = Thesis.objects.first()

        self.assertEqual(prolongation_date, thesis.prolongation_date)
        self.assertEqual(Thesis.PROLONGED, thesis.status)
        self.assertEqual(4, thesis.prolongation_weeks)
        self.assertTrue(result)

    def test_can_prolong_a_thesis_twice(self):
        first_prolongation = date(2019, 1, 1)
        second_prolongation = date(2019, 3, 1)

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.APPLIED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        restriction_note = False)

        thesis.save()

        result = thesis.prolong(first_prolongation, "aus gutem Grund", 4)

        thesis = Thesis.objects.first()

        self.assertEqual(first_prolongation, thesis.prolongation_date)
        self.assertEqual(Thesis.PROLONGED, thesis.status)
        self.assertEqual(4, thesis.prolongation_weeks)
        self.assertTrue(result)

        result = thesis.prolong(second_prolongation, "aus neuem Grund", 4)

        self.assertEqual(second_prolongation, thesis.prolongation_date)
        self.assertEqual(Thesis.PROLONGED, thesis.status)
        self.assertEqual(4, thesis.prolongation_weeks)
        self.assertTrue(result)

    def test_can_not_prolong_a_handed_in_thesis(self):
        prolongation_date = date(2019, 1, 1)

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.HANDED_IN,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30))

        thesis.save()

        self.assertEqual(Thesis.objects.first().prolongation_date, None)

        result = thesis.prolong(prolongation_date, "aus gutem Grund", 4)

        thesis = Thesis.objects.first()

        self.assertEqual(None, thesis.prolongation_date)
        self.assertEqual(Thesis.HANDED_IN, thesis.status)
        self.assertFalse(result)

    def test_can_not_prolong_a_graded_thesis(self):
        prolongation_date = date(2019, 1, 1)

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.GRADED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30))

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
                        thesis_program=self.student.program,
                        status=Thesis.APPLIED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30))

        thesis.save()

        self.assertEqual(Thesis.objects.first().prolongation_date, None)

        with self.assertRaises(ValidationError):
            thesis.prolong(prolongation_date, "aus gutem Grund", 4)

    def test_can_not_prolong_thesis_with_date_before_due_date(self):
        prolongation_date = date(2018, 6, 29)

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.APPLIED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30))

        thesis.save()

        with self.assertRaises(ValidationError):
            thesis.prolong(prolongation_date, "aus gutem Grund", 4)

    def test_can_not_prolong_thesis_with_date_equal_due_date(self):
        prolongation_date = date(2018, 6, 30)

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.APPLIED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30))

        thesis.save()

        with self.assertRaises(ValidationError):
            thesis.prolong(prolongation_date, "aus gutem Grund", 4)

    def test_thesis_without_handed_in_date_is_never_late(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.APPLIED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30))

        self.assertFalse(thesis.is_late())

    def test_thesis_is_not_late_if_handed_in_on_due_date(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.HANDED_IN,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        handed_in_date=date(2018, 6, 30))

        self.assertFalse(thesis.is_late())

    def test_thesis_is_late_if_handed_in_after_due_date(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.HANDED_IN,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        handed_in_date=date(2018, 7, 1))

        self.assertTrue(thesis.is_late())

    def test_thesis_is_not_late_if_handed_in_on_prolongation_date(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.HANDED_IN,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        prolongation_date=date(2018, 7, 30),
                        handed_in_date=date(2018, 7, 30))

        self.assertFalse(thesis.is_late())

    def test_thesis_is_late_if_handed_in_after_prolongation_date(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.HANDED_IN,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        prolongation_date=date(2018, 9, 30),
                        handed_in_date=date(2018, 10, 1))

        self.assertTrue(thesis.is_late())

    def test_can_hand_in_an_applied_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.APPLIED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30))

        handed_in_date = date(2018, 6, 30)

        thesis.hand_in(handed_in_date)

        self.assertEqual(thesis.handed_in_date, handed_in_date)
        self.assertEqual(Thesis.HANDED_IN, thesis.status)
        self.assertTrue(thesis.is_handed_in())

    def test_can_hand_in_with_restriction_note(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.APPLIED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30))

        handed_in_date = date(2018, 6, 30)

        thesis.hand_in(handed_in_date, True)

        self.assertEqual(thesis.handed_in_date, handed_in_date)
        self.assertEqual(Thesis.HANDED_IN, thesis.status)
        self.assertTrue(thesis.is_handed_in())
        self.assertTrue(thesis.restriction_note)

    def test_can_hand_in_a_prolonged_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.PROLONGED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        prolongation_date=date(2018, 7, 30))

        handed_in_date = date(2018, 8, 30)

        thesis.hand_in(handed_in_date)

        self.assertEqual(thesis.handed_in_date, handed_in_date)
        self.assertEqual(Thesis.HANDED_IN, thesis.status)
        self.assertTrue(thesis.is_handed_in())

    def test_can_not_hand_in_thesis_again(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.HANDED_IN,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        handed_in_date=date(2018, 6, 30))

        handed_in_date = date(2018, 8, 29)

        success = thesis.hand_in(handed_in_date)

        self.assertFalse(success)
        self.assertNotEqual(thesis.handed_in_date, handed_in_date)
        self.assertEqual(Thesis.HANDED_IN, thesis.status)
        self.assertTrue(thesis.is_handed_in())

    def test_handing_in_a_graded_thesis_does_not_change_status(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.GRADED,
                        grade=1.3,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        examination_date=date(2018, 6, 30))

        handed_in_date = date(2018, 8, 29)

        success = thesis.hand_in(handed_in_date)

        self.assertTrue(success)
        self.assertEqual(thesis.handed_in_date, handed_in_date)
        self.assertEqual(Thesis.GRADED, thesis.status)
        self.assertTrue(thesis.is_handed_in())

    def test_deadline_without_prolongation(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.APPLIED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30))

        self.assertEqual(thesis.due_date, thesis.deadline)

    def test_deadline_with_prolongation(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.PROLONGED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        prolongation_date=date(2018, 9, 30))

        self.assertEqual(thesis.prolongation_date, thesis.deadline)

    def test_bachelor_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30))

        self.assertTrue(thesis.is_bachelor())

    def test_master_thesis(self):
        self.student.program = "IM"

        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30))

        self.assertTrue(thesis.is_master())

    def test_student_is_now_master(self):
        """id stays the same after the student changed his program.
        The program of old theses has to stay the same."""
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Some title",
                        thesis_program=self.student.program,
                        status=Thesis.PROLONGED,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 6, 30),
                        prolongation_date=date(2018, 9, 30))

        self.student.program = "IM"

        self.assertEqual(self.student.program, "IM")
        self.assertEqual(thesis.thesis_program, "IB")
