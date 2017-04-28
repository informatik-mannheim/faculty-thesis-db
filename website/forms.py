from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError

from website.models import *

from datetime import timedelta


class ThesisForm(ModelForm):

    class Meta:
        model = Thesis
        fields = ['title', 'student', 'supervisor', 'assessor']


class HandInForm(forms.Form):
    handed_in_date = forms.DateField(label="Abgabedatum",
                                     required=True,
                                     widget=forms.SelectDateWidget)

    restriction_note = forms.BooleanField(label="Sperrvermerk",
                                          required=False)

    new_title = forms.CharField(label="Neuer Titel",
                                max_length=300,
                                required=True,
                                widget=forms.TextInput(
                                    attrs={'max_length': '200',
                                           'class': 'title'})
                                )

    @classmethod
    def initialize_from(cls, thesis):
        # TODO: test new_title defaults
        initials = {'handed_in_date': thesis.deadline,
                    'new_title': thesis.title}

        return cls(initial=initials)


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

    restriction_note = forms.BooleanField(label="Sperrvermerk", required=False)

    examination_date = forms.DateField(
        widget=forms.SelectDateWidget,
        label="Kolloquiumsdatum")

    handed_in_date = forms.DateField(
        widget=forms.SelectDateWidget,
        label="Abgabedatum",
        required=True)

    def clean(self):
        super(GradeForm, self).clean()

        if 'grade' in self.cleaned_data:
            if 4 < self.cleaned_data["grade"] < 5.0:
                raise forms.ValidationError({'grade': 'Ungültige Note'})

    @classmethod
    def initialize_from(cls, thesis):
        initials = {
            'restriction_note': thesis.restriction_note,
            'examination_date': thesis.handed_in_date or thesis.deadline,
            'handed_in_date': thesis.handed_in_date or thesis.deadline,
        }

        return cls(initial=initials)

    def persist(self, thesis):
        grade = self.cleaned_data["grade"]
        examination_date = self.cleaned_data["examination_date"]
        restriction_note = self.cleaned_data["restriction_note"]
        handed_in_date = self.cleaned_data["handed_in_date"]

        thesis.hand_in(handed_in_date, restriction_note)
        thesis.assign_grade(grade, examination_date, restriction_note)


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
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Vorname'}))

    last_name = forms.CharField(
        label="Nachname",
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nachname'}))
    email = forms.CharField(
        label="E-Mail",
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'E-Mail'}))

    def clean(self):
        super(AssessorForm, self).clean()
        if not any(self.cleaned_data.values()):
            self.cleaned_data['assessor'] = None

        else:
            try:
                assessor = Assessor(
                    first_name=self.cleaned_data['first_name'],
                    last_name=self.cleaned_data['last_name'],
                    email=self.cleaned_data['email'])

                assessor.full_clean()

                self.cleaned_data['assessor'] = assessor
            except ValidationError:
                raise forms.ValidationError('Zweitkorrektor unvollständig')


class ThesisApplicationForm(forms.Form):
    title = forms.CharField(label="Titel",
                            max_length=300,
                            widget=forms.TextInput(
                                attrs={'placeholder': 'Titel der Arbeit...',
                                       'autofocus': 'autofocus'}))

    begin_date = forms.DateField(
        widget=forms.SelectDateWidget,
        label="Beginn")

    due_date = forms.DateField(
        widget=forms.SelectDateWidget,
        label="Abgabe")

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
        label="bei", max_length=300, required=False)

    def clean(self):
        super(ThesisApplicationForm, self).clean()

        begin = self.cleaned_data.get('begin_date')
        end = self.cleaned_data.get('due_date')

        if begin is not None and end is not None and begin >= end:
            raise forms.ValidationError(
                {'due_date': 'Abgabe muss später als der Beginn sein'})

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
                        supervisor=supervisor,
                        external=self.cleaned_data['external'],
                        external_where=self.cleaned_data['external_where'],
                        student_contact=contact)

        thesis.save()

        return thesis

    def change_thesis(self, thesis, assessor):
        if assessor:
            assessor.save()
        thesis.title = self.cleaned_data['title']
        thesis.begin_date = self.cleaned_data['begin_date']
        thesis.due_date = self.cleaned_data['due_date']
        thesis.assessor = assessor
        thesis.external = self.cleaned_data['external']
        thesis.external_where = self.cleaned_data['external_where']
        thesis.student_contact = self.cleaned_data[
            "student_email"] or student.email
        thesis.full_clean()
        thesis.save()
        return thesis
