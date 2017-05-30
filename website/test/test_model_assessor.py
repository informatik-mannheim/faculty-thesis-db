from django.test import TestCase

from website.models import *


class AssessorTests(TestCase):

    def test_create_short_name(self):
        assessor = Assessor(first_name='Peter', last_name='Maier')

        self.assertEqual("P.Maier", assessor.short_name)
