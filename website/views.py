from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse


def index(request):
    return redirect(reverse('overview'))


@login_required
def overview(request):
    return render(request, 'website/overview.html')
