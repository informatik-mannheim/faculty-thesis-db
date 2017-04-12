from unittest import TestCase
from datetime import datetime


from website.util import dateutil


class ThesisModelTests(TestCase):

    def test_get_beginning_of_next_month(self):

        test_dates = [
            (datetime(2017, 1, 1), datetime(2017, 1, 1)),
            (datetime(2017, 1, 2), datetime(2017, 2, 1)),
            (datetime(2017, 1, 15), datetime(2017, 2, 1)),
            (datetime(2017, 1, 30), datetime(2017, 2, 1)),
            (datetime(2017, 1, 31), datetime(2017, 2, 1)),
            (datetime(2017, 2, 28), datetime(2017, 3, 1)),
            (datetime(2017, 12, 31), datetime(2018, 1, 1)),
        ]

        for date in test_dates:
            result = dateutil.next_month_start(date[0])
            self.assertEqual(result, date[1])

    def test_add_months(self):
        now = datetime(2017, 1, 1)
        now_plus_3 = datetime(2017, 3, 31)
        now_plus_6 = datetime(2017, 6, 30)

        then = datetime(2019, 12, 1)
        then_plus_3 = datetime(2020, 2, 29)
        then_plus_6 = datetime(2020, 5, 31)

        self.assertEqual(now_plus_3, dateutil.add_months(3, now))
        self.assertEqual(now_plus_6, dateutil.add_months(6, now))

        self.assertEqual(then_plus_3, dateutil.add_months(3, then))
        self.assertEqual(then_plus_6, dateutil.add_months(6, then))

    def test_get_thesis_period(self):
        start, end = dateutil.get_thesis_period(datetime(2017, 1, 2), 3)

        self.assertEqual(start, datetime(2017, 2, 1))
        self.assertEqual(end, datetime(2017, 4, 30))

        start, end = dateutil.get_thesis_period(datetime(2017, 1, 1), 6)

        self.assertEqual(start, datetime(2017, 1, 1))
        self.assertEqual(end, datetime(2017, 6, 30))
