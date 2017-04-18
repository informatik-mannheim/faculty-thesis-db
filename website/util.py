from dateutil.relativedelta import relativedelta


class dateutil(object):

    @staticmethod
    def next_month_start(date):
        if date.day == 1:
            return date

        return (date + relativedelta(months=1)).replace(day=1)

    @staticmethod
    def add_months(number, date):
        return date + relativedelta(months=number, days=-1)

    @staticmethod
    def get_thesis_period(date, student):
        months = 3 if student.is_bachelor() else 6
        start = dateutil.next_month_start(date)
        end = dateutil.add_months(months, start)

        return (start, end)
