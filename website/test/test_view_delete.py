from django.urls import reverse

from datetime import date
import uuid

from website.models import Thesis
from website.test.test import LoggedInTestCase


class ViewChangeTests(LoggedInTestCase):

    def test_404_if_thesis_not_found(self):
        response_get = self.client.get(reverse('delete', args=[uuid.uuid4()]))
        response_post = self.client.post(reverse('delete', args=[uuid.uuid4()]))

        self.assertEqual(404, response_get.status_code)
        self.assertEqual(404, response_post.status_code)

    def test_thesis_found(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        status=Thesis.APPLIED,
                        restriction_note=False)

        thesis.save()

        response = self.client.get(reverse('delete', args=[thesis.surrogate_key]))
        self.assertEqual(200, response.status_code)

    def test_delete_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        status=Thesis.APPLIED,
                        restriction_note=False)

        thesis.save()

        response = self.client.post(reverse('delete', args=[thesis.surrogate_key]))

        self.assertEqual(302, response.status_code)
        self.assertEqual(Thesis.objects.first(), None)

    def test_delete_graded_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        examination_date=date(2018, 4, 30),
                        status=Thesis.GRADED,
                        restriction_note=False)

        thesis.save()

        response = self.client.post(reverse('delete', args=[thesis.surrogate_key]))

        self.assertEqual(302, response.status_code)
        self.assertEqual(Thesis.objects.first(), thesis)

    def test_delete_handed_in_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        handed_in_date=date(2018, 3, 30),
                        status=Thesis.HANDED_IN,
                        restriction_note=False)

        thesis.save()

        response = self.client.post(reverse('delete', args=[thesis.surrogate_key]))

        self.assertEqual(302, response.status_code)
        self.assertEqual(Thesis.objects.first(), thesis)

    def test_delete_prolonged_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        prolongation_date=date(2018, 4, 30),
                        status=Thesis.PROLONGED,
                        restriction_note=False)

        thesis.save()

        response = self.client.post(reverse('delete', args=[thesis.surrogate_key]))

        self.assertEqual(302, response.status_code)
        self.assertEqual(Thesis.objects.first(), thesis)

    def test_delete_approved_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        status=Thesis.APPLIED,
                        excom_status=Thesis.EXCOM_APPROVED,
                        restriction_note=False)

        thesis.save()

        response = self.client.post(reverse('delete', args=[thesis.surrogate_key]))

        self.assertEqual(302, response.status_code)
        self.assertEqual(Thesis.objects.first(), thesis)

    def test_delete_rejected_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        thesis_program=self.student.program,
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        status=Thesis.APPLIED,
                        excom_status=Thesis.EXCOM_REJECTED,
                        restriction_note=False)

        thesis.save()

        response = self.client.post(reverse('delete', args=[thesis.surrogate_key]))

        self.assertEqual(302, response.status_code)
        self.assertEqual(Thesis.objects.first(), thesis)