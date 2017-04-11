from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from sendfile import sendfile

from website.models import *
from website.forms import *

from thesispool.pdf import BachelorForms


def index(request):
    return redirect(reverse('overview'))


@login_required
def download(request, pk):
    thesis = Thesis.objects.get(pk=pk)

    pdf = BachelorForms(thesis).ausgabe()

    return sendfile(request,
                    pdf.path,
                    attachment=True,
                    attachment_filename=pdf.filename)


@login_required
def delete_thesis(request, pk):
    Thesis.objects.get(pk=pk).delete()

    return HttpResponseRedirect('/overview/')


@login_required
def overview(request):
    theses = Thesis.objects.for_supervisor(request.user.username)

    return render(request, 'website/overview.html', {"theses": theses})


@login_required
def create_step_two(request, student_id):
    student = Student.objects.find(student_id)

    if request.method == 'POST':
        form = ThesisApplicationForm(request.POST)

        if form.is_valid():
            assessor = form.cleaned_data['assessor']

            supervisor = Supervisor(first_name=request.user.first_name,
                                    last_name=request.user.last_name,
                                    id=request.user.username)

            student.save()
            supervisor.save()

            if assessor:
                assessor.save()

            Thesis(title=form.cleaned_data['title'],
                   begin_date=form.cleaned_data['begin_date'],
                   due_date=form.cleaned_data['due_date'],
                   assessor=assessor,
                   student=student,
                   supervisor=supervisor).save()

            return HttpResponseRedirect('/overview/')

    else:
        form = ThesisApplicationForm(initial={'student_id': student_id})

    context = {'form': form, 'student': student}
    return render(request, 'website/create_step_two.html', context)


@login_required
def create_step_one(request):
    student = None

    if request.method == 'POST':
        form = CheckStudentIdForm(request.POST)

        if form.is_valid():
            student = form.cleaned_data['student']

    else:
        form = CheckStudentIdForm()

    context = {'form': form, 'student': student}

    return render(request, 'website/create_step_one.html', context)
