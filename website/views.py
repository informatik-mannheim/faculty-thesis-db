from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse

from website.models import *
from website.forms import *


def index(request):
    return redirect(reverse('overview'))


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
            begin_date = form.cleaned_data['begin_date']
            due_date = form.cleaned_data['due_date']
            title = form.cleaned_data['title']

            student = Student(id=123456,
                              first_name="Larry",
                              last_name="Langzeitstudent")

            supervisor = Supervisor(first_name=request.user.first_name,
                                    last_name=request.user.last_name,
                                    id=request.user.username)

            assessor = a_form.save()

            student.save()
            assessor.save()
            supervisor.save()

            Thesis(title=title,
                   begin_date=begin_date,
                   due_date=due_date,
                   assessor=assessor,
                   student=student,
                   supervisor=supervisor).save()

            return HttpResponseRedirect('/overview/')

    else:
        form = ThesisApplicationForm()
        a_form = AssessorForm()

    context = {'form': form, 'a_form': a_form}
    return render(request, 'website/create_thesis.html', context)
