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
    title = forms.CharField(label="Titel", max_length=300)
    student_id = forms.IntegerField(label="Matrikelnummer")

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

        matnr = int(self.cleaned_data['student_id'])

        errors = []

        if not Student.objects.find(matnr):
            errors.append(forms.ValidationError(
                {'student_id': 'Matrikelnummer existiert nicht'}))

        if self.cleaned_data['begin_date'] >= self.cleaned_data['due_date']:
            errors.append(forms.ValidationError(
                {'due_date': 'Abgabe muss später als der Beginn sein'}))

        if errors:
            raise forms.ValidationError(errors)

        self.cleaned_data['student'] = Student.objects.find(matnr)
