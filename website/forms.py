from django import forms
from django.forms import ModelForm
from django.utils import timezone

from datetime import timedelta

from website.models import *

from website.util import dateutil

# List of years for SelectDateWidget to allow years in the past
YEARS = [x for x in range(datetime.now().year - 2, datetime.now().year + 2)]


class ThesisForm(ModelForm):
    class Meta:
        model = Thesis
        fields = ['title', 'student', 'supervisor', 'assessor']


class ProlongationForm(forms.Form):
    reason_widget = forms.Textarea(attrs={'cols': 40, 'rows': 5})
    weeks_widget = forms.NumberInput(
        attrs={'maxlength': '2', 'autofocus': 'autofocus'})

    reason = forms.CharField(label="Begründung",
                             max_length=2000,
                             required=True,
                             strip=True,
                             widget=reason_widget)

    weeks = forms.IntegerField(label="Wochen",
                               required=True,
                               min_value=1,
                               max_value=99,
                               widget=weeks_widget)

    prolongation_date = forms.DateField(label="Neue Abgabe",
                                        widget=forms.SelectDateWidget,
                                        required=True)

    due_date = forms.DateField(label="Ursprüngliche Abgabe",
                               widget=forms.HiddenInput(),
                               required=True)

    @classmethod
    def initialize_from(cls, thesis):
        """Due date depends on whether a thesis was prolonged or not.
        Prolongation date is always due_date + 1 month"""
        initials = {
            'due_date': thesis.deadline,
            'prolongation_date': thesis.deadline + timedelta(30)
        }

        return cls(initial=initials)

    def clean(self):
        prolongation_date = self.cleaned_data["prolongation_date"]
        due_date = self.cleaned_data["due_date"]

        if prolongation_date <= due_date:
            raise ValidationError(
                {'prolongation_date': 'Verlängerung liegt vor der Abgabe'})


class GradeForm(forms.Form):
    grade = forms.DecimalField(label="Note",
                               decimal_places=1,
                               max_digits=2,
                               min_value=1.0,
                               max_value=5.0,
                               widget=forms.NumberInput(
                                   attrs={'autofocus': 'autofocus'}))

    assessor_grade = forms.DecimalField(label="Zweitkorrektor-Note",
                                        decimal_places=1,
                                        max_digits=2,
                                        required=False,
                                        min_value=1.0,
                                        max_value=5.0,
                                        widget=forms.NumberInput(
                                            attrs={'autofocus': 'autofocus'}))

    restriction_note = forms.BooleanField(label="Sperrvermerk", required=False)

    examination_date = forms.DateField(
        widget=forms.SelectDateWidget(years=YEARS),
        label="Kolloquiumsdatum")

    handed_in_date = forms.DateField(
        widget=forms.SelectDateWidget(years=YEARS),
        label="Abgabedatum",
        required=True)

    assessor = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    def clean(self):
        super(GradeForm, self).clean()

        if 'grade' in self.cleaned_data:
            if 4 < self.cleaned_data["grade"] < 5.0:
                raise forms.ValidationError({'grade': 'Ungültige Note'})

        if 'assessor' in self.cleaned_data and 'assessor_grade' in self.cleaned_data \
                and self.cleaned_data["assessor"] != '':
            if self.cleaned_data["assessor_grade"] is not None and 4 < self.cleaned_data["assessor_grade"] < 5.0:
                raise forms.ValidationError({'assessor_grade': 'Ungültige Note'})
            elif self.cleaned_data["assessor_grade"] is None:
                raise forms.ValidationError({'assessor_grade': 'Note benötigt'})

    @classmethod
    def initialize_from(cls, thesis):
        initials = {
            'restriction_note': thesis.restriction_note,
            'examination_date': thesis.handed_in_date or thesis.deadline,
            'handed_in_date': thesis.handed_in_date or thesis.deadline,
            'grade': thesis.grade or None,
            'assessor_grade': thesis.assessor_grade or None,
        }

        return cls(initial=initials)

    def persist(self, thesis):
        grade = self.cleaned_data["grade"]
        assessor_grade = self.cleaned_data["assessor_grade"]
        examination_date = self.cleaned_data["examination_date"]
        restriction_note = self.cleaned_data["restriction_note"]
        handed_in_date = self.cleaned_data["handed_in_date"]

        thesis.hand_in(handed_in_date, restriction_note)
        thesis.assign_grade(grade, assessor_grade, examination_date, restriction_note)


class CheckStudentIdForm(forms.Form):
    student_id = forms.IntegerField(label="Matrikelnummer",
                                    widget=forms.TextInput(attrs={
                                        'autofocus': 'autofocus'}))

    def clean(self):
        super(CheckStudentIdForm, self).clean()

        matnr = int(self.cleaned_data['student_id'])

        if not Student.objects.find(matnr):
            raise forms.ValidationError(
                {'student_id': 'Matrikelnummer existiert nicht'})

        self.cleaned_data['student'] = Student.objects.find(matnr)


class AssessorForm(forms.Form):
    first_name = forms.CharField(
        label="Vorname",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Vorname'}))

    last_name = forms.CharField(
        label="Nachname",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nachname'}))

    email = forms.CharField(
        label="E-Mail",
        max_length=80,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'E-Mail'}))

    a_title = forms.CharField(
        label="akad. Grad",
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'akad. Grad'}))

    def clean(self):
        super(AssessorForm, self).clean()
        if not any(self.cleaned_data.values()):
            self.cleaned_data['assessor'] = None

        else:
            try:
                assessor = Assessor(
                    first_name=self.cleaned_data['first_name'],
                    last_name=self.cleaned_data['last_name'],
                    email=self.cleaned_data['email'],
                    a_title=self.cleaned_data['a_title'])

                assessor.full_clean()

                self.cleaned_data['assessor'] = assessor
            except ValidationError:
                raise forms.ValidationError('Zweitkorrektor unvollständig')


