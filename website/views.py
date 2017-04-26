from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views import View
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils import timezone
from sendfile import sendfile

from website.forms import *
from website.models import *
from website.util import dateutil
from thesispool.pdf import *

User = get_user_model()


def index(request):
    return redirect(reverse('overview'))


@login_required
def prolong(request, key):
    thesis = get_object_or_404(Thesis, surrogate_key=key)

    if request.POST:
        form = ProlongationForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data["reason"]
            prolongation_date = form.cleaned_data["prolongation_date"]
            weeks = form.cleaned_data["weeks"]

            thesis.prolong(prolongation_date, reason, weeks)
            return HttpResponseRedirect(reverse('overview'))

    else:
        form = ProlongationForm.initialize_from(thesis)

    context = {'thesis': thesis, 'form': form}

    return render(request, 'website/prolong.html', context)


@login_required
def grade(request, key):
    thesis = get_object_or_404(Thesis, surrogate_key=key)

    if request.POST:
        form = GradeForm(request.POST)
        if form.is_valid():
            form.persist(thesis)

            return HttpResponseRedirect(reverse('overview'))
    else:
        form = GradeForm.initialize_from(thesis)

    context = {"thesis": thesis, 'form': form}

    return render(request, 'website/grade.html', context)


@login_required
def handin(request, key):
    thesis = get_object_or_404(Thesis, surrogate_key=key)

    if request.POST:
        form = HandInForm(request.POST)

        if form.is_valid():
            restriction_note = form.cleaned_data["restriction_note"]
            handed_in_date = form.cleaned_data["handed_in_date"]
            new_title = form.cleaned_data["new_title"]
            thesis.title = new_title
            thesis.hand_in(handed_in_date, restriction_note)

            return HttpResponseRedirect(reverse('overview'))
    else:
        form = HandInForm.initialize_from(thesis)

    context = {"thesis": thesis, 'form': form}

    return render(request, 'website/handin.html', context)


@login_required
def overview(request):
    theses = Thesis.objects.for_supervisor(request.user.username)

    return render(request, 'website/overview.html', {"theses": theses})


class PdfView(View):
    type = None

    def send(self, request, pdf):
        """Call xsendfile wrapper to send PDF (in attachment mode)"""
        return sendfile(request,
                        pdf.path,
                        attachment=True,
                        attachment_filename=pdf.filename)

    def get(self, request, *args, **kwargs):
        """Create PDF of requested type (passed by urls.py) for selected thesis
        and send it via xsendfile"""
        thesis = Thesis.objects.get(surrogate_key=kwargs["key"])
        pdf_type = kwargs["type"]

        return self.send(request, pdf_type(thesis).get())


class CreateStepTwo(View):

    def dispatch(self, request, *args, **kwargs):
        self.student = Student.objects.find(kwargs["student_id"])

        self.start, self.end = dateutil.get_thesis_period(
            timezone.now(), self.student)

        return super(CreateStepTwo, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = ThesisApplicationForm(initial={'student_id': self.student.id,
                                              'begin_date': self.start,
                                              'due_date': self.end})

        context = {
            'form': form,
            'a_form': AssessorForm(),
            'student': self.student
        }

        return render(request, 'website/create_step_two.html', context)

    def post(self, request, *args, **kwargs):
        form = ThesisApplicationForm(request.POST)
        a_form = AssessorForm(request.POST)

        if form.is_valid() and a_form.is_valid():
            supervisor = Supervisor.from_user(request.user)
            assessor = a_form.cleaned_data["assessor"]

            form.create_thesis(assessor, supervisor, self.student)

            return HttpResponseRedirect('/overview/')

        context = {'form': form, 'a_form': a_form, 'student': self.student}

        return render(request, 'website/create_step_two.html', context)


@login_required
def create_step_one(request):
    student, form = None, None

    if request.method == 'POST':
        form = CheckStudentIdForm(request.POST)

        if form.is_valid():
            student = form.cleaned_data['student']

    context = {'form': form or CheckStudentIdForm(), 'student': student}

    return render(request, 'website/create_step_one.html', context)
