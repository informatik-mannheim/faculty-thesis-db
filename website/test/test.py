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
                          last_name="Langzeitstudent",
                          program="IB")

        assessor = Assessor(first_name="Hansi",
                            last_name="Schmidt",
                            email="h.schmidt@example.com")

        student.save()
        assessor.save()

        thesis = Thesis(student=student,
                        assessor=assessor,
                        supervisor=supervisor,
                        title="Eine einzelne Thesis",
                        thesis_program=student.program,
                        begin_date=datetime.now().date(),
                        due_date=date(2018, 1, 30),
                        status=Thesis.APPLIED,
                        restriction_note = False)

        return thesis

    @classmethod
    def small(cls, supervisor):
        student = Student(id=123456,
                          first_name="Max",
                          last_name="Musterstudent",
                          program="IB")

        assessor = Assessor(first_name="Peter",
                            last_name="Maier",
                            email="p.maier@example.com")

        student.save()
        assessor.save()

        a = Thesis(student=student,
                   assessor=assessor,
                   supervisor=supervisor,
                   title="Eine Thesis",
                   thesis_program=student.program,
                   begin_date=datetime.now().date(),
                   due_date=date(2018, 1, 30),
                   status=Thesis.PROLONGED)

        b = Thesis(student=student,
                   assessor=assessor,
                   supervisor=supervisor,
                   title="Eine andere Thesis",
                   thesis_program=student.program,
                   begin_date=datetime.now().date(),
                   due_date=date(2019, 1, 30),
                   status=Thesis.APPLIED)

        c = Thesis(student=student,
                   assessor=assessor,
                   supervisor=supervisor,
                   title="Eine weitere Thesis",
                   thesis_program=student.program,
                   begin_date=datetime.now().date(),
                   due_date=date(2017, 1, 30),
                   status=Thesis.GRADED)

        a.save()
        b.save()
        c.save()

        return [a, b, c]


class LoggedInTestCase(TestCase):

    def setUp(self):
        self.user = User(username="prof", password="pass", initials="PPP")
        self.user.save()

        self.student = Student(
            id=123456, first_name="Larry", last_name="Langzeitstudent", program="IB")
        self.assessor = Assessor(
            first_name="Max", last_name="Mustermann", email="mm@example.com")
        self.supervisor = Supervisor(
            first_name="Peter", last_name="Professpr", id=self.user.username)

        self.supervisor.save()
        self.student.save()
        self.assessor.save()

        self.client = Client()
        self.client.force_login(self.user)
