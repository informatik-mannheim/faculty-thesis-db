from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import never_cache

from website.models import Thesis, User
from approvals.forms import RejectForm


def is_excom_member(user):
    return isinstance(user, User) and user.is_excom


@user_passes_test(is_excom_member, login_url='/accounts/login/')
@never_cache
def index(request):
    open_theses = Thesis.objects.exclude(excom_status=Thesis.EXCOM_APPROVED)

    context = {'theses': open_theses}

    return render(request, 'approvals/index.html', context)


@user_passes_test(is_excom_member, login_url='/accounts/login/')
@never_cache
def approve(request, key):
    thesis = get_object_or_404(Thesis, surrogate_key=key)

    thesis.approve(request.user)

    return redirect(reverse('index'))


@user_passes_test(is_excom_member, login_url='/accounts/login/')
@never_cache
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
