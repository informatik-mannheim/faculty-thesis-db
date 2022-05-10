from django.test import TestCase, Client
from django.urls import reverse

from website.models import Student, User


class ViewFindStudentTests(TestCase):
    databases = {'default', 'faculty'}

    def setUp(self):
        user = User(username="t.smits", password="pass")
        user.save()

        self.client = Client()
        self.client.force_login(user)

        self.student = Student(
            id=123456, first_name="Peter", last_name="Petermann", program="IB")
        self.student.save(using='faculty')

    def test_empty_find_student(self):
        response = self.client.get(reverse('find_student'))

        self.assertEqual(200, response.status_code)
        self.assertEqual(None, response.context['student'])

    def test_post_valid_matrikelnummer(self):
        response = self.client.post(
            reverse('find_student'), {'student_id': '123456'})

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.student, response.context['student'])
        self.assertEqual(True, response.context['form'].is_valid())

    def test_post_invalid_matrikelnummer(self):
        response = self.client.post(
            reverse('find_student'), {'student_id': '000999'})

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context['student'])
        self.assertFalse(response.context['form'].is_valid())
