from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from website.models import Thesis


@login_required(login_url='/accounts/login/')
def index(request):
    #if not request.user.is_secretary:
        #return HttpResponse("geht net")
    context = {'theses': Thesis.objects.all()}
    return render(request, 'approvals/index.html', context)
