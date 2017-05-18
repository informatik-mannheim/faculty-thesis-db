from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.urls import reverse

from datetime import datetime

from website.models import Student, Thesis, User, Supervisor


setup_test_environment()


class ViewCreateTests(TestCase):

    def send(self, post_data):
        return self.client.post(
            reverse('create', args=['123456']), post_data)

    def setUp(self):
        user = User(username="t.smits", password="pass", initials="SHO")
        user.save()

        self.client = Client()
        self.client.force_login(user)

        self.student = Student(
            id=123456, first_name="Peter", last_name="Petermann", program="IB")
        self.student.save(using='faculty')

    def test_empty_create_view(self):
        response = self.client.get(reverse('create', args=['123456']))

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["student"], self.student)

    def test_can_have_no_assessor(self):
        post_data = {
            'title': 'A wonderful title',
            'begin_date_day': '1',
            'begin_date_month': '3',
            'begin_date_year': '2017',
            'due_date_day': '1',
            'due_date_month': '6',
            'due_date_year': '2017',
            'external_where': 'Alstom',
            'student_email': 'student@example.com'
        }

        response = self.send(post_data)

        self.assertEqual(302, response.status_code)
        self.assertEqual(1, Thesis.objects.count())
        self.assertFalse(Thesis.objects.first().assessor)

    def test_must_provide_complete_assessor_first_name(self):
        post_data = {
            'first_name': 'Horst',
        }

        response = self.send(post_data)

        assessor_form = response.context["a_form"]

        self.assertEqual(200, response.status_code)
        self.assertFalse(assessor_form.is_valid())
        self.assertTrue(
            'Zweitkorrektor unvollständig' in assessor_form.errors['__all__'])
        self.assertFalse(Thesis.objects.count())

    def test_must_provide_complete_assessor_last_name(self):
        post_data = {
            'last_name': 'Schneider',
        }

        response = self.send(post_data)

        assessor_form = response.context["a_form"]

        self.assertEqual(200, response.status_code)
        self.assertFalse(assessor_form.is_valid())
        self.assertTrue(
            'Zweitkorrektor unvollständig' in assessor_form.errors['__all__'])
        self.assertFalse(Thesis.objects.count())

    def test_must_provide_complete_assessor_email(self):
        post_data = {
            'email': 'h.schneider@example.com',
        }

        response = self.send(post_data)

        assessor_form = response.context["a_form"]

        self.assertEqual(200, response.status_code)
        self.assertFalse(assessor_form.is_valid())
        self.assertTrue(
            'Zweitkorrektor unvollständig' in assessor_form.errors['__all__'])
        self.assertFalse(Thesis.objects.count())

    def test_must_provide_valid_begin_date(self):
        post_data = {
            'title': 'A title',
            'first_name': 'Horst',
            'last_name': 'Schneider',
            'email': 'h.schneider@example.com',
            'begin_date_day': '31',
            'begin_date_month': '2',
            'begin_date_year': '2017',
            'external_where': 'Alstom',
            'student_email': 'student@example.com'
        }

        response = self.send(post_data)

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["form"].is_valid())
        self.assertTrue('begin_date' in response.context["form"].errors.keys())
        self.assertFalse(Thesis.objects.count())

    def test_must_provide_valid_due_date(self):
        post_data = {
            'title': 'A title',
            'first_name': 'Horst',
            'last_name': 'Schneider',
            'email': 'h.schneider@example.com',
            'begin_date_day': '20',
            'begin_date_month': '2',
            'begin_date_year': '2017',
            'due_date_day': '100',
            'due_date_month': '6',
            'due_date_year': '2017',
            'external_where': 'Alstom',
            'student_email': 'student@example.com'
        }

        response = self.send(post_data)

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["form"].is_valid())
        self.assertTrue('due_date' in response.context["form"].errors.keys())
        self.assertFalse(Thesis.objects.count())

    def test_must_provide_due_date_after_start_date(self):
        post_data = {
            'title': 'A title',
            'first_name': 'Horst',
            'last_name': 'Schneider',
            'email': 'h.schneider@example.com',
            'begin_date_day': '1',
            'begin_date_month': '6',
            'begin_date_year': '2017',
            'due_date_day': '1',
            'due_date_month': '5',
            'due_date_year': '2017',
            'external_where': 'Alstom',
            'student_email': 'student@example.com'
        }

        response = self.send(post_data)

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["form"].is_valid())
        self.assertTrue('due_date' in response.context["form"].errors.keys())
        self.assertFalse(Thesis.objects.count())

    def test_must_provide_a_title(self):
        post_data = {
            'title': '',
            'first_name': 'Horst',
            'last_name': 'Schneider',
            'email': 'h.schneider@example.com',
            'begin_date_day': '1',
            'begin_date_month': '3',
            'begin_date_year': '2017',
            'due_date_day': '1',
            'due_date_month': '6',
            'due_date_year': '2017',
            'external_where': 'Alstom',
            'student_email': 'student@example.com'
        }

        response = self.send(post_data)

        self.assertEqual(200, response.status_code)
        self.assertTrue('title' in response.context["form"].errors.keys())
        self.assertFalse(response.context["form"].is_valid())
        self.assertFalse(Thesis.objects.count())

    def test_create_thesis_with_all_form_values(self):
        post_data = {
            'title': "Ein Titel",
            'first_name': 'Horst',
            'last_name': 'Schneider',
            'email': 'h.schneider@example.com',
            'begin_date_day': '1',
            'begin_date_month': '3',
            'begin_date_year': '2017',
            'due_date_day': '1',
            'due_date_month': '6',
            'due_date_year': '2017',
            'external_where': 'Alstom',
            'student_email': 'student@example.com'
        }

        response = self.send(post_data)

        self.assertEqual(302, response.status_code)

        thesis = Thesis.objects.first()

        self.assertEqual(post_data["title"], thesis.title)
        self.assertEqual(post_data["first_name"], thesis.assessor.first_name)
        self.assertEqual(post_data["last_name"], thesis.assessor.last_name)
        self.assertEqual(post_data["email"], thesis.assessor.email)
        self.assertEqual(post_data["student_email"], thesis.student_contact)
        self.assertEqual(post_data["external_where"], thesis.external_where)
        self.assertEqual(datetime(2017, 3, 1).date(), thesis.begin_date)
        self.assertEqual(datetime(2017, 6, 1).date(), thesis.due_date)

    def test_create_student_mail_if_none_provided(self):
        post_data = {
            'title': "Ein Titel",
            'first_name': 'Horst',
            'last_name': 'Schneider',
            'email': 'h.schneider@example.com',
            'begin_date_day': '1',
            'begin_date_month': '3',
            'begin_date_year': '2017',
            'due_date_day': '1',
            'due_date_month': '6',
            'due_date_year': '2017',
            'external_where': 'Alstom',
            'student_email': ''
        }

        response = self.send(post_data)

        self.assertEqual(302, response.status_code)

        thesis = Thesis.objects.first()

        self.assertEqual(post_data["title"], thesis.title)
        self.assertEqual(post_data["first_name"], thesis.assessor.first_name)
        self.assertEqual(post_data["last_name"], thesis.assessor.last_name)
        self.assertEqual(post_data["email"], thesis.assessor.email)
        self.assertEqual(self.student.email, thesis.student_contact)
        self.assertEqual(post_data["external_where"], thesis.external_where)
        self.assertEqual(datetime(2017, 3, 1).date(), thesis.begin_date)
        self.assertEqual(datetime(2017, 6, 1).date(), thesis.due_date)

    def test_headlines_differ_for_bachelor_and_master(self):
        bachelor = Student(id=123, first_name="A", last_name="B", program='IB')
        master = Student(id=456, first_name="C", last_name="D", program='IM')

        bachelor.save(using='faculty')
        master.save(using='faculty')

        response_bachelor = self.client.get(reverse('create', args=['123']))
        response_master = self.client.get(reverse('create', args=['456']))

        self.assertEqual(200, response_bachelor.status_code)
        self.assertEqual(200, response_master.status_code)
        self.assertEqual(response_bachelor.context[
                         "headline"], "Bachelorthesis anlegen")
        self.assertEqual(response_master.context[
                         "headline"], "Masterthesis anlegen")

    def test_supervisor_choices_for_sekretariat(self):
        user = User(username="t.sekretariat", password="pass", initials="SEK")

        user.is_secretary = True
        user.save()

        client = Client()
        client.force_login(user)

        response = client.get(reverse('create', args=['123456']))

        self.assertEqual(200, response.status_code)
        self.assertIn("s_form", response.context)
        self.assertIsNone(response.context["supervisor"])

    def test_supervisor_choice_is_validated(self):
        user = User(username="t.sekretariat", password="pass", initials="SEK")

        user.is_secretary = True
        user.save()

        client = Client()
        client.force_login(user)

        post_data = {'title': 'eine thesis', 'supervisors': 'not.existant'}

        response = client.post(reverse('create', args=['123456']), post_data)

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["s_form"].is_valid())
        self.assertIn("supervisors", response.context["s_form"].errors)

    def test_supervisor_choice_is_attached_to_thesis(self):
        user = User(username="t.sekretariat", password="pass", initials="SEK")

        user.is_secretary = True
        user.save()

        client = Client()
        client.force_login(user)

        post_data = {
            'title': "Ein Titel",
            'first_name': 'Horst',
            'last_name': 'Schneider',
            'email': 'h.schneider@example.com',
            'begin_date_day': '1',
            'begin_date_month': '3',
            'begin_date_year': '2017',
            'due_date_day': '1',
            'due_date_month': '6',
            'due_date_year': '2017',
            'external_where': 'Alstom',
            'student_email': ''
        }

        post_data["supervisors"] = "t.prof"

        response = client.post(reverse('create', args=['123456']), post_data)

        self.assertEqual(302, response.status_code)

        thesis = Thesis.objects.first()

        all_supervisors = Supervisor.objects.fetch_supervisors_from_ldap()

        self.assertIn(thesis.supervisor, all_supervisors)
