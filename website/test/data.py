from datetime import datetime

from website.models import *


class ThesisSet(object):

    @classmethod
    def empty(cls):
        return []

    @classmethod
    def single(cls, supervisor):
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
                        due_date=datetime(2018, 1, 30),
                        status=Thesis.PROLONGED)

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
                   due_date=datetime(2018, 1, 30),
                   status=Thesis.PROLONGED)

        b = Thesis(student=student,
                   assessor=assessor,
                   supervisor=supervisor,
                   title="Eine andere Thesis",
                   begin_date=datetime.now().date(),
                   due_date=datetime(2019, 1, 30),
                   status=Thesis.APPLIED)

        c = Thesis(student=student,
                   assessor=assessor,
                   supervisor=supervisor,
                   title="Eine weitere Thesis",
                   begin_date=datetime.now().date(),
                   due_date=datetime(2017, 1, 30),
                   status=Thesis.GRADED)

        a.save()
        b.save()
        c.save()

        return [a, b, c]
