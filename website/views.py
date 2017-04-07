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
    theses = Thesis.objects.filter(supervisor__id=request.user.username)

    return render(request, 'website/overview.html', {"theses": theses})


@login_required
def create(request):
    if request.method == 'POST':
        form = ThesisApplicationForm(request.POST)
        a_form = AssessorForm(request.POST)

        if form.is_valid() and a_form.is_valid():
            assessor = a_form.save()
            student = form.cleaned_data['student']

            supervisor = Supervisor(first_name=request.user.first_name,
                                    last_name=request.user.last_name,
                                    id=request.user.username)

            student.save()
            supervisor.save()

            Thesis(title=form.cleaned_data['title'],
                   begin_date=form.cleaned_data['begin_date'],
                   due_date=form.cleaned_data['due_date'],
                   assessor=assessor,
                   student=student,
                   supervisor=supervisor).save()

            return HttpResponseRedirect('/overview/')

    else:
        form = ThesisApplicationForm()
        a_form = AssessorForm()

    context = {'form': form, 'a_form': a_form}
    return render(request, 'website/create_thesis.html', context)
