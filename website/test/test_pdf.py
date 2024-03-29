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

        self.assertEqual(xfdf.fields["Auswahl_Arbeit"], "0")
        self.assertEqual(xfdf.fields["Wahlt_Arbeit"], "Bachelor")
        self.assertEqual(xfdf.fields["Thema_der_Arbeit"], thesis.title)
        self.assertEqual(xfdf.fields["Kurztitel der Arbeit"], thesis.title)
        self.assertEqual(xfdf.fields["Name, Vorname"], thesis.student.last_name + ", " + thesis.student.first_name)
        self.assertEqual(xfdf.fields["Beginn der Arbeit"], thesis.begin_date.strftime(date_format))
        self.assertEqual(xfdf.fields["Beginn_Arbeit"], thesis.begin_date.strftime(date_format))
        self.assertEqual(xfdf.fields["Abgabedatum"], thesis.due_date.strftime(date_format))
        self.assertEqual(xfdf.fields["Ende_Arbeit"], thesis.due_date.strftime(date_format))
        self.assertEqual(xfdf.fields["Datum_urspruengliche_Abgabe"], thesis.due_date.strftime(date_format))
        self.assertEqual(xfdf.fields["Matrikelnr"], str(thesis.student.id))
        self.assertEqual(xfdf.fields["Matrikelnummer"], str(thesis.student.id))
        self.assertEqual(xfdf.fields["Email"], thesis.student_contact)
        self.assertEqual(xfdf.fields["Fakultät Studiengang"], "Fakultät für Informatik / " + thesis.thesis_program)
        self.assertEqual(xfdf.fields["Fakultät_Studiengang"], "Fakultät für Informatik / " + thesis.thesis_program)
        self.assertEqual(xfdf.fields["Kurzzeichen_Fakultät"], "I")
        self.assertEqual(xfdf.fields["Fakultät"], "I")
        self.assertEqual(xfdf.fields["Kurzzeichen1"], supervisor.initials)
        self.assertEqual(xfdf.fields["Kurzzeichen_erst"], supervisor.initials)
        self.assertEqual(xfdf.fields["Kurzzeichen_Prof"], supervisor.initials)
        self.assertEqual(xfdf.fields["Name Erstprüfer"], supervisor.short_name)
        self.assertEqual(xfdf.fields["Hochschullehrer/in"], supervisor.short_name)

        self.assertEqual(xfdf.fields["Ort_der_Arbeit"], "außer_Hause")
        self.assertEqual(xfdf.fields["Adresse_der_Firma"], thesis.external_where)

        self.assertEqual(xfdf.fields["Note Erstprüfer"], "1,3")
        self.assertEqual(xfdf.fields["Gesamtnote"], "1,3")

        self.assertEqual(xfdf.fields["auswählen"], "0")

        self.assertEqual(xfdf.fields["Datum Kolloquium"], thesis.examination_date.strftime(date_format))
        self.assertEqual(xfdf.fields["Mit Note"], "1")

    def test_thesis_internal(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU")
        thesis = ThesisStub.applied(supervisor)
        thesis.external = False

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()

        self.assertEqual(xfdf.fields["Ort_der_Arbeit"], "im Hause")
        self.assertNotIn("Adresse_der_Firma", xfdf.fields)

    def test_no_assessor(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU")
        thesis = ThesisStub.applied(supervisor)
        thesis.assessor = None

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()

        self.assertNotIn("Name Zweitprüfer", xfdf.fields)
        self.assertNotIn("Zweitkorrektor/in", xfdf.fields)
        self.assertNotIn("assessor_grade", xfdf.fields)
        
    def test_has_assessor_with_title(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU")
        thesis = ThesisStub.applied(supervisor)
        thesis.assessor = Assessor(
            first_name="Meier", last_name="Mannfred", email="m.mannfred@example.com", academic_title="Dr.")

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()
        
        self.assertEqual(xfdf.fields["Name Zweitprüfer"], thesis.assessor.short_name + ', ' + thesis.assessor.academic_title)
        self.assertEqual(xfdf.fields["Zweitkorrektor/in"], thesis.assessor.short_name + ', ' + thesis.assessor.academic_title)

    def test_no_grade(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU")
        thesis = ThesisStub.applied(supervisor)

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()

        self.assertNotIn('Note Erstprüfer', xfdf.fields)
        self.assertNotIn('Gesamtnote', xfdf.fields)

    def test_prolonged_thesis(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU", id="mmuster")
        supervisor.save()
        thesis = ThesisStub.applied(supervisor)
        thesis.save()
        thesis.prolong(thesis.due_date + timedelta(30), "Weil", 4)

        date_format = "%d.%m.%Y"

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()

        self.assertEqual(xfdf.fields['auswählen'], '1')
        self.assertEqual(
            xfdf.fields['Begründung_Antrag'], thesis.prolongation_reason)
        self.assertEqual(
            xfdf.fields['Symtome / Auswirkung'], thesis.prolongation_reason)
        self.assertEqual(
            xfdf.fields['Zeitraum_Verlängerung'], str(thesis.prolongation_weeks))
        self.assertEqual(
            xfdf.fields['Zeitraum'], "Wochen")
        self.assertEqual(xfdf.fields['Datum_neue_Abgabe'],
                         thesis.prolongation_date.strftime(date_format))
        self.assertEqual(xfdf.fields['Datum_neuer Abgabetermin'],
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

        self.assertEqual(xfdf.fields['auswählen'], '2')

    def test_special_case_bewertung(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU", id="mmuster")
        supervisor.save()
        thesis = ThesisStub.applied(supervisor)
        thesis.save()
        thesis.prolong(thesis.due_date + timedelta(30), "Weil", 4)

        xfdf = AbstractPDF(thesis, "bewertung")._generate_xfdf()

        date_format = "%d.%m.%Y"

        self.assertEqual(xfdf.fields['Ort_der_Arbeit'], '1')
        self.assertEqual(xfdf.fields['Datum'], thesis.prolongation_date.strftime(date_format))

    def test_assesor_grade(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU")
        thesis = ThesisStub.applied(supervisor)
        thesis.student_contact = 'student@example.com'
        thesis.grade = Decimal("1.3")
        thesis.assessor_grade = Decimal("1.7")
        thesis.handed_in_date = thesis.due_date
        thesis.examination_date = date(2020, 3, 13)
        thesis.restriction_note = True

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()

        self.assertEqual(xfdf.fields["Note Zweitprüfer"], "1,7")

    def test_full_grade(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU")
        thesis = ThesisStub.applied(supervisor)
        thesis.student_contact = 'student@example.com'
        thesis.grade = Decimal("1.3")
        thesis.assessor_grade = Decimal("1.4")
        thesis.handed_in_date = thesis.due_date
        thesis.examination_date = date(2020, 3, 13)

        thesis2 = ThesisStub.applied(supervisor)
        thesis2.student_contact = 'student@example.com'
        thesis2.grade = Decimal("1.4")
        thesis2.assessor_grade = Decimal("1.4")
        thesis2.handed_in_date = thesis.due_date
        thesis2.examination_date = date(2020, 3, 13)

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()
        xfdf2= AbstractPDF(thesis2, "gibtsnich")._generate_xfdf()


        self.assertEqual(xfdf.fields["Gesamtnote"], "1,3")
        self.assertEqual(xfdf2.fields["Gesamtnote"], "1,4")

    def test_entity_replacement(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU")
        thesis = ThesisStub.applied(supervisor)
        thesis.title = '<&"\'>Test'

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()

        self.assertEqual(xfdf.fields["Thema_der_Arbeit"], "&lt;&amp;&quot;&apos;&gt;Test")

    def test_old_thesis_master_student(self):
        supervisor = Supervisor(
            first_name="Max", last_name="Muster", initials="MMU")
        thesis = ThesisStub.applied(supervisor)
        thesis.student.program = 'IM'

        xfdf = AbstractPDF(thesis, "gibtsnich")._generate_xfdf()

        self.assertEqual(thesis.student.program, "IM")
        self.assertEqual(xfdf.fields["Fakultät Studiengang"], "Fakultät für Informatik / " + "IB")
