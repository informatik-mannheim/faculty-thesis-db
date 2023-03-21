import operator

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views import View
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy

from django_sendfile import sendfile

from website.forms import *
from website.models import *

from django.contrib.auth.views import LoginView

User = get_user_model()


def index(request):
    return redirect(reverse('overview'))


class ThesispoolLoginView(LoginView):
    models = User
    template_name = 'website/login.html'
    next_page = reverse_lazy('overview')


@login_required
@never_cache
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
@never_cache
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


class Overview(View):

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        if request.user.is_secretary or request.user.is_head:
            theses = Thesis.objects.all()
        else:
            theses = Thesis.objects.for_supervisor(request.user.username)

        if "due_date" in request.GET and request.GET["due_date"] != "":
            if "." in request.GET["due_date"]:
                month, year = request.GET["due_date"].split(".")
                bound_lower = year + "-" + month + "-" + "01"
                bound_upper = year + "-" + str(int(month) + 1) + "-" + "01"
            else:
                year = request.GET["due_date"]
                bound_lower = year + "-" + "01" + "-" + "01"
                bound_upper = str(int(year) + 1) + "-" + "01" + "-" + "01"
            theses = theses.filter(due_date__gte=bound_lower, due_date__lt=bound_upper)

        if "status" in request.GET and request.GET["status"] != "":
            theses = theses.filter(status=request.GET["status"])

        if "title" in request.GET and request.GET["title"] != "":
            theses = theses.filter(title__contains=request.GET["title"])

        # parameters: id, first_name and/or last_name
        if "student" in request.GET and request.GET["student"] != "":
            if True in [char.isdigit() for char in request.GET["student"]]:
                students_with_id = Student.objects.filter(id__startswith=request.GET["student"])
            else:
                # following code based on assumption: no spaces in surnames
                if " " in request.GET["student"]:
                    students_name, students_surname = request.GET["student"].rsplit(" ", 1)
                    students_with_name = Student.objects.filter(
                        first_name__startswith=students_name)
                    students_with_surname = Student.objects.filter(
                        last_name__startswith=students_name)
                else:
                    students_with_name = Student.objects.filter(
                        first_name__startswith=request.GET["student"])
                    students_with_surname = Student.objects.filter(
                        last_name__startswith=request.GET["student"])
                students_with_id = [students.id for students in students_with_name or students_with_surname]

            theses = theses.filter(student__in=students_with_id)

        # parameters: first_name and/or last_name
        if "assessor" in request.GET and request.GET["assessor"] != "":
            if " " in request.GET["assessor"]:
                assessor_name, assessor_surname = request.GET["assessor"].rsplit(" ", 1)
                assessors_with_name = Assessor.objects.filter(
                    first_name__startswith=assessor_name)
                assessors_with_surname = Assessor.objects.filter(
                    last_name__startswith=assessor_surname)
            else:
                assessors_with_name = Assessor.objects.filter(
                    first_name__startswith=request.GET["assessor"])
                assessors_with_surname = Assessor.objects.filter(
                    last_name__startswith=request.GET["assessor"])
            theses = theses.filter(
                assessor__in=[assessor.id for assessor in assessors_with_name or assessors_with_surname])

        if "sort_by" in request.GET and request.GET["sort_by"] != "":
            sort_by = request.GET["sort_by"]
            to_reverse = False
            if "r_" in sort_by:
                sort_by = sort_by.split("r_")[1]
                to_reverse = True
            # students are ordered by surname
            if sort_by == "student":
                theses = sorted(theses, key=operator.attrgetter("student.last_name"))
            # assessors are ordered by surname, theses with no assessors are ordered at the back
            elif sort_by == "assessor":
                theses_has_assessor = sorted(theses.exclude(assessor=None),
                                             key=operator.attrgetter("assessor.last_name"))
                theses = theses_has_assessor + list(theses.filter(assessor=None))
            else:
                theses = theses.order_by(sort_by)

            if to_reverse:
                theses = theses[::-1]

        context = {"theses": theses,
                   "sort_by": request.GET["sort_by"] if "sort_by" in request.GET else "",
                   "due_date": request.GET["due_date"] if "due_date" in request.GET else "",
                   "status": request.GET["status"] if "status" in request.GET else "",
                   "title": request.GET["title"] if "title" in request.GET else "",
                   "student": request.GET["student"] if "student" in request.GET else "",
                   "assessor": request.GET["assessor"] if "assessor" in request.GET else "", }

        return render(request, 'website/overview.html', context)


class PdfView(View):
    type = None

    def send(self, request, pdf):
        """Call xsendfile wrapper to send PDF (in attachment mode)"""
        return sendfile(request,
                        pdf.path,
                        attachment=True,
                        attachment_filename=pdf.filename)

    @method_decorator(never_cache)
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

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        s_form = SupervisorsForm() if not self.supervisor else None
        a_form = AssessorForm()

        form = ThesisApplicationForm.initialize_from(self.student)

        context = {
            'form': form,
            's_form': s_form,
            'a_form': a_form,
            'student': self.student,
            'headline': self.headline,
            'supervisor': self.supervisor}

        return render(request, 'website/create_or_change.html', context)

    @method_decorator(never_cache)
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
            "Master" if self.thesis.is_master() else "Bachelor")
        return super(ChangeView, self).dispatch(request, *args, **kwargs)

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        student = self.thesis.student
        assessor = self.thesis.assessor

        if self.thesis.is_prolonged():
            form = ThesisApplicationForm(initial={
                'student_id': student.id,
                'begin_date': self.thesis.begin_date,
                'due_date': self.thesis.due_date,
                'prolongation_date': self.thesis.prolongation_date,
                'title': self.thesis.title,
                'external': self.thesis.external,
                'external_where': self.thesis.external_where,
                'student_email': self.thesis.student_contact})
        else:
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
                'email': assessor.email,
                'academic_title': assessor.academic_title
            })
        else:
            a_form = AssessorForm()

        context = {
            'thesis': self.thesis,
            'form': form,
            'a_form': a_form,
            'student': self.thesis.student,
            'headline': self.headline,
            'supervisor': self.thesis.supervisor
        }

        return render(request, 'website/create_or_change.html', context)

    @method_decorator(never_cache)
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
            "Master" if self.thesis.is_master() else "Bachelor")
        return super(DeleteThesis, self).dispatch(request, *args, **kwargs)

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):

        if self.thesis.is_graded() or self.thesis.is_handed_in() or self.thesis.is_prolonged() or \
                self.thesis.is_approved() or self.thesis.is_rejected():
            return redirect('overview')

        context = {
            'headline': self.headline,
            'theses': self.thesis,
        }

        return render(request, 'website/delete_thesis.html', context)

    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):

        if self.thesis.is_graded() or self.thesis.is_handed_in() or self.thesis.is_prolonged() or \
                self.thesis.is_approved() or self.thesis.is_rejected():
            return redirect('overview')

        self.thesis.delete()

        return redirect('overview')


@login_required
@never_cache
def find_student(request):
    student, form = None, None

    if request.method == 'POST':
        if request.POST.getlist('student_id') not in ([''], []):
            form = CheckStudentIdForm(request.POST)

            if form.is_valid():
                student = form.cleaned_data['student']

        s_form = StudentForm(request.POST)

        if s_form.is_valid():
            s_form.create_student()

    s_form = StudentForm()

    context = {'form': form or CheckStudentIdForm(), 'student': student, 's_form': s_form}

    return render(request, 'website/find_student.html', context)
