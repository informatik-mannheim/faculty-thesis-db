from django.test import TestCase
from django.test.utils import setup_test_environment

from website.models import *


setup_test_environment()


class StudentTests(TestCase):

    def create_test_student(self, program):
        return Student(id=123456,
                       first_name="Max",
                       last_name="Mustermann",
                       program=program)

    def test_is_master(self):
        self.assertTrue(self.create_test_student('IM').is_master())
        self.assertFalse(self.create_test_student('IB').is_master())
        self.assertFalse(self.create_test_student('UIB').is_master())
        self.assertFalse(self.create_test_student('MEB').is_master())
        self.assertFalse(self.create_test_student('IMB').is_master())
        self.assertFalse(self.create_test_student('EMLB').is_master())
        self.assertFalse(self.create_test_student('MTB').is_master())
        self.assertFalse(self.create_test_student('WI').is_master())

    def test_is_bachelor(self):
        self.assertFalse(self.create_test_student('IM').is_bachelor())
        self.assertTrue(self.create_test_student('IB').is_bachelor())
        self.assertTrue(self.create_test_student('UIB').is_bachelor())
        self.assertTrue(self.create_test_student('MEB').is_bachelor())
        self.assertTrue(self.create_test_student('IMB').is_bachelor())
        self.assertTrue(self.create_test_student('EMLB').is_bachelor())
        self.assertTrue(self.create_test_student('MTB').is_bachelor())
        self.assertTrue(self.create_test_student('WI').is_bachelor())
