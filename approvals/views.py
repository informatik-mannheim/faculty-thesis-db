from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required

from website.models import Thesis, ExcomChairman
from approvals.forms import RejectForm


@login_required(login_url='/accounts/login/')
def index(request):
    if not request.user.is_excom:
        return redirect(reverse("overview"))

    open_theses = Thesis.objects.exclude(excom_status=Thesis.EXCOM_APPROVED)

    context = {'theses': open_theses}

    print(ExcomChairman.objects.count())

    return render(request, 'approvals/index.html', context)


@login_required(login_url='/accounts/login/')
def approve(request, key):
    thesis = get_object_or_404(Thesis, surrogate_key=key)

    thesis.approve(request.user)

    return redirect(reverse('index'))


@login_required(login_url='/accounts/login/')
def reject(request, key):
    thesis = get_object_or_404(Thesis, surrogate_key=key)

    if request.POST:
        form = RejectForm(request.POST)
        if form.is_valid():
            thesis.reject(request.user, form.cleaned_data["reason"])

            return redirect(reverse('index'))

    else:
        form = RejectForm()

    context = {
        'thesis': thesis,
        'form': form,
    }

    return render(request, 'approvals/reject.html', context)
