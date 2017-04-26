from django.test import TestCase, Client
from website.models import *

from datetime import date, datetime


class ThesisStub(object):

    @classmethod
    def empty(cls):
        return []

    @classmethod
    def applied(cls, supervisor):
        student = Student(id=987654,
                          first_name="Larry",
                          last_name="Langzeitstudent")

        assessor = Assessor(first_name="Hansi",
                            last_name="Schmidt",
                            email="h.schmidt@example.com")

        student.save()
        assessor.save()

        thesis = Thesis(student=student,
                        assessor=assessor,
                        supervisor=supervisor,
                        title="Eine einzelne Thesis",
                        begin_date=datetime.now().date(),
                        due_date=date(2018, 1, 30),
                        status=Thesis.APPLIED)

        return thesis

    @classmethod
    def small(cls, supervisor):
        student = Student(id=123456,
                          first_name="Max",
                          last_name="Musterstudent")

        assessor = Assessor(first_name="Peter",
                            last_name="Maier",
                            email="p.maier@example.com")

        student.save()
        assessor.save()

        a = Thesis(student=student,
                   assessor=assessor,
                   supervisor=supervisor,
                   title="Eine Thesis",
                   begin_date=datetime.now().date(),
                   due_date=date(2018, 1, 30),
                   status=Thesis.PROLONGED)

        b = Thesis(student=student,
                   assessor=assessor,
                   supervisor=supervisor,
                   title="Eine andere Thesis",
                   begin_date=datetime.now().date(),
                   due_date=date(2019, 1, 30),
                   status=Thesis.APPLIED)

        c = Thesis(student=student,
                   assessor=assessor,
                   supervisor=supervisor,
                   title="Eine weitere Thesis",
                   begin_date=datetime.now().date(),
                   due_date=date(2017, 1, 30),
                   status=Thesis.GRADED)

        a.save()
        b.save()
        c.save()

        return [a, b, c]


class LoggedInTestCase(TestCase):

    def setUp(self):
        user = User(username="prof", password="pass", initials="PPP")
        user.save()

        self.student = Student(
            id=123456, first_name="Larry", last_name="Langzeitstudent")
        self.assessor = Assessor(
            first_name="Max", last_name="Mustermann", email="mm@example.com")
        self.supervisor = Supervisor(
            first_name="Peter", last_name="Professpr", id=user.username)

        self.supervisor.save()
        self.student.save()
        self.assessor.save()

        self.client = Client()
        self.client.force_login(user)
