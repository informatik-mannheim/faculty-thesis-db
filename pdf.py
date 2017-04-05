#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess


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


class FDF(object):
    """Generate FDF (File Data Format) files to populate PDF forms with data.

    Form data on PDF files can be populated by using one of these formats:
    - FDF (File Data Format)
    - XFDF (XML Forms Data Format)

    FDF is kind of dated, has an awkward syntax and features only
    limited support for special characters. If possible, use XFDF.

    The generated FDF file can be applied to an existig PDF file
    with severaldifferent tools, e.g. pdftk.
    """

    def __init__(self, checkbox_yes):
        """Initialize with a positive value for checkboxes(as it may vary)"""
        self.fields = {}
        self._checkbox_yes = checkbox_yes

    def _footer(self):
        footer = "] >> >>\n" \
            "endobj\n" \
            "trailer\n" \
            "<</Root 1 0 R>>\n" \
            "%%EOF"

        return footer

    def _header(self):
        header = "%FDF-1.2 \n" \
            "1 0 obj<</FDF<< /Fields[\n"
        return header

    def _fields(self):
        field_str = "<< /T({0}) /V({1}) >>"
        fields = [field_str.format(t, v) for t, v in self.fields.items()]
        return "\n".join(fields)

    def add_field(self, name, value):
        """Add a value for a named field"""
        self.fields[name] = value

    def check(self, field):
        """Check a form checkbox"""
        self.fields[field] = self._checkbox_yes

    def uncheck(self, field):
        """Uncheck a form checkbox"""
        self.fields[field] = "Off"

    def generate(self):
        """Generate FDF text from field definitions"""
        return self._header() + self._fields() + self._footer()


fdf = XFDF("Ja")
fdf.add_field("Vorname", "Jürgen")
fdf.add_field("Name", "Schneider")
fdf.add_field("BeginnDerArbeit", "01.01.2019")
fdf.add_field("AbgabeDerArbeit", "01.04.2019")
fdf.add_field("MatrNr", "123456")
fdf.add_field("EMail", "123456@stud.hs-mannheim.de")
fdf.add_field("KürzelErstkorrektor", "  SMI")

fdf.add_field("KürzelZweitkorrektor", "  IME")
fdf.add_field("Firma", "Krauss-Maffei Wegmann")

fdf.add_field("Nachfrist", "On") # this should be "Ja"
fdf.add_field("Titel", "\nEinsatz eines Flux-Kompensators für Zeitreisen mit einer maximalen Höchstgeschwindigkeit von WARP 7")
fdf.uncheck("IB")
fdf.check("StudienzeitNein")

fdf.check("IMB")
fdf.check("AnfertigungFirma")
fdf.uncheck("UIB")

with open("/tmp/gen.xfdf", "w+") as file:
    file.write(fdf.generate())

subprocess.run(["pdftk", "website/pdf/formulare.pdf",
                "fill_form", "/tmp/gen.xfdf", "output", "/tmp/pdf.pdf", "flatten"])
subprocess.run(["pdftk", "/tmp/pdf.pdf", "cat",
                "1", "output", "/tmp/pdf1.pdf"])
