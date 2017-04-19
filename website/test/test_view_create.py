from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from website.models import User
from django.urls import reverse

from website.models import Student


setup_test_environment()


class ViewCreateStepOneTests(TestCase):

    def setUp(self):
        user = User(username="t.smits", password="pass")
        user.save()

        self.client = Client()
        self.client.force_login(user)

        self.student = Student(
            id=123456, first_name="Peter", last_name="Petermann", program="IB")
        self.student.save(using='faculty')

    def test_empty_step_one(self):
        response = self.client.get(reverse('create_step_one'))

        self.assertEqual(200, response.status_code)
        self.assertEqual(None, response.context['student'])

    def test_post_valid_matrikelnummer(self):
        response = self.client.post(
            reverse('create_step_one'), {'student_id': '123456'})

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.student, response.context['student'])
        self.assertEqual(True, response.context['form'].is_valid())

    def test_post_invalid_matrikelnummer(self):
        response = self.client.post(
            reverse('create_step_one'), {'student_id': '000999'})

        self.assertEqual(200, response.status_code)
        self.assertEqual(None, response.context['student'])
        self.assertEqual(False, response.context['form'].is_valid())


class ViewCreateStepTwoTests(TestCase):

    def setUp(self):
        user = User(username="t.smits", password="pass")
        user.save()

        self.client = Client()
        self.client.force_login(user)

        self.student = Student(
            id=123456, first_name="Peter", last_name="Petermann", program="IB")
        self.student.save(using='faculty')

    def test_empty_step_two(self):
        response = self.client.get(reverse('create_step_two', args=['123456']))

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["student"], self.student)

    def test_validation_stuff(self):
        response = self.client.get(reverse('create_step_two', args=['123456']))

        self.assertEqual(202, response.status_code,
                         "Hier noch vieel mehr testen!")
