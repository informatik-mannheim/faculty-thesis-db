#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import tempfile
import os
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


class BachelorForms(object):
    TMP_DIR = "/tmp/thesispool"
    BASE_PDF = "website/pdf/formulare.pdf"

    def __init__(self, thesis):
        self.thesis = thesis
        self.__generated_pdf = None

    def ausgabe(self):
        """Return PDFInfo for filled out pdf for Bachelorarbeit Ausgabe"""
        return self.__generate_pdf()[0]

    def bewertung(self):
        """Return PDFInfo for filled out pdf for Bachelorarbeit Bewertung"""
        return self.__generate_pdf()[1]

    def __generate_pdf(self):
        """Generate PDF file from Thesis instance.

        Creates an XFDF file with all fields populated from a Thesis
        instance and runs pdftk to merge it with the base PDF to fill
        all form fields. Result is written to tempdir.

        Returns the absolute path of the generated pdf without suffix.
        """
        if not self.__generated_pdf:
            self.__ensure_temp_dir_exists()

            xfdf = self.__generate_xfdf()
            xfdf_path = self.__write_xfdf_to_tmp(xfdf)

            self.__generated_pdf = self.__run_pdftk(xfdf_path)

        return self.__generated_pdf

    def __ensure_temp_dir_exists(self):
        os.makedirs(self.TMP_DIR, exist_ok=True)

    def __generate_xfdf(self):
        """Generate XFDF data used in PDF form data population"""
        xfdf = XFDF("Ja")

        xfdf.add_field("Vorname", self.thesis.student.first_name)
        xfdf.add_field("Name", self.thesis.student.last_name)
        xfdf.add_field("BeginnDerArbeit",
                       self.thesis.begin_date.strftime("%m.%d.%Y"))
        xfdf.add_field("AbgabeDerArbeit",
                       self.thesis.due_date.strftime("%m.%d.%Y"))
        xfdf.add_field("MatrNr", self.thesis.student.id)
        xfdf.add_field("Titel", self.thesis.title)
        xfdf.add_field("EMail", self.thesis.student.email)
        # clear checkboxes just to be sure
        xfdf.uncheck("UIB")
        xfdf.uncheck("IB")
        xfdf.uncheck("IMB")

        xfdf.check(self.thesis.student.program)

        return xfdf

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
        subprocess.run(["pdftk", self.BASE_PDF,
                        "fill_form", xfdf_path,
                        "output", pdf_path, "flatten"])

        # run pdftk again to burst the filled out pdf into separate pdfs
        subprocess.run(["pdftk", pdf_path, "burst",
                        "output", pdf_path + "_%02d"])

        return [
            self.__generate_pdf_info('ausgabe', pdf_path + "_01"),
            self.__generate_pdf_info('bewertung', pdf_path + "_02"),
            self.__generate_pdf_info('verlaengerung', pdf_path + "_03"),
            self.__generate_pdf_info('kolloquium_termin', pdf_path + "_04"),
            self.__generate_pdf_info('kolloquium', pdf_path + "_05"),
        ]

    def __generate_pdf_info(self, type, path):
        today = datetime.now().strftime("%Y%m%d")
        student_id = self.thesis.student.id

        filename = "{0}_{1}_ba_{2}.pdf".format(today, type, student_id)

        return PDFInfo(path, filename)
