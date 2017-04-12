from django.test import TestCase
from django.test.utils import setup_test_environment

from website.models import *


setup_test_environment()


class AssessorTests(TestCase):

    def test_create_short_name(self):
        assessor = Assessor(first_name='Peter', last_name='Maier')

        self.assertEqual("P.Maier", assessor.short_name)
