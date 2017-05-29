from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required

from website.models import Thesis


@login_required(login_url='/accounts/login/')
def index(request):
    if not request.user.is_excom:
        return redirect(reverse("overview"))

    context = {'theses': Thesis.objects.all()}
    return render(request, 'approvals/index.html', context)


@login_required(login_url='/accounts/login/')
def approve(request, key):
    return redirect(reverse('index'))


@login_required(login_url='/accounts/login/')
def reject(request, key):
    return redirect(reverse('index'))
