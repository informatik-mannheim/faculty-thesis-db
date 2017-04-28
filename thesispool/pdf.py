#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import tempfile
import os
from thesispool.settings import BASE_DIR
from datetime import datetime


class XFDF(object):
    """Generate XFDF files to populate PDF forms with data.

    Form data on PDF files can be populated by using one of these formats:
    - FDF (File Data Format)
    - XFDF (XML Forms Data Format)

    XFDF is an XML format and utf-8 by default. Prefer this to FDF if possible.

    The generated XFDF file can be applied to an existig PDF file
    with severaldifferent tools, e.g. pdftk.
    """

    def __init__(self, checkbox_yes):
        """Initialize with a positive value for checkboxes(as it may vary)"""
        self.fields = {}
        self._checkbox_yes = checkbox_yes

    def _footer(self):
        footer = '\n</fields>\n' \
                 '<f href="test.pdf"/>\n' \
                 '</xfdf>'

        return footer

    def _header(self):
        header = '<?xml version="1.0" encoding="UTF-8"?>\n' \
            '<xfdf xmlns="http://ns.adobe.com/xfdf/" xml:space="preserve">\n' \
            '<fields>\n'
        return header

    def _fields(self):

        field_str = '<field name="{0}">\n' \
                    '<value>{1}</value>\n' \
                    '</field>'
        fields = [field_str.format(t, v) for t, v in self.fields.items()]
        return "\n".join(fields)

    def add_field(self, key, value):
        self.fields[key] = value

    def check(self, field):
        self.fields[field] = self._checkbox_yes

    def uncheck(self, field):
        self.fields[field] = "Off"

    def generate(self):
        return self._header() + self._fields() + self._footer()


class PDFInfo(object):

    def __init__(self, path, filename):
        self.path = path
        self.filename = filename


class AbstractPDF(object):
    """Base class to populate empty pdf forms with form data.

    Override with name of form that should be used for populating
    form fields with data from the thesis instance.
    """
    TMP_DIR = "/tmp/thesispool"
    BASE_PDF = os.path.join(BASE_DIR, 'website/pdf/{0}.pdf')

    def __init__(self, thesis, form_name):
        self.thesis = thesis
        self.form_name = form_name
        self.input_pdf_path = self.BASE_PDF.format(self.form_name)
        self.__generated_pdf = None

    def get(self):
        return self.__generate_pdf()

    def __generate_pdf(self):
        """Generate PDF file from Thesis instance.

        Creates an XFDF file with all fields populated from a Thesis
        instance and runs pdftk to merge it with the base PDF to fill
        all form fields. Result is written to tempdir.

        Returns the absolute path of the generated pdf without suffix.
        """
        if not self.__generated_pdf:
            self.__ensure_temp_dir_exists()

            xfdf = self._generate_xfdf()
            xfdf_path = self.__write_xfdf_to_tmp(xfdf)

            self.__generated_pdf = self.__run_pdftk(xfdf_path)

        return self.__generated_pdf

    def __ensure_temp_dir_exists(self):
        os.makedirs(self.TMP_DIR, exist_ok=True)

    def _generate_xfdf(self):
        """Generate XFDF data used in PDF form data population"""
        xfdf = XFDF("On")

        xfdf.add_field("Vorname", self.thesis.student.first_name)
        xfdf.add_field("Name", self.thesis.student.last_name)
        xfdf.add_field("BeginnDerArbeit",
                       self.__date_format(self.thesis.begin_date))
        xfdf.add_field("AbgabeDerArbeit",
                       self.__date_format(self.thesis.due_date))
        xfdf.add_field("MatrNr", self.thesis.student.id)
        xfdf.add_field("Titel", self.thesis.title)
        xfdf.add_field("EMail", self.thesis.student_contact)
        xfdf.add_field("Studiengang", self.thesis.student.program)
        xfdf.add_field("KürzelErstkorrektor", self.thesis.supervisor.initials)

        if self.thesis.assessor:
            xfdf.add_field("NameZweitkorrektor",
                           self.thesis.assessor.short_name)

        if self.thesis.external:
            xfdf.check("AnfertigungFirma")
        else:
            xfdf.uncheck("AnfertigungFirma")
            xfdf.check("AnfertigungHS")
        if self.thesis.grade:
            grade = ('%.1f' % self.thesis.grade).replace('.', ',')
            xfdf.add_field("Note", grade)
        if self.thesis.external_where:
            xfdf.add_field("Firma", self.thesis.external_where)

        if self.thesis.is_prolonged():
            xfdf.check("AbgabeMitVerlängerung")

            xfdf.add_field("BegründungVerlängerung",
                           self.thesis.prolongation_reason)
            xfdf.add_field("VerlängerungUmWochen",
                           self.thesis.prolongation_weeks)
            xfdf.add_field("DatumAbgabeNeu", self.__date_format(
                self.thesis.prolongation_date))
        else:
            xfdf.uncheck("AbgabeMitVerlängerung")

        if self.thesis.is_late():
            xfdf.check("AbgabeVerspätet")
            xfdf.uncheck("AbgabeTermingerecht")
        else:
            xfdf.uncheck("AbgabeVerspätet")
            xfdf.check("AbgabeTermingerecht")

        if self.thesis.handed_in_date:
            xfdf.add_field("DatumAbgabe",
                           self.__date_format(self.thesis.handed_in_date))

        if self.thesis.examination_date:
            xfdf.add_field("DatumKolloquium",
                           self.__date_format(self.thesis.examination_date))

        if self.thesis.restriction_note:
            xfdf.check("Sperrvermerk")
        else:
            xfdf.uncheck("Sperrvermerk")

        return xfdf

    def __date_format(self, date):
        return date.strftime("%d.%m.%Y")

    def __write_xfdf_to_tmp(self, xfdf):
        fd, xfdf_path = tempfile.mkstemp(suffix=".xfdf",
                                         dir=self.TMP_DIR,
                                         prefix="gen_")

        os.write(fd, xfdf.generate().encode())
        os.close(fd)

        return xfdf_path

    def __run_pdftk(self, xfdf_path):
        """Run pdftk to merge the generated XFDF with all PDF files."""
        pdf_path = xfdf_path.replace(".xfdf", ".pdf")

        # run pdftk to fill form fields
        subprocess.run(["pdftk", self.input_pdf_path,
                        "fill_form", xfdf_path,
                        "output", pdf_path, "flatten"])

        return self.__generate_pdf_info(pdf_path)

    def __generate_pdf_info(self, path):
        today = datetime.now().strftime("%Y%m%d")
        student_id = self.thesis.student.id

        filename = "{0}_{1}_{2}.pdf".format(
            today, self.form_name, student_id)

        return PDFInfo(path, filename)


class ApplicationPDF(AbstractPDF):
    """PDF for application of thesis"""

    def __init__(self, thesis):
        super(ApplicationPDF, self).__init__(thesis, 'ausgabe')


class GradingPDF(AbstractPDF):
    """PDF for grading of thesis"""

    def __init__(self, thesis):
        super(GradingPDF, self).__init__(thesis, 'bewertung')


class ProlongationPDF(AbstractPDF):
    """PDF for prolongation of thesis"""

    def __init__(self, thesis):
        super(ProlongationPDF, self).__init__(thesis, 'verlaengerung')
