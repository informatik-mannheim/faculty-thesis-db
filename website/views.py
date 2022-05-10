from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views import View
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404

from django_sendfile import sendfile

from website.forms import *
from website.models import *
from thesispool.pdf import *
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

User = get_user_model()

class ThesispoolLoginView(LoginView):
    models = User
    template_name = 'website/login.html'
    next_page = reverse_lazy('overview')


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
    if request.user.is_secretary:
        theses = Thesis.objects.all()
    else:
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


class CreateThesis(View):

    def dispatch(self, request, *args, **kwargs):
        self.student = Student.objects.find(kwargs["student_id"])

        if request.user.is_secretary:
            self.supervisor = None
        else:
            self.supervisor = Supervisor.from_user(request.user)

        return super(CreateThesis, self).dispatch(request, *args, **kwargs)

    @property
    def headline(self):
        prefix = ("Master", "Bachelor")[self.student.is_bachelor()]
        return "%sthesis anlegen" % prefix

    def get(self, request, *args, **kwargs):
        form = ThesisApplicationForm.initialize_from(self.student)
        s_form = SupervisorsForm() if not self.supervisor else None
        a_form = AssessorForm()

        context = {
            'form': form,
            's_form': s_form,
            'a_form': a_form,
            'student': self.student,
            'headline': self.headline,
            'supervisor': self.supervisor}

        return render(request, 'website/create_or_change.html', context)

    def post(self, request, *args, **kwargs):
        form = ThesisApplicationForm(request.POST)
        a_form = AssessorForm(request.POST)

        if not self.supervisor:
            s_form = SupervisorsForm(request.POST)

            if s_form.is_valid():
                s_id = s_form.cleaned_data['supervisors']
                self.supervisor = Supervisor.objects.fetch_supervisor(s_id)
        else:
            s_form = None

        if form.is_valid() and a_form.is_valid() and ((not s_form) or s_form.is_valid()):
            assessor = a_form.cleaned_data["assessor"]

            form.create_thesis(assessor, self.supervisor, self.student)

            return HttpResponseRedirect('/overview/')

        context = {
            'form': form,
            'a_form': a_form,
            'student': self.student,
            'headline': self.headline,
            'supervisor': self.supervisor,
            's_form': s_form}

        return render(request, 'website/create_or_change.html', context)


class ChangeView(View):

    def dispatch(self, request, *args, **kwargs):
        self.thesis = get_object_or_404(Thesis, surrogate_key=kwargs["key"])
        self.headline = "{0}thesis ändern".format(
            "Master" if self.thesis.student.is_master() else "Bachelor")
        return super(ChangeView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        student = self.thesis.student
        assessor = self.thesis.assessor

        form = ThesisApplicationForm(initial={
            'student_id': student.id,
            'begin_date': self.thesis.begin_date,
            'due_date': self.thesis.due_date,
            'title': self.thesis.title,
            'external': self.thesis.external,
            'external_where': self.thesis.external_where,
            'student_email': self.thesis.student_contact})

        if assessor:
            a_form = AssessorForm(initial={
                'first_name': assessor.first_name,
                'last_name': assessor.last_name,
                'email': assessor.email
            })
        else:
            a_form = AssessorForm()

        context = {
            'form': form,
            'a_form': a_form,
            'student': self.thesis.student,
            'headline': self.headline,
            'supervisor': self.thesis.supervisor
        }

        return render(request, 'website/create_or_change.html', context)

    def post(self, request, *args, **kwargs):
        form = ThesisApplicationForm(request.POST)
        a_form = AssessorForm(request.POST)

        if form.is_valid() and a_form.is_valid():
            assessor = a_form.cleaned_data["assessor"]

            form.change_thesis(self.thesis, assessor)

            return HttpResponseRedirect('/overview/')

        context = {
            'form': form,
            'a_form': a_form,
            'student': self.thesis.student,
            'headline': self.headline}

        return render(request, 'website/create_or_change.html', context)


@login_required
def find_student(request):
    student, form = None, None

    if request.method == 'POST':
        form = CheckStudentIdForm(request.POST)

        if form.is_valid():
            student = form.cleaned_data['student']

    context = {'form': form or CheckStudentIdForm(), 'student': student}

    return render(request, 'website/find_student.html', context)
