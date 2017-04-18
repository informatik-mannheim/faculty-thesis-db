from django.contrib.auth.decorators import login_required
from django.views import View
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from sendfile import sendfile

from website.forms import *
from website.models import *
from website.util import dateutil

from thesispool.pdf import *


def index(request):
    return redirect(reverse('overview'))


@login_required
def delete_thesis(request, pk):
    Thesis.objects.get(pk=pk).delete()

    return HttpResponseRedirect('/overview/')


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
        thesis = Thesis.objects.get(pdf_key=kwargs["pdfkey"])
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

        context = {'form': form, 'student': self.student}

        return render(request, 'website/create_step_two.html', context)

    def post(self, request, *args, **kwargs):
        form = ThesisApplicationForm(request.POST)

        if form.is_valid():
            supervisor = Supervisor(first_name=request.user.first_name,
                                    last_name=request.user.last_name,
                                    id=request.user.username)

            form.create_thesis(supervisor, self.student)

            return HttpResponseRedirect('/overview/')

        context = {'form': form, 'student': self.student}

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