class StudentForm(forms.Form):
    id = forms.IntegerField(
        label="Matrikelnummer")

    first_name = forms.CharField(
        label="Vorname",
        max_length=30)

    last_name = forms.CharField(
        label="Nachname",
        max_length=30)

    program = forms.CharField(
        label="Studiengang",
        min_length=2)

    def clean(self):
        super(StudentForm, self).clean()
        manager = StudentManager()

        for field in ["first_name", "last_name", "program"]:
            if field in self.cleaned_data and False in [char.isalpha() for char in self.cleaned_data[field]]:
                raise forms.ValidationError(field + ': Zeichen/Ziffern nicht erlaubt')

        if "id" in self.cleaned_data and manager.find(self.cleaned_data["id"]) is not None:
            raise forms.ValidationError('Matrikelnummer bereits vorhanden')

        if "program" not in self.cleaned_data or self.cleaned_data["program"][-1] not in ["B", "M"]:
            raise forms.ValidationError('Studiengang muss mit "B" (Bachelor) order "M" (Master) enden')

        if "program" not in self.cleaned_data or self.cleaned_data["program"] in ["IB", "IM", "IMB", "CSB", "UIB"]:
            raise forms.ValidationError('Studenten der Fakultät I sind bereits in der Datenbank vorhanden')

    def create_student(self):
        if not self.is_valid():
            return None

        student = Student(id=self.cleaned_data["id"],
                          first_name=self.cleaned_data["first_name"],
                          last_name=self.cleaned_data["last_name"],
                          program=self.cleaned_data["program"])

        student.save()

        return student


class ThesisApplicationForm(forms.Form):
    title = forms.CharField(label="Titel",
                            max_length=200,
                            widget=forms.TextInput(
                                attrs={'placeholder': 'Titel der Arbeit...',
                                       'autofocus': 'autofocus'}))

    begin_date = forms.DateField(
        widget=forms.SelectDateWidget(years=YEARS),
        label="Beginn")

    due_date = forms.DateField(
        widget=forms.SelectDateWidget(years=YEARS),
        label="Abgabe")

    prolongation_date = forms.DateField(
        label="Verlängerungsdatum",
        widget=forms.HiddenInput(),
        required=False)

    external = forms.BooleanField(
        label="extern",
        initial=False,
        required=False
    )

    student_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'E-Mail (optional)'}),
        required=False
    )

    external_where = forms.CharField(
        label="bei", max_length=200, required=False)

    def clean(self):
        super(ThesisApplicationForm, self).clean()

        begin = self.cleaned_data.get('begin_date')
        end = self.cleaned_data.get('due_date')
        prolong = self.cleaned_data.get('prolongation_date')

        if begin is not None and end is not None and begin >= end:
            raise forms.ValidationError(
                {'due_date': 'Abgabe muss später als der Beginn sein'})

        if prolong is not None and end is not None and prolong < end:
            raise forms.ValidationError(
                {'due_date': 'Verlängerung muss später als der Beginn sein'})

    def create_thesis(self, assessor, supervisor, student):
        if not self.is_valid():
            return None

        if assessor:
            assessor.save()

        supervisor.save()
        student.save()

        contact = self.cleaned_data["student_email"] or student.email

        thesis = Thesis(title=self.cleaned_data['title'],
                        begin_date=self.cleaned_data['begin_date'],
                        due_date=self.cleaned_data['due_date'],
                        assessor=assessor,
                        student=student,
                        thesis_program=student.program,
                        supervisor=supervisor,
                        external=self.cleaned_data['external'],
                        external_where=self.cleaned_data['external_where'],
                        student_contact=contact)

        thesis.save()

        return thesis

    def change_thesis(self, thesis, assessor):
        if not self.is_valid():
            return None

        if assessor:
            assessor.save()

        thesis.title = self.cleaned_data['title']
        thesis.begin_date = self.cleaned_data['begin_date']
        thesis.due_date = self.cleaned_data['due_date']
        thesis.assessor = assessor
        thesis.external = self.cleaned_data['external']
        thesis.external_where = self.cleaned_data['external_where']
        thesis.student_contact = self.cleaned_data[
                                     "student_email"] or thesis.student.email

        thesis.full_clean()
        thesis.save()

        return thesis

    @classmethod
    def initialize_from(cls, student):
        start, end = dateutil.get_thesis_period(timezone.now(), student)

        return cls(initial={'student_id': student.id,
                            'begin_date': start,
                            'due_date': end})


class SupervisorsForm(forms.Form):
    supervisors = forms.ChoiceField(
        required=True, choices=(), label="Professor")

    def __init__(self, *args, **kwargs):
        super(SupervisorsForm, self).__init__(*args, **kwargs)

        supervisors = Supervisor.objects.fetch_supervisors_from_ldap()
        supervisors = sorted(supervisors, key=lambda s: s.last_name.lower())
        supervisors = [(s.id, str(s)) for s in supervisors]

        self.fields['supervisors'] = forms.ChoiceField(choices=supervisors)
