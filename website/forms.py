from datetime import timedelta

from django import forms
from django.forms import ModelForm
from django.utils import timezone

from website.models import *


class ThesisForm(ModelForm):

    class Meta:
        model = Thesis
        fields = ['title', 'student', 'supervisor', 'assessor']


class AssessorForm(ModelForm):

    class Meta:
        model = Assessor
        fields = ['first_name', 'last_name', 'email']


class ThesisApplicationForm(forms.Form):
    studiengang_choices = (('IB', 'IB'), ('MIB', 'MIB'), ('UIB', 'UIB'))

    title = forms.CharField(label="Titel", max_length=100)
    student_id = forms.CharField(label="Matrikelnummer")

    studiengang = forms.ChoiceField(
        label="Studiengang",
        required=True,
        widget=forms.RadioSelect,
        choices=studiengang_choices)

    begin_date = forms.DateField(
        widget=forms.SelectDateWidget,
        label="Beginn",
        initial=timezone.now())

    due_date = forms.DateField(
        widget=forms.SelectDateWidget,
        label="Abgabe",
        initial=timezone.now() + timedelta(90))

    def clean(self):
        super(ThesisApplicationForm, self).clean()
        if self.cleaned_data['student_id'] != '123456':
            raise forms.ValidationError({'student_id': 'gibt es nicht'})
