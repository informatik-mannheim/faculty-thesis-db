from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse

from website.models import Thesis


def index(request):
    return redirect(reverse('overview'))


@login_required
def overview(request):
    theses = Thesis.objects.filter(supervisor__id=request.user.username)

    return render(request, 'website/overview.html', {"theses": theses})


@login_required
def create(request):
    return render(request, 'website/create_thesis.html')
