from django.urls import reverse

from datetime import date
import uuid

from website.models import Thesis
from website.test.test import LoggedInTestCase, ThesisStub


class ViewChangeTests(LoggedInTestCase):

    def test_404_if_thesis_not_found(self):
        response = self.client.get(reverse('change', args=[uuid.uuid4()]))

        self.assertEqual(404, response.status_code)

    def test_empty_change_view(self):
        thesis = ThesisStub.applied(self.supervisor)
        thesis.save()

        response = self.client.get(
            reverse('change', args=[thesis.surrogate_key]))

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["student"], thesis.student)

    def test_can_change_values(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        status=Thesis.APPLIED,
                        restriction_note = False)

        new_values = {
            'title': 'Ein ganz anderer Titel',
            'begin_date': date(2019, 1, 30),
            'due_date': date(2019, 4, 30),
            'student_email': 'student@example.com',
            'external': True,
            'external_where': 'Eine externe Firma'
        }

        thesis.save()

        response = self.client.post(
            reverse('change', args=[thesis.surrogate_key]), new_values)

        changed_thesis = Thesis.objects.get(surrogate_key=thesis.surrogate_key)
        self.assertEqual(302, response.status_code)
        self.assertEqual(changed_thesis.title, new_values["title"])
        self.assertEqual(changed_thesis.assessor, None)
        self.assertEqual(changed_thesis.begin_date, new_values["begin_date"])
        self.assertEqual(changed_thesis.due_date, new_values["due_date"])
        self.assertEqual(changed_thesis.external_where,
                         new_values["external_where"])
        self.assertEqual(changed_thesis.external, new_values["external"])
        self.assertEqual(changed_thesis.student_contact,
                         new_values["student_email"])

    def test_validation_of_required_fields(self):
        """required fields cannot be empty"""
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        status=Thesis.APPLIED)

        new_values = {}

        thesis.save()

        response = self.client.post(
            reverse('change', args=[thesis.surrogate_key]), new_values)

        self.assertEqual(200, response.status_code)
        self.assertIn('title', response.context["form"].errors)
        self.assertIn('begin_date', response.context["form"].errors)
        self.assertIn('due_date', response.context["form"].errors)

    def test_validation_due_date_if_prolonged(self):
        """new due_date cannot be later than prolongation_date"""
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        prolongation_date=date(2018, 4, 30),
                        status=Thesis.APPLIED)

        new_values = {
            'title': 'Ein ganz anderer Titel',
            'begin_date': date(2018, 1, 30),
            'due_date': date(2018, 5, 30),
            'prolongation_date': date(2018, 4, 30)
        }

        thesis.save()

        response = self.client.post(
            reverse('change', args=[thesis.surrogate_key]), new_values)

        self.assertEqual(200, response.status_code)
        self.assertIn('due_date', response.context["form"].errors)
        self.assertTrue(
            'Verlängerung liegt vor der Abgabe' in str(response.context["form"].errors))

    def test_theses_program_does_not_change_after_creation(self):
        """when the student changes his program, the theses_program does not change.
        theses_program is only set when creating a thesis."""
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        status=Thesis.APPLIED)

        self.student.program = "IM"

        new_values = {
            'title': 'Ein ganz anderer Titel',
            'thesis_program': self.student.program,
            'begin_date': date(2019, 1, 30),
            'due_date': date(2018, 3, 30)
        }

        thesis.save()

        response = self.client.post(
            reverse('change', args=[thesis.surrogate_key]), new_values)

        self.assertEqual(200, response.status_code)
        self.assertEqual("IB", thesis.thesis_program)