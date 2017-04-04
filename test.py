class FDFGenerator(object):

    def __init__(self):
        self.fields = {}

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

    def add_field(self, key, value):
        self.fields[key] = value

    def check(self, field):
        self.fields[field] = "Ja"

    def uncheck(self, field):
        self.fields[field] = "Off"

    def generate(self):
        return self._header() + self._fields() + self._footer()


fdf = FDFGenerator()
fdf.add_field("Vorname", "Horst")
fdf.add_field("Name", "Schneider")
fdf.uncheck("IB")
fdf.uncheck("IMB")
fdf.uncheck("UIB")

with open("/tmp/gen.fdf", "w+") as file:
    file.write(fdf.generate())
