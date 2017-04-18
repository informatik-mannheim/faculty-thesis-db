from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError

from website.models import *


class ThesisForm(ModelForm):

    class Meta:
        model = Thesis
        fields = ['title', 'student', 'supervisor', 'assessor']


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
