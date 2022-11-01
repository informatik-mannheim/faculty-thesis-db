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

    def test_post_valid_matrikelnummer_in_faculty(self):
        response = self.client.post(
            reverse('find_student'), {'student_id': '123456'})

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.student, response.context['student'])
        self.assertTrue(response.context['form'].is_valid())

    def test_post_valid_matrikelnummer_in_default(self):
        student = Student(id=987654, first_name="Linus", last_name="Kanstein", program="IB")
        student.save(using='default')

        response = self.client.post(
            reverse('find_student'), {'student_id': '987654'})

        self.assertEqual(200, response.status_code)
        self.assertEqual(student, response.context['student'])
        self.assertTrue(response.context['form'].is_valid())

    def test_post_invalid_matrikelnummer(self):
        response = self.client.post(
            reverse('find_student'), {'student_id': '000999'})

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context['student'])
        self.assertFalse(response.context['form'].is_valid())

    def test_empty_create_view_get(self):
        response = self.client.get(reverse('find_student'))

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["s_form"].is_valid())

    def test_empty_create_view_post(self):
        post_data = {}
        response = self.client.post(reverse('find_student'), post_data)

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["s_form"].is_valid())

    def test_with_bachelor_program(self):
        post_data = {
            "id": 654321,
            "first_name": "Linus",
            "last_name": "Kanstein",
            "program": "IJB"
        }

        response = self.client.post(reverse('find_student'), post_data)

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, Student.objects.count())

    def test_with_master_program(self):
        post_data = {
            "id": 654321,
            "first_name": "Linus",
            "last_name": "Kanstein",
            "program": "IMM"
        }

        response = self.client.post(reverse('find_student'), post_data)

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, Student.objects.count())

    def test_invalid_with_missing_id(self):
        post_data = {
            "first_name": "Linus",
            "last_name": "Kanstein",
            "program": "IJB"
        }

        response = self.client.post(reverse('find_student'), post_data)

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["s_form"].is_valid())
        self.assertEqual(0, Student.objects.count())

    def test_invalid_with_missing_first_name(self):
        post_data = {
            "id": 654321,
            "last_name": "Kanstein",
            "program": "IJB"
        }

        response = self.client.post(reverse('find_student'), post_data)

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["s_form"].is_valid())
        self.assertEqual(0, Student.objects.count())

    def test_invalid_with_missing_last_name(self):
        post_data = {
            "id": 654321,
            "first_name": "Linus",
            "program": "IB"
        }

        response = self.client.post(reverse('find_student'), post_data)

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["s_form"].is_valid())
        self.assertEqual(0, Student.objects.count())

    def test_invalid_with_missing_program(self):
        post_data = {
            "id": 654321,
            "first_name": "Linus",
            "last_name": "Kanstein",
        }

        response = self.client.post(reverse('find_student'), post_data)

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["s_form"].is_valid())
        self.assertEqual(0, Student.objects.count())

    def test_invalid_if_error_in_program(self):
        for program in ["IE", "B", "IB", "IM", "CSB", "UIB", "IMB", "1IB", "_IB"]:
            post_data = {
                "id": 654321,
                "first_name": "Linus",
                "last_name": "Kanstein",
                "program": program
            }

            response = self.client.post(reverse('find_student'), post_data)

            self.assertEqual(200, response.status_code)
            self.assertFalse(response.context["s_form"].is_valid())
            self.assertEqual(0, Student.objects.count())

    def test_invalid_when_id_already_used_in_faculty(self):
        post_data = {
            "id": 123456,
            "first_name": "Linus",
            "last_name": "Kanstein",
            "program": "IB"
        }

        response = self.client.post(reverse('find_student'), post_data)

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["s_form"].is_valid())

        # count does not work on faculty db
        self.assertEqual(0, Student.objects.count())

    def test_invalid_when_id_already_used_in_default(self):
        student = Student(id=98765, first_name="Peter", last_name="Petermann", program="IB")
        student.save(using='default')

        post_data = {
            "id": 98765,
            "first_name": "Linus",
            "last_name": "Kanstein",
            "program": "IB"
        }

        response = self.client.post(reverse('find_student'), post_data)

        self.assertEqual(200, response.status_code)
        self.assertFalse(response.context["s_form"].is_valid())
        self.assertEqual(1, Student.objects.count())
