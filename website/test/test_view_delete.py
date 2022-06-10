from django.urls import reverse

from datetime import date
import uuid

from website.models import Thesis
from website.test.test import LoggedInTestCase, ThesisStub


class ViewChangeTests(LoggedInTestCase):

    def test_404_if_thesis_not_found(self):
        response_get = self.client.get(reverse('delete', args=[uuid.uuid4()]))
        response_post = self.client.post(reverse('delete', args=[uuid.uuid4()]))

        self.assertEqual(404, response_get.status_code)
        self.assertEqual(404, response_post.status_code)

    def test_delete_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        status=Thesis.APPLIED,
                        restriction_note=False)

        thesis.save()

        self.assertEqual(Thesis.objects.filter(id=thesis.id).first(), thesis)

        response_get = self.client.get(reverse('delete', args=[thesis.surrogate_key]))
        self.assertEqual(200, response_get.status_code)

        response_post = self.client.post(reverse('delete', args=[thesis.surrogate_key]))

        self.assertEqual(302, response_post.status_code)
        self.assertEqual(Thesis.objects.filter(id=thesis.id).first(), None)

    def test_delete_graded_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        status=Thesis.GRADED,
                        restriction_note=False)

        thesis.save()

        self.assertEqual(Thesis.objects.filter(id=thesis.id).first(), thesis)

        response_get = self.client.get(reverse('delete', args=[thesis.surrogate_key]))
        self.assertEqual(302, response_get.status_code)

        response_post = self.client.post(reverse('delete', args=[thesis.surrogate_key]))

        self.assertEqual(302, response_post.status_code)
        self.assertEqual(Thesis.objects.filter(id=thesis.id).first(), thesis)

    def test_delete_handed_in_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        status=Thesis.HANDED_IN,
                        handed_in_date=date(2018, 2, 28),
                        restriction_note=False)

        thesis.save()

        self.assertEqual(Thesis.objects.filter(id=thesis.id).first(), thesis)

        response_get = self.client.get(reverse('delete', args=[thesis.surrogate_key]))
        self.assertEqual(302, response_get.status_code)

        response_post = self.client.post(reverse('delete', args=[thesis.surrogate_key]))

        self.assertEqual(302, response_post.status_code)
        self.assertEqual(Thesis.objects.filter(id=thesis.id).first(), thesis)

    def test_delete_prolonged_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        status=Thesis.PROLONGED,
                        prolongation_date=date(2018, 2, 28),
                        restriction_note=False)

        thesis.save()

        self.assertEqual(Thesis.objects.filter(id=thesis.id).first(), thesis)

        response_get = self.client.get(reverse('delete', args=[thesis.surrogate_key]))
        self.assertEqual(302, response_get.status_code)

        response_post = self.client.post(reverse('delete', args=[thesis.surrogate_key]))

        self.assertEqual(302, response_post.status_code)
        self.assertEqual(Thesis.objects.filter(id=thesis.id).first(), thesis)

    def test_delete_approved_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        status=Thesis.APPLIED,
                        excom_status=Thesis.EXCOM_APPROVED,
                        restriction_note=False)

        thesis.save()

        self.assertEqual(Thesis.objects.filter(id=thesis.id).first(), thesis)

        response_get = self.client.get(reverse('delete', args=[thesis.surrogate_key]))
        self.assertEqual(302, response_get.status_code)

        response_post = self.client.post(reverse('delete', args=[thesis.surrogate_key]))

        self.assertEqual(302, response_post.status_code)
        self.assertEqual(Thesis.objects.filter(id=thesis.id).first(), thesis)

    def test_delete_rejected_thesis(self):
        thesis = Thesis(student=self.student,
                        assessor=self.assessor,
                        supervisor=self.supervisor,
                        title="Eine einzelne Thesis",
                        begin_date=date(2018, 1, 30),
                        due_date=date(2018, 3, 30),
                        status=Thesis.APPLIED,
                        excom_status=Thesis.EXCOM_REJECTED,
                        restriction_note=False)

        thesis.save()

        self.assertEqual(Thesis.objects.filter(id=thesis.id).first(), thesis)

        response_get = self.client.get(reverse('delete', args=[thesis.surrogate_key]))
        self.assertEqual(302, response_get.status_code)

        response_post = self.client.post(reverse('delete', args=[thesis.surrogate_key]))

        self.assertEqual(302, response_post.status_code)
        self.assertEqual(Thesis.objects.filter(id=thesis.id).first(), thesis)