from django.test import TestCase

from datetime import date, timedelta
from decimal import Decimal

from thesispool.pdf import AbstractPDF
from website.models import *
from website.test.test import ThesisStub


class TestPDF(TestCase):

    def test_fields_that_are_always_populated(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU")
        thesis = ThesisStub.applied(supervisor)
        thesis.student_contact = 'student@example.com'
        thesis.external = True
        thesis.external_where = "Arbeitsamt"
        thesis.grade = Decimal("1.3")
        thesis.handed_in_date = thesis.due_date
        thesis.examination_date = date(2020, 3, 13)
        thesis.restriction_note = True

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()

        date_format = "%d.%m.%Y"

        self.assertEqual(xfdf.fields["Titel"], thesis.title)
        self.assertEqual(xfdf.fields["NameVorname"], thesis.student.last_name + ", " + thesis.student.first_name)
        self.assertEqual(xfdf.fields["BeginnDerArbeit"],
                         thesis.begin_date.strftime(date_format))
        self.assertEqual(xfdf.fields["AbgabeDerArbeit"],
                         thesis.due_date.strftime(date_format))
        self.assertEqual(xfdf.fields["MatrNr"], thesis.student.id)
        self.assertEqual(xfdf.fields["EMail"], thesis.student_contact)
        self.assertEqual(xfdf.fields["Studiengang"], "Fakultät für Informatik / " + thesis.student.program)
        self.assertEqual(
            xfdf.fields["KürzelErstkorrektor"], supervisor.initials)
        self.assertEqual(
            xfdf.fields["NameZweitkorrektor"], thesis.assessor.short_name)
        self.assertEqual(xfdf.fields["AnfertigungFirma"], "On")
        self.assertEqual(xfdf.fields["Note"], "1,3")
        self.assertEqual(xfdf.fields["AbgabeMitVerlängerung"], "Off")
        self.assertEqual(xfdf.fields["AbgabeTermingerecht"], "On")
        self.assertEqual(xfdf.fields["DatumAbgabe"],
                         thesis.handed_in_date.strftime(date_format))
        self.assertEqual(xfdf.fields["DatumKolloquium"],
                         thesis.examination_date.strftime(date_format))
        self.assertEqual(xfdf.fields["Sperrvermerk"], "On")

    def test_thesis_internal(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU")
        thesis = ThesisStub.applied(supervisor)
        thesis.external = False
        thesis.external_where = ''

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()

        self.assertEqual(xfdf.fields["AnfertigungFirma"], "Off")
        self.assertNotIn('Firma', xfdf.fields)

    def test_no_assessor(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU")
        thesis = ThesisStub.applied(supervisor)
        thesis.assessor = None

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()

        self.assertNotIn('NameZweitkorrektor', xfdf.fields)

    def test_no_grade(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU")
        thesis = ThesisStub.applied(supervisor)

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()

        self.assertNotIn('Note', xfdf.fields)

    def test_prolonged_thesis(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU", id="mmuster")
        supervisor.save()
        thesis = ThesisStub.applied(supervisor)
        thesis.save()
        thesis.prolong(thesis.due_date + timedelta(30), "Weil", 4)

        date_format = "%d.%m.%Y"

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()

        self.assertEqual(xfdf.fields['AbgabeMitVerlängerung'], 'On')
        self.assertEqual(
            xfdf.fields['BegründungVerlängerung'], thesis.prolongation_reason)
        self.assertEqual(
            xfdf.fields['VerlängerungUmWochen'], thesis.prolongation_weeks)
        self.assertEqual(xfdf.fields['DatumAbgabeNeu'],
                         thesis.prolongation_date.strftime(date_format))

    def test_late_thesis(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU", id="mmuster")
        supervisor.save()
        thesis = ThesisStub.applied(supervisor)
        thesis.begin_date = date(2018, 1, 1)
        thesis.due_date = date(2018, 3, 1)
        thesis.handed_in_date = date(2018, 3, 2)
        thesis.save()

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()

        self.assertEqual(xfdf.fields['AbgabeTermingerecht'], 'Off')
        self.assertEqual(xfdf.fields['AbgabeVerspätet'], 'On')

    def test_no_restriction_note(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU", id="mmuster")
        supervisor.save()
        thesis = ThesisStub.applied(supervisor)
        thesis.restriction_note = False
        thesis.save()

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()

        self.assertEqual(xfdf.fields['Sperrvermerk'], 'Off')
