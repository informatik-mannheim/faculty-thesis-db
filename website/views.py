import operator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404

from django_sendfile import sendfile

from website.forms import *
from website.models import *
from thesispool.pdf import *
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

User = get_user_model()


def index(request):
    return redirect(reverse('overview'))


# Login-view
class ThesispoolLoginView(LoginView):
    models = User
    template_name = 'website/login.html'
    next_page = reverse_lazy('overview')


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


class Overview(ListView):
    model = Thesis
    template_name = "overview.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_secretary:
            theses = Thesis.objects.all()
        else:
            theses = Thesis.objects.for_supervisor(request.user.username)

        return render(request, 'website/overview.html', {"theses": theses})

    def post(self, request, *args, **kwargs):
        if request.user.is_secretary:
            theses = Thesis.objects.all()
        else:
            theses = Thesis.objects.for_supervisor(request.user.username)

        if request.POST["due_date"] != "":
            theses = theses.filter(due_date__gte=request.POST["due_date"])

        if request.POST["status"] != "":
            theses = theses.filter(status__contains=request.POST["status"])

        if request.POST["title"] != "":
            theses = theses.filter(title__contains=request.POST["title"])

        # search-parameter for assessors is either a name or their id
        if request.POST["student"] != "":
            if True in [char.isdigit() for char in request.POST["student"]]:
                # get all students whose id starts with request.POST["student"]
                students_with_id = Student.objects.filter(
                    id__iregex=r'^'+request.POST["student"]+'[0-9]*')
            else:
                # assumption: no spaces in surnames
                if " " in request.POST["student"]:
                    student_name, student_surname = request.POST["student"].rsplit(" ", 1)
                    students_with_name = Student.objects.filter(
                        first_name__contains=student_name)
                    students_with_surname = Student.objects.filter(
                        last_name__contains=student_surname)
                else:
                    students_with_name = Student.objects.filter(
                        first_name__contains=request.POST["student"])
                    students_with_surname = Student.objects.filter(
                        last_name__contains=request.POST["student"])
                students_with_id = [student.id for student in students_with_name | students_with_surname]
            theses = theses.filter(student__in=students_with_id)

        # search-parameter for assessors is a name
        if request.POST["assessor"] != "":
            if " " in request.POST["assessor"]:
                assessor_name, assessor_surname = request.POST["assessor"].rsplit(" ", 1)
                assessors_with_name = Assessor.objects.filter(
                    first_name__contains=assessor_name)
                assessors_with_surname = Assessor.objects.filter(
                    last_name__contains=assessor_surname)
            else:
                assessors_with_name = Assessor.objects.filter(
                    first_name__contains=request.POST["assessor"])
                assessors_with_surname = Assessor.objects.filter(
                    last_name__contains=request.POST["assessor"])
            theses = theses.filter(
                assessor__in=[assessor.id for assessor in assessors_with_name | assessors_with_surname])

        if request.POST["sort"] != "":
            # students are ordered by surname
            if request.POST["sort"] == "student":
                theses = sorted(theses, key=operator.attrgetter("student.last_name"))
            # assessors are ordered by surname, theses with no assessors are ordered at the back
            elif request.POST["sort"] == "assessor":
                theses_has_assessor = sorted(theses.exclude(assessor=None),
                                             key=operator.attrgetter("assessor.last_name"))
                theses = theses_has_assessor + list(theses.filter(assessor=None))
            else:
                theses = theses.order_by(request.POST["sort"])

            # request.POST always returns a String, type casting needed
            if str(theses) == request.POST["theses"]:
                theses = reversed(theses)

        context = {"theses": theses,
                   "due_date": request.POST["due_date"],
                   "status": request.POST["status"],
                   "student": request.POST["student"],
                   "title": request.POST["title"],
                   "assessor": request.POST["assessor"]}

        return render(request, 'website/overview.html', context)


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
            'theses': self.thesis,
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


class DeleteThesis(View):

    def dispatch(self, request, *args, **kwargs):
        self.thesis = get_object_or_404(Thesis, surrogate_key=kwargs["key"])
        self.headline = "{0}thesis löschen".format(
            "Master" if self.thesis.student.is_master() else "Bachelor")
        return super(DeleteThesis, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        if self.thesis.is_graded() or self.thesis.is_handed_in() or self.thesis.is_prolonged() or \
            self.thesis.is_approved() or self.thesis.is_rejected():
            return redirect('overview')

        context = {
            'headline': self.headline,
            'theses': self.thesis,
        }

        return render(request, 'website/delete_thesis.html', context)

    def post(self, request, *args, **kwargs):

        if self.thesis.is_graded() or self.thesis.is_handed_in() or self.thesis.is_prolonged() or \
            self.thesis.is_approved() or self.thesis.is_rejected():
            return redirect('overview')

        self.thesis.delete()

        return redirect('overview')


@login_required
def find_student(request):
    student, form = None, None

    if request.method == 'POST':
        form = CheckStudentIdForm(request.POST)

        if form.is_valid():
            student = form.cleaned_data['student']

    context = {'form': form or CheckStudentIdForm(), 'student': student}

    return render(request, 'website/find_student.html', context)
