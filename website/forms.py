from datetime import timedelta

from django import forms
from django.forms import ModelForm

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

    external_where = forms.CharField(
        label="bei", max_length=300, required=False)

    assessor_first_name = forms.CharField(
        label="Vorname",
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Vorname'}))

    assessor_last_name = forms.CharField(
        label="Nachname",
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nachname'}))
    assessor_email = forms.CharField(
        label="E-Mail",
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'E-Mail'}))

    def clean(self):
        super(ThesisApplicationForm, self).clean()

        begin = self.cleaned_data.get('begin_date')
        end = self.cleaned_data.get('due_date')

        if begin is not None and end is not None and begin >= end:
            raise forms.ValidationError(
                {'due_date': 'Abgabe muss später als der Beginn sein'})

        if not self.cleaned_data['assessor_email']:
            self.cleaned_data['assessor'] = None

        else:
            self.cleaned_data['assessor'] = Assessor(
                first_name=self.cleaned_data['assessor_first_name'],
                last_name=self.cleaned_data['assessor_last_name'],
                email=self.cleaned_data['assessor_email'])
